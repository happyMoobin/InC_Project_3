USE mini1;

-- 사용자 정보 테이블 (로그인, 회원가입, 마이페이지 등)
CREATE TABLE users ( 
    user_id INT AUTO_INCREMENT PRIMARY KEY, -- 사용자 고유 ID (PK)
    user_name VARCHAR(50) UNIQUE NOT NULL, -- 사용자 이름
    id VARCHAR(100) UNIQUE NOT NULL, -- 로그인 id (이메일)
    password VARCHAR(255) NOT NULL, -- 로그인 비밀번호
    signup_date DATETIME DEFAULT CURRENT_TIMESTAMP, -- 가입 일자
    credit INT DEFAULT 0, -- 크레딧 보유량
    answer VARCHAR(45) NOT NULL
);

CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY, -- 상품 고유 ID (PK)
    product_name VARCHAR(100) NOT NULL, -- 상품명
    description TEXT, -- 상품 설명
    image_path VARCHAR(255), -- 상품(이미지) 경로
    price DECIMAL(10, 2) NOT NULL, -- 상품 가격
    user_id INT, -- 판매자 ID (FK)
				-- 구매자 ID 필요할까? xx
    status ENUM('available', 'sold', 'reserved') DEFAULT 'available',  -- 판매 상태
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE orders ( -- 주문 테이블
    order_id INT AUTO_INCREMENT PRIMARY KEY, -- 주문 고유 ID (PK)
    product_id INT, -- 구매된 상품 ID (FK)
    user_id INT, -- 구매자 ID (FK)
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP, -- 주문 일자
    order_price DECIMAL(10, 2), -- 구매한 가격 
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE posts ( -- 게시판 테이블 추가
    post_id INT AUTO_INCREMENT PRIMARY KEY, -- 게시글 고유 ID (PK)
    user_id INT, -- 작성자 ID (FK)
    title VARCHAR(200) NOT NULL, -- 게시글 제목
    content TEXT NOT NULL, -- 게시글 내용
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- 작성 시간
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP, -- 수정 시간 (수정할 경우)
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE comments ( -- 댓글 테이블 추가
    comment_id INT AUTO_INCREMENT PRIMARY KEY, -- 댓글 고유 ID
    post_id INT, -- 게시글 ID (FK)
    user_id INT, -- 작성자 ID (FK)
    content TEXT NOT NULL, -- 댓글 내용
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- 작성 시간
    FOREIGN KEY (post_id) REFERENCES posts(post_id) ON DELETE CASCADE, -- 게시글 삭제 시 관련 댓글도 삭제
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE messages ( --문의 메시지 테이블
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    product_id INT NOT NULL,
    message_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    replied_content TEXT,
    replied_at TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(user_id),
    FOREIGN KEY (receiver_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 암호 찾기 질문
-- ALTER TABLE `mini1`.`users` 
-- ADD COLUMN `answer` VARCHAR(45) NOT NULL AFTER `credit`;


-- 이미지 생성 기록을 저장하고, 사용자가 나중에 접근할 수 있도록 관리하려면 이미지 생성 테이블 필요?
-- CREATE TABLE generated_images ( 
--     image_id INT AUTO_INCREMENT PRIMARY KEY, -- 생성한 이미지 고유 ID (PK)
--     user_id INT,  -- 이미지를 생성한 사용자 ID
--     image_path VARCHAR(255),  -- 생성된 이미지의 파일 경로
--     description VARCHAR(255),  -- 생성된 이미지에 대한 설명 (선택사항)
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- 생성된 시간
--     FOREIGN KEY (user_id) REFERENCES users(user_id)
-- );




