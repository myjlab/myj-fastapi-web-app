CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    nickname VARCHAR(64),
    password VARCHAR(64) NOT NULL
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    due_date DATE DEFAULT NULL,
    img_path VARCHAR(255) DEFAULT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE dones (
    id INTEGER PRIMARY KEY,
    FOREIGN KEY (id) REFERENCES tasks(id) ON DELETE CASCADE
);