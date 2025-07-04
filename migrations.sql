-- Users table
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

-- Questions table
CREATE TABLE IF NOT EXISTS questions (
    id TEXT PRIMARY KEY,
    subject TEXT,
    category TEXT,
    difficulty TEXT,
    marks REAL,
    questionText TEXT,
    explanation TEXT,
    questionType TEXT,
    hasImage INTEGER
);

-- Answers table
CREATE TABLE IF NOT EXISTS answers (
    id TEXT PRIMARY KEY,
    questionId TEXT,
    optionLabel TEXT,
    optionText TEXT,
    isCorrect INTEGER,
    FOREIGN KEY(questionId) REFERENCES questions(id)
);

-- Performance table
CREATE TABLE IF NOT EXISTS performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userId TEXT,
    questionId TEXT,
    userAnswer TEXT,
    isCorrect INTEGER,
    answeredAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(userId) REFERENCES users(id),
    FOREIGN KEY(questionId) REFERENCES questions(id)
);

-- Question images table
CREATE TABLE IF NOT EXISTS questionImages (
    id TEXT PRIMARY KEY,
    questionId TEXT,
    imagePath TEXT,
    altText TEXT,
    FOREIGN KEY(questionId) REFERENCES questions(id)
);