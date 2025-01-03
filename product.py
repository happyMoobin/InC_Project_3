from flask import *
from gpt_dalle_module import *
import os
from PIL import Image
from io import BytesIO
import base64
from projectDB import *
from werkzeug.utils import secure_filename
from logging_conf import *

blueprint = Blueprint('product', __name__, url_prefix='/product' ,template_folder='templates')

# 상품 등록 페이지
@blueprint.route('/addProduct', methods=['GET', 'POST'])
def addProduct():
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_description = request.form['product_description']
        product_price = request.form['product_price']
        
        # 이미지 파일 처리
        product_image = request.files['product_image']
        if product_image:
            image_filename = product_image.filename
            image_path = os.path.join('static/generated_image', image_filename)
            product_image.save(image_path)  # 이미지 저장

            # DB에 상품 추가
            productDAO().add_product(product_name, product_description, image_path, product_price, session['user_id'])
            # flash('상품이 등록되었습니다.')
            product_logger.info(f'{product_name} 상품 등록')
            return redirect(url_for('main.main'))  # 등록 후 페이지 리다이렉션
        
    return render_template('addProduct.html')
# 구매 페이지
@blueprint.route('/buyProduct/<int:product_id>')
def buyProduct(product_id):
    product = productDAO().get_product_by_id(product_id)
    if not product:
        flash("상품을 찾을 수 없습니다.")
        product_logger.error(f'{product_id} 존재하지 않는 상품')
        return redirect(url_for('main.main'))
    
    # 판매자의 정보를 가져옴
    user_dao = UserDao()
    seller = user_dao.get_user_by_id(product['user_id'])  # 상품의 user_id를 통해 판매자 정보 조회
    
    if not seller:
        flash("판매자를 찾을 수 없습니다.")
        product_logger.error(f'{product_id} 판매자 정보 없음')
        return redirect(url_for('main.main'))
    
    return render_template('buyProduct.html', product=product, seller=seller)


# 구매 기능
@blueprint.route('/buyProduct/<int:product_id>', methods=['POST'])
def confirmPurchase(product_id):
    user = UserDao().get_current_user()

    if not user:
        flash("로그인이 필요합니다.")
        product_logger.warning('로그인 필요')
        return jsonify({'redirect_url': url_for('user.login')}), 401  # JSON 응답으로 리디렉션 URL 반환

    # 구매 로직 처리
    result = productDAO().purchase_product(product_id, user['user_id'])

    if "구매가 완료되었습니다." in result:
        product = productDAO().get_product_by_id(product_id)
        if product:
            order_dao = orderDAO()
            order_dao.createOrder(
                product_id=product_id,
                user_id=user['user_id'],
                order_price=product['price']
            )
            product_logger.info(f'{product_id} 상품 구매 완료')

            # 다운로드 파일 경로 설정
            file_path = product['image_path']
            directory = os.path.dirname(file_path)
            filename = os.path.basename(file_path)

            # 다운로드 URL 반환
            download_url = url_for('product.download_file', directory=directory, filename=filename)
            return jsonify({
                'message': '구매가 완료되었습니다.',
                'download_url': download_url,
                'redirect_url': url_for('user.myPage')
            })
    else:
        return jsonify({'message': '크레딧이 부족합니다.', 'redirect_url': url_for('main.main')}), 400

@blueprint.route('/download/<path:directory>/<path:filename>')
def download_file(directory, filename):
    return send_from_directory(directory=directory, path=filename, as_attachment=True)

# @blueprint.route('/buyProduct/<int:product_id>', methods=['POST'])
# def confirmPurchase(product_id):
#     user = UserDao().get_current_user()  # 로그인한 사용자 정보 가져오기

#     if not user:
#         flash("로그인이 필요합니다.")
#         product_logger.warning('로그인 필요')
#         return redirect(url_for('user.login'))

#     # 구매 로직 처리
#     result = productDAO().purchase_product(product_id, user['user_id'])  # user_id를 전달하여 구매 처리
#     # flash(result)  # 결과 메시지 플래시에 표시
    
#     # 구매 성공 시 주문 정보를 기록
#     if "구매가 완료되었습니다." in result:  # 구매가 성공했을 경우
#         # 상품 정보를 가져와서 주문 생성
#         product = productDAO().get_product_by_id(product_id)  # 상품 정보 가져오기
#         if product:
#             order_dao = orderDAO()  # orderDAO 인스턴스 생성
#             order_dao.createOrder(product_id=product_id, user_id=user['user_id'], order_price=product['price'])  # 주문 기록
#             product_logger.info(f'{product_id} 상품 구매 완료')
#     else:
#         flash('크레딧이 부족합니다.')
#         product_logger.warning('크레딧 부족')
#         return redirect(url_for('main.main'))
    
#     flash('구매가 완료되었습니다.')
#     return redirect(url_for('user.myPage'))

# 생성 페이지
@blueprint.route('/createImage')
def createImage():
    return render_template('createImage.html')

# 이미지 생성 바로 저장되도록 해서 이미지 저장버튼 처리 필요없음

# 프롬프트를 통한 이미지 생성
@blueprint.route('/generateImageFromPrompt', methods=['GET', 'POST'])
def generateImageFromPrompt():
    # 프롬프트에 입력한 내용을 GPT를 통해 DALL-E 프롬프트로 만들고, 이를 DALL-E에게 주입시켜 이미지를 생성한 후 created 페이지로 리턴해야 함
    if request.method == 'POST':
        user_prompt = request.form.get('prompt')
        user_id = session.get('user_id')
        
        if not user_prompt:
            flash('프롬프트를 입력해주세요')
            product_logger.warning('프롬프트 입력 오류')
            return redirect(url_for('product.createImage'))
        
        # 크레딧 감소 시도
        if not productDAO().generate_image(user_id):
            flash('크레딧이 부족하여 이미지를 생성할 수 없습니다.')
            product_logger.warning('크레딧 부족')
            return redirect(url_for('product.createImage'))

        dalle_propt = generate_dalle_prompt(user_prompt)
        
        image_data = create_dalle_image(dalle_propt)
        image = Image.open(BytesIO(base64.b64decode(image_data)))
        
        # 이미지는 로컬에 저장됨. 
        filename = f'{user_id}_image_{user_prompt[:5]}.png'
        save_path = os.path.join(current_app.root_path, 'static', 'generated_image', filename)
        image.save(save_path)
        
        image_url = url_for('static', filename=f'generated_image/{filename}')
        product_logger.info(f'{filename} 이미지 생성 완료')
        return redirect(url_for('product.generatedImage', image_url=image_url))

    if request.method == 'GET':
        return render_template('createIamge.html')
    
    
# 카테고리를 이용한 이미지 생성
@blueprint.route('/generateImageFromCategory', methods=['GET', 'POST'])
def generateImageFromCategory():
    if request.method == 'POST':
        
        category = request.form.get('category')
        topic = request.form.get('topic')
        user_id = session.get('user_id')
        
        if not category or not topic:
            flash('프롬프트를 입력해주세요')
            product_logger.warning('프롬프트 입력 오류')
            return redirect(url_for('product.createImage'))
        
        # # 크레딧 감소 시도
        if not productDAO().generate_image(user_id):
            flash('크레딧이 부족하여 이미지를 생성할 수 없습니다.')
            product_logger.warning('크레딧 부족')
            return redirect(url_for('product.createImage'))
        
        prompt = generate_dalle_category(category, topic)
        
        image_data = create_dalle_image(prompt)
        image = Image.open(BytesIO(base64.b64decode(image_data)))
        
        filename = f'{user_id}_image_{topic}.png' # 파일 이름 수정완료
        save_path = os.path.join(current_app.root_path, 'static', 'generated_image', filename)
        image.save(save_path)
        
        image_url = url_for('static', filename=f'generated_image/{filename}')
        product_logger.info(f'{filename} 이미지 생성')
        return redirect(url_for('product.generatedImage', image_url=image_url))
    
    if request.method == 'GET':
        return render_template('createImage.html')
    

# 생성된 이미지 결과 화면. 이미지 생성 시 image에 저장되도록 했기 때문에 추가로 저장은 필요 없음
@blueprint.route('/createdImage')
def generatedImage():
    image_url = request.args.get('image_url')
    return render_template('createdImage.html', image_url=image_url)

@blueprint.route('/inquire/<int:product_id>', methods=['GET', 'POST'])
def inquire(product_id):
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            flash("로그인이 필요합니다.")
            product_logger.warning('로그인 필요')
            return redirect(url_for('user.login'))

        message_content = request.form['message_content']
        product = productDAO().get_product_by_id(product_id)

        if product:
            receiver_id = product['user_id']
            MessagesDao().send_message(sender_id=user_id, receiver_id=receiver_id, product_id=product_id, message_content=message_content)
            flash("판매자에게 문의 메시지가 전송되었습니다.")
            product_logger.info(f'userId : {user_id} receiver_Id : {receiver_id} product_Id : {product_id} 문의 전송')
            return redirect(url_for('user.inquiry_history'))
                        
            # return """
            # <script>
            #     alert("판매자에게 문의 메시지가 전송되었습니다.");
            #     window.location.href = "{}";
            # </script>
            # """.format(url_for('user.inquiry_history'))
        else:
            flash("상품을 찾을 수 없습니다.")
            product_logger.error('상품이 존재하지 않습니다.')
            return redirect(url_for('main.main'))
    
    return render_template('inquire.html', product_id=product_id)
