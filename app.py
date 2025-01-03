from flask import *
import board
import user
import product
import main

# import logging
# import logging.config

# 기능 별 분리 생각할것 -> 블루프린트 적용 완료
# 알케미(ORM)
# 검색기능 추가(X), 카테고리별 보기 및 검색 (카테고리 - 그림, 로고, 사진 ..)
# streamlit

app = Flask(__name__)
# logging.config.fileConfig('logging.conf')
# logger = logging.getLogger(__name__)

app.secret_key = 'bsdajvkbakjbfoehihewrpqkldn21pnifninelfbBBOIQRqnflsdnljneoBBOBi2rp1rp12r9uh'

# 블루프린트
app.register_blueprint(board.blueprint)
app.register_blueprint(user.blueprint)
app.register_blueprint(product.blueprint)
app.register_blueprint(main.blueprint)


# 상품 목록을 저장하기 위한 리스트
# products = []


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
