CREATE TABLE users (
	id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(32) NOT NULL,
	login_id VARCHAR(32) NOT NULL,
	login_pw VARCHAR(200) NOT NULL,
	email VARCHAR(50),
	phone VARCHAR(50),
	UNIQUE(login_id)
);


CREATE TABLE admin (
	id INT PRIMARY KEY,
	FOREIGN KEY(id) REFERENCES users(id) ON DELETE CASCADE
);


CREATE TABLE subscribe (
	id INT NOT NULL,
	expired_at TIMESTAMP,
	FOREIGN KEY(id) REFERENCES users(id) ON DELETE CASCADE
);


CREATE TABLE subjects (
	id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(64) NOT NULL
);


CREATE TABLE quizzes (
	id INT AUTO_INCREMENT PRIMARY KEY,
	u_id INT NOT NULL,
	s_id INT NOT NULL,
	question VARCHAR(255) NOT NULL,
	answer VARCHAR(128) NOT NULL,
	opt1 VARCHAR(128) NOT NULL,
	opt2 VARCHAR(128),
	opt3 VARCHAR(128),
	comment VARCHAR(512),
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(u_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY(s_id) REFERENCES subjects(id) ON DELETE CASCADE
);


CREATE TABLE board (
	id INT AUTO_INCREMENT PRIMARY KEY,
	u_id INT NOT NULL,
	title VARCHAR(255) NOT NULL,
	content TEXT NOT NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(u_id) REFERENCES users(id) ON DELETE CASCADE
);


CREATE TABLE files (
	id INT AUTO_INCREMENT PRIMARY KEY,
	b_id INT NOT NULL,
	o_filename VARCHAR(255) NOT NULL,
	e_filename VARCHAR(255) NOT NULL,
	FOREIGN KEY(b_id) REFERENCES board(id) ON DELETE CASCADE
);


CREATE TABLE lecture (
	id INT AUTO_INCREMENT PRIMARY KEY,
	s_id INT NOT NULL,
	name VARCHAR(32) NOT NULL,
	o_filename VARCHAR(255) NOT NULL,
	e_filename VARCHAR(255) NOT NULL,
	FOREIGN KEY(s_id) REFERENCES subjects(id) ON DELETE CASCADE
);


INSERT INTO subjects VALUES (NULL, "인프라 활용을 위한 파이썬");
INSERT INTO subjects VALUES (NULL, "애플리케이션 보안");
INSERT INTO subjects VALUES (NULL, "시스템/네트워크 보안 기술");
INSERT INTO subjects VALUES (NULL, "클라우드 보안 기술");

INSERT INTO subjects VALUES (NULL, "클라우드기반 시스템 운영/구축 실무");
INSERT INTO subjects VALUES (NULL, "클라우드기반 취약점 진단 및 대응 실무");
INSERT INTO subjects VALUES (NULL, "데이터 3법과 개인정보보호");
INSERT INTO subjects VALUES (NULL, "클라우드 보안 컨설팅 실무");