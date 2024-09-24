CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    nickname TEXT,
    password TEXT NOT NULL,
    UNIQUE (email)
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    due_date DATE,
    img_path TEXT,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE dones (
    id INTEGER PRIMARY KEY,
    FOREIGN KEY (id) REFERENCES tasks (id)
);