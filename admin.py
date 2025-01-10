from flask import * 
from DB.userDB import *
from DB.productDB import *
from DB.s3 import *
from DB.data_stream import *

blueprint = Blueprint('admin', __name__, url_prefix='/admin' ,template_folder='templates')

# 사용자 관리
@blueprint.route('/manage_user')
def manage_user():
    users = UserDao().get_all_users()
    return render_template('manage_user.html',users=users)

# 상품 관리
@blueprint.route('/manage_product')
def manage_product():
    products = ProductDao().get_all_products()
    
    # 판매량 추가
    for product in products:
        product['sales_amount'] = int(salesdataDao().get_quantity_by_id(product['product_id']))
       
    return render_template('manage_product.html',products=products)

# 상품 관리
@blueprint.route('/add_product', methods=['GET', 'POST'])
def add_product():
    name = request.form['name']
    price = request.form['price']
    description = request.form['description']
    image = request.files['image'] 
    
    image_url = upload_file_to_s3(image, name)
    
    ProductDao().insert_product(name,price,description,image_url)
    salesdataDao().insert_data(name)

    products = ProductDao().get_all_products()

    return render_template('manage_product.html',products=products)

# 상품 관리
@blueprint.route('/update_product/<product_id>',methods=['POST'])
def update_product(product_id):
    product_id = request.form['name']
    price = request.form['price']
    description = request.form['description']
    image = request.files['image'] 
    
    ProductDao().update_product(product_id,price,description,image)
    products = ProductDao().get_all_products()
    return render_template('manage_product.html',products=products)

# 상품 관리
@blueprint.route('/delete_product/<product_id>',methods=['POST'])
def delete_product(product_id):
    ProductDao().delete_product(product_id)
    salesdataDao().delete_product(product_id)
    products = ProductDao().get_all_products()
    delete_object(product_id)
    return render_template('manage_product.html',products=products)

@blueprint.route('/manage_order')
def manage_order():
    return render_template('manage_order.html')