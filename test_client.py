from app import app  # Flask 앱 임포트
import random
import time
def test_checkout(cart_items):
    client = app.test_client()  # Flask 테스트 클라이언트 생성
    with client.session_transaction() as session:
        session['login_info'] = {'user_id': 'test_user'}  # 세션 데이터 설정

    response = client.post('/bucket/checkout', data={
        'cart_items': str(cart_items)
    })

    print("Response data:", response.data.decode())
    assert response.status_code == 302  # 리다이렉트 성공 여부 확인

items = [
        [
            {'product_name': '맥북', 'price': 12000, 'quantity': 1, 'image_path': 'https://imagebucketmini3.s3.ap-northeast-3.amazonaws.com/test2/s4.jpeg'}
        ],
        [
            {'product_name': '이지스함', 'price': 150000, 'quantity': 1, 'image_path': 'https://imagebucketmini3.s3.ap-northeast-3.amazonaws.com/test2/s4.jpeg'}
        ],
        [
            {'product_name': '신세계상품권', 'price': 100000, 'quantity': 1, 'image_path': 'https://imagebucketmini3.s3.ap-northeast-3.amazonaws.com/test2/s4.jpeg'}
        ],
        [
            {'product_name': '신발', 'price': 50000, 'quantity': 1, 'image_path': 'https://imagebucketmini3.s3.ap-northeast-3.amazonaws.com/test2/s4.jpeg'}
        ]
    ]

# 판매 데이터 샘플 전송
if __name__ == "__main__":

    while True:
        # 테스트 실행 3초 마다 랜덤으로 주문
        test_checkout(items[random.randint(0, 3)])
        time.sleep(3)