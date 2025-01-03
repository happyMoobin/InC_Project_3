from logging_conf import *
from flask import * 
from projectDB import *

blueprint = Blueprint('user', __name__, url_prefix='/user' ,template_folder='templates')
# logging.config.fileConfig('logging.conf')
# logger = logging.getLogger(__name__)

# 로그인 기능
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_logger.info(f'로그인 시도 : {username}')
        # 사용자 정보 조회
        user = UserDao().get_user(username, password)

        if user:  # 사용자가 존재할 경우
            session['login_info'] = user[1]  # 로그인 정보 세션에 저장
            session['user_id'] = user[0]  # 사용자 고유 ID 저장
            flash('로그인 성공!')  # 로그인 성공 메시지
            user_logger.info(f'로그인 성공 : {username}')
            return redirect(url_for('main.main'))  # => 리디렉션 처리
        else:
            flash('로그인 실패. 사용자 이름 또는 비밀번호를 확인하세요.')  # 오류 메시지
            user_logger.warning(f'로그인 실패 : {username}')
            return redirect(url_for('user.login'))  # 로그인 실패 시 로그인 페이지로 이동
        
    return render_template('login.html')

# 로그아웃
@blueprint.route('/logout')
def logout():
    if 'login_info' in session:
        session.pop('login_info', None)
        session.pop('user_id', None)
        flash('로그아웃 되었습니다.')  # 로그아웃 메시지
        user_logger.info('로그아웃 완료')
    return redirect(url_for('main.main'))

# 회원가입
@blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_name = request.form['UserName']
        id = request.form['UserId']
        password = request.form['UserPw']
        confirm_password = request.form['UserPwConfirm']
        answer = request.form['FindPwAnswer']

        if password != confirm_password:
            flash('비밀번호가 일치하지 않습니다.')
            user_logger.warning('비밀번호 에러')
            return redirect(url_for('user.signup'))

        user_dao = UserDao()
        existing_user = user_dao.get_user_by_id(id)
        if existing_user:
            flash('이미 사용 중입니다. 다른 값을 넣어주세요.')
            user_logger.warning(f'PW 중복 발생')
            return redirect(url_for('user.signup'))

        result = user_dao.insert_user(user_name, id, password, answer)
        
        if 'Insert OK' in result:
            flash('회원가입이 완료되었습니다.')
            user_logger.info(f'{user_name} 회원가입 완료')
            return redirect(url_for('user.login'))
        else:
            flash('FATAL ERROR !')
            user_logger.error('FATAL ERROR')
            return redirect(url_for('user.main'))

    return render_template('signup.html')

# id 중복 확인
@blueprint.route('/check_duplicate', methods=['POST'])
def check_duplicate():
    data = request.get_json()
    id = data.get('userId')
    
    user_dao = UserDao()
    existing_user = user_dao.get_id_by_id(id)
    is_duplicate = existing_user is not None
    
    return jsonify({'isDuplicate': is_duplicate})

# 비밀 번호 찾기
@blueprint.route('/find_pw', methods=['POST','GET'])
def find_pw():
    if request.method == 'POST':
        user_name = request.form['UserId']
        answer = request.form['answer']
        new_password = request.form['new_password']
        result = UserDao().change_pw(user_name, answer, new_password)
        print(result)
        if result == True:
            flash('비밀번호가 변경되었습니다.')
            user_logger.info(f'{user_name} 비밀번호 변경')
            return redirect(url_for('user.login'))  # 로그인 페이지로 리다이렉트
        else:
            flash('질문에 대한 답을 다시 입력해주세요.', 'error')
            user_logger.warning(f'{user_name} Diffrent Answer')
            return redirect(url_for('user.find_pw'))  # 비밀번호 찾기 페이지로 리다이렉트
    
    # GET 요청일 경우 비밀번호 찾기 페이지 렌더링
    return render_template('find_pw.html')
    

# # 회원가입 세부 기능
# @blueprint.route('/register')
# def register():
#     pass


# # 회원가입 세부 기능
# @blueprint.route('/register')
# def register():
#     pass


