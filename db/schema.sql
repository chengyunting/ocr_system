CREATE DATABASE ocr_system;

USE ocr_system;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE recognition_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    document_type VARCHAR(50),
    recognition_text TEXT,
    recognition_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
