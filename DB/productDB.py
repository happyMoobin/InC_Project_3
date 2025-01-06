from flask import *
import boto3

dynamodb = boto3.resource(
    'dynamodb',
    region_name='ap-northeast-3'
)

table = dynamodb.Table('products')

class ProductDao:
    def __init__(self):
        pass

    def get_all_products(self):
        # 모든 요소 조회
        response = table.scan()
        products = response['Items'] 
        return products
    
    def get_product(self, product_id):
        response =  table.get_item(
            Key={
                'product_id': product_id
            }
        )   
        product_detail = response.get('Item')
        return product_detail
    
    def insert_product(self, id, price,description, image):
        # DynamoDB에 사용자 데이터 삽입
        response = table.put_item(
            Item={
                'product_id': id, 
                'price': price,
                'description': description,
                'image_path': image
            }
        )

    def delete_product(self,product_id):
        response = table.delete_item(
            Key={
                'product_id': product_id  # 삭제할 항목의 기본 키
            }
        )

    def update_product(self, product_id, price, description, image):
        try:
            response = table.update_item(
                Key={
                    'product_id': product_id
                },
                UpdateExpression="SET image=:i, price=:p, description=:d",
                ExpressionAttributeValues={
                    ':i': str(image),  # image 값을 문자열로 처리
                    ':p': int(price),  # price를 정수로 변환
                    ':d': str(description)  # description 값을 문자열로 처리
                },
                ReturnValues="UPDATED_NEW"  # 업데이트된 항목 반환 (선택사항)
            )
            print("Update successful:", response)
            return response
        except Exception as e:
            print("Error updating product:", str(e))
            raise