# 마이페이지(이름, ID, 구매 내역, 판매 내역 크레딧 조회 가능하도록)
@blueprint.route('/myPage')
def myPage():
    if 'login_info' in session:
        username = session['login_info']
        user_id = session['user_id']
        user = UserDao().get_user_by_id(user_id)
        if user:
            user_data = {
                'name': user['user_name'],
                'email': user['id'],
                'signup_date': user['signup_date'],
                'credit': user['credit']
            }
        return render_template('myPage.html', user_data=user_data)
    else:
        return redirect(url_for('user.login'))  # 세션이 없다면 로그인으로

# 구매 내역 페이지(실제 상품 연동 필요)
@blueprint.route('/buyList')
def buyList():
    user_id = session.get('user_id')  # 로그인된 유저 ID
    if not user_id:
        flash('로그인이 필요합니다.')
        user_logger.error('로그인 필요')
        return redirect(url_for('user.login'))
    
    # 유저가 판매한 상품의 리스트 가져오기
    orders = orderDAO().get_orders_by_user(user_id)
    
    return render_template('buyList.html', orders=orders)

# 판매 내역 페이지(실제 상품 연동 필요)
@blueprint.route('/sellList')
def sellList():
    user_id = session.get('user_id')
    if not user_id:
        flash("로그인이 필요합니다.")
        user_logger.error('로그인 필요')
        return redirect(url_for('user.login'))
    
    # 판매자가 등록한 상품의 판매 내역 가져오기
    sold_products = productDAO().get_sold_products(user_id)
    
    return render_template('sellList.html', sold_products=sold_products)

@blueprint.route('/addCredit', methods=['GET', 'POST'])
def addCredit():
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            flash("로그인이 필요합니다.")
            user_logger.error('로그인 필요')
            return redirect(url_for('user.login'))

        # 금액 받기
        amount = request.form.get('amount', type=int)  # amount를 그대로 가져옵니다.
        print('amount  >>>>>>>>>>', amount)

        if amount is not None and amount >= 1000:
            user_logger.info(f"User ID: {user_id}, Amount: {amount}")
            user_dao = UserDao()
            success = user_dao.add_credit(user_id, amount)  # 크레딧 추가 메서드 호출

            if success:
                flash(f"₩{amount:,}이 충전되었습니다.")  # 수정된 통화 포맷
                return redirect(url_for('main.main'))  # 홈 페이지로 리디렉션
            # else:
            #     flash("충전 중 오류가 발생했습니다.")
        else:
            flash("충전할 금액을 올바르게 입력해주세요.")
            user_logger.error(f'{user_id} 충전 오류')


        flash("크레딧 충전이 완료되었습니다.")
        user_logger.info(f'user_id : {user_id}, amount = {amount} 충전 완료')
        return redirect(url_for('user.myPage'))  # 충전 페이지로 리다이렉트

    return render_template('addCredit.html')

@blueprint.route('/inquiry_history')
def inquiry_history():
    user_id = session.get('user_id')
    if not user_id:
        flash("로그인이 필요합니다.")
        user_logger.error('로그인 필요')
        return redirect(url_for('user.login'))
    
    inquiries = MessagesDao().get_inquiries_by_user(user_id)
    return render_template('inquiry_history.html', inquiries=inquiries)

@blueprint.route('/inquiry_detail/<int:message_id>', methods=['GET', 'POST'])
def inquiry_detail(message_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("로그인이 필요합니다.")
        user_logger.error('로그인 필요')
        return redirect(url_for('user.login'))
    
    if request.method == 'POST':
        reply_content = request.form['reply_content']
        MessagesDao().send_reply(message_id, user_id, reply_content)
        flash("답장이 전송되었습니다.")
        user_logger.info(f'{user_id} {reply_content} 답장 전송 완료')
        return redirect(url_for('user.inquiry_history'))
                
        # return """
        # <script>
        #     alert("답장이 완료되었습니다.");
        #     window.location.href = "{}";
        # </script>
        # """.format(url_for('user.inquiry_history'))
    
    messages = MessagesDao().get_conversation(message_id, user_id)
    return render_template('inquiry_detail.html', messages=messages)

