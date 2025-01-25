from flask import * 
from DB.userDB import *
from DB.productDB import *
from DB.ordersDB import *
from DB.data_stream import *
from datetime import datetime

blueprint = Blueprint('bucket', __name__, url_prefix='/bucket' ,template_folder='templates')

#장바구니
@blueprint.route('/bucket', methods=['GET', 'POST'])
def bucket():
    #모든 리스트 반환
    items = UserDao().get_cart_by_id(session['login_info'].get('user_id') )
    cart_items = []
    total_price = 0
    for item in items:
        element = {}
        product_name = item[0]
        product_quantity = item[1]
        product_detail=ProductDao().get_product(product_name)
       
        element['product_name'] = product_name
        element['price'] = int(product_detail['price'])
        element['quantity'] = int(product_quantity)
        element['image_path'] = product_detail['image_path']
        
        cart_items.append(element)
        total_price += element['price'] * element['quantity']

    return render_template('bucket.html',cart_items=cart_items, total_price=total_price)

#장바구니에 추가
@blueprint.route('/add_cart', methods=['GET','POST'])
def add_cart():
    
    # 사용자 인증 정보 확인
    if 'login_info' not in session:
        flash("로그인이 필요합니다.")
        return redirect(url_for('main.main'))
    
    user_id = session['login_info'].get('user_id')
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity'))
    
    if request.method == 'POST':
        UserDao().update_cart(user_id, product_id, quantity)
        return redirect(url_for('bucket.bucket')) 
    return render_template('bucket.html')

#장바구니
@blueprint.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    user_id = session['login_info'].get('user_id')
    product_id = request.form.get('product_id')

    if request.method == 'POST':
        UserDao().remove_from_cart(user_id, product_id)
        return redirect(url_for('bucket.bucket'))
    return render_template('bucket.html')


@blueprint.route('/checkout', methods=['POST'])
def checkout():
    try:
        # 요청 데이터 받기
        string_cart_items = request.form['cart_items']  # 장바구니 데이터
        
        string_data = string_cart_items.replace("'", "\"")  # 작은따옴표를 큰따옴표로 변경
        
        # 문자열을 리스트로 변환
        items = json.loads(string_data)
        user_id = session['login_info'].get('user_id')
        num_items = []
        total_price = 0

        for item in items:
            total_price += item['price']*item['quantity'] 
            num_items.append([item['product_name'],item['quantity']])
            
            # Kinesis data stream 처리를 위한 데이터 
            # salesdataDao().send_sales_data(item['product_name'], item['quantity'])
        
        # order table DynamoDB에 저장할 데이터 생성
        order_data = {
            'order_id': str(datetime.now().timestamp()),  # 고유 주문 ID
            'timestamp': str(datetime.now().strftime('%y-%m-%d')),  # 주문 시간
            'cart_items': num_items,  # 장바구니 상품 목록
            'num_item': int(item['quantity']), # 가격
            'total_price': total_price,
            'user_id': user_id
        }

        # DynamoDB에 데이터 삽입
        orderDao().put_order(order_data)

        UserDao().remove_all_from_cart(user_id)
        # 성공 메시지와 메인 페이지로 리다이렉트
        flash("결제가 완료되었습니다!")
        return redirect(url_for('main.main'))

    except Exception as e:
        print("Error during checkout:", e)
        flash("결제 중 오류가 발생했습니다.")
        return redirect(url_for('main.main'))