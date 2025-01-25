from flask import * 
from DB.userDB import *
from DB.ordersDB import *

blueprint = Blueprint('user', __name__, url_prefix='/user' ,template_folder='templates')

# 로그인 기능
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 사용자 정보 조회
        user = UserDao().get_user(username, password)
        
        if user:  # 사용자가 존재할 경우
            session['login_info'] = user  # 로그인 정보 세션에 저장
            flash('로그인 성공!')  # 로그인 성공 메시지
            
            return redirect(url_for('main.main'))  # => 리디렉션 처리
        else:
            flash('로그인 실패. 사용자 이름 또는 비밀번호를 확인하세요.')  # 오류 메시지
            return redirect(url_for('user.login'))  # 로그인 실패 시 로그인 페이지로 이동
        
    return render_template('login.html')

# 로그아웃
@blueprint.route('/logout')
def logout():
    if 'login_info' in session:
        session.pop('login_info', None)
        session.pop('user_id', None)
        flash('로그아웃 되었습니다.')  # 로그아웃 메시지
    return redirect(url_for('main.main'))

# 회원가입
@blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        id = request.form['user_id']
        password = request.form['UserPw']
        confirm_password = request.form['UserPwConfirm']
        user_name = request.form['UserName']
        answer = request.form['FindPwAnswer']

        if password != confirm_password:
            flash('비밀번호가 일치하지 않습니다.')
            return redirect(url_for('user.signup'))

        user_dao = UserDao()
        existing_user = user_dao.get_user_by_id(id)
        if existing_user:
            flash('이미 사용 중입니다. 다른 값을 넣어주세요.')
            return redirect(url_for('user.signup'))

        result = user_dao.insert_user(user_name, id, password, answer)
        
        if 'Insert OK' in result:
            flash('회원가입이 완료되었습니다.')
            return redirect(url_for('user.login'))
        else:
            flash('FATAL ERROR !')
            return redirect(url_for('user.main'))

    return render_template('signup.html')

@blueprint.route('/check_duplicate', methods=['POST'])
def check_duplicate():
    data = request.get_json()  # 클라이언트에서 보낸 JSON 데이터
    user_id = data.get("user_id")
    
    existing_user = UserDao().get_user_by_id(user_id)
    if existing_user:
        return jsonify({"status": "error", "message": "이미 등록된 아이디입니다."})
    else:
        return jsonify({"status": "success", "message": "사용 가능한 아이디입니다."})

@blueprint.route('/mypage', methods=['GET','POST'])    
def mypage():
    orders = orderDao().get_orders_by_id(session['login_info'].get('UserID'))
    index = 1 
    for order in orders:
        for product in order.get('cart_items'):
            product.append(index)
            index+=1
    return render_template('mypage.html', orders=orders, int=int,enumerate=enumerate)
