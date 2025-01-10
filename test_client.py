from app import app  # Flask 앱 임포트

def test_checkout():
    client = app.test_client()  # Flask 테스트 클라이언트 생성
    with client.session_transaction() as session:
        session['login_info'] = {'UserID': 'test_user'}  # 세션 데이터 설정
    
    cart_items = [
       {'product_name': 'test2', 'price': 2000, 'quantity': 1, 'image_path': 'https://imagebucketmini3.s3.ap-northeast-3.amazonaws.com/test2/s4.jpeg'}
    ]
    response = client.post('/bucket/checkout', data={
        'cart_items': str(cart_items)
    })

    print("Response data:", response.data.decode())
    assert response.status_code == 302  # 리다이렉트 성공 여부 확인

# 판매 데이터 샘플 전송
if __name__ == "__main__":
    for i in range(100):
        # 테스트 실행
        test_checkout()