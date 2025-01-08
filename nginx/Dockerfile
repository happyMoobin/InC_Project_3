# Nginx 기본 이미지 사용
FROM nginx:alpine

# Nginx 설정 파일 복사
COPY nginx.conf /etc/nginx/nginx.conf

# EC2-1의 IP를 환경 변수로 설정
ENV EC2_1_PRIVATE_IP="127.0.0.1"

# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]

EXPOSE 80
