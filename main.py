from flask import *
from projectDB import *
from logging_conf import *

blueprint = Blueprint('main', __name__, template_folder='templates')

# 초기 화면
@blueprint.route('/')
def index():
    return redirect(url_for('main.main'))

# 메인 화면
@blueprint.route('/main')
def main():
    # 전체 상품 리스트 가져오기
    products = productDAO().get_all_products()
    
    # 판매 중인 상품과 판매 완료된 상품으로 분리
    selling_products = [product for product in products if product['status'] != 'sold']
    sold_products = [product for product in products if product['status'] == 'sold']
    
    main_logger.info('mainpage 방문')
    # 템플릿에 각각 전달
    return render_template('home.html', selling_products=selling_products, sold_products=sold_products)