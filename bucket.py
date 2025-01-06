from flask import * 
from DB.userDB import *
from DB.productDB import *

blueprint = Blueprint('bucket', __name__, url_prefix='/bucket' ,template_folder='templates')

#장바구니
@blueprint.route('/bucket', methods=['GET', 'POST'])
def bucket():
    #모든 리스트 반환
    items = UserDao().get_cart_by_id(session['login_info'].get('UserID') )
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
    
    user_id = session['login_info'].get('UserID')
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity'))
    
    if request.method == 'POST':
        UserDao().update_cart(user_id, product_id, quantity)
        return redirect(url_for('bucket.bucket')) 
    return render_template('bucket.html')

#장바구니
@blueprint.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    user_id = session['login_info'].get('UserID')
    product_id = request.form.get('product_id')

    if request.method == 'POST':
        UserDao().remove_from_cart(user_id, product_id)
        return redirect(url_for('bucket.bucket'))
    return render_template('bucket.html')