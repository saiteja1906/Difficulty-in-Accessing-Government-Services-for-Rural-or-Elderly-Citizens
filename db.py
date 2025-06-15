import mysql.connector
from config import MYSQL_CONFIG
from datetime import datetime

def get_db_connection():
    """Create and return a database connection."""
    return mysql.connector.connect(**MYSQL_CONFIG)

def init_db():
    """Initialize the database and create tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        age INT,
        address VARCHAR(255),
        phone VARCHAR(20),
        aadhaar VARCHAR(12) UNIQUE,
        dob DATE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Services Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        service_id VARCHAR(50),
        documents JSON,
        status VARCHAR(20),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        UNIQUE KEY unique_user_service (user_id, service_id)
    )
    """)

    # Create Chat History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        message TEXT,
        response TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    # Create Feedback Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        rating INT,
        comment TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()

def add_user(name, age, address, phone, aadhaar, dob):
    """Add a new user to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        INSERT INTO users (name, age, address, phone, aadhaar, dob)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, age, address, phone, aadhaar, dob))
        
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

def get_user(aadhaar, dob=None):
    """Get user by Aadhaar number and optionally DOB."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        if dob:
            cursor.execute("""
            SELECT * FROM users WHERE aadhaar = %s AND dob = %s
            """, (aadhaar, dob))
        else:
            cursor.execute("""
            SELECT * FROM users WHERE aadhaar = %s
            """, (aadhaar,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def update_user_status(user_id, service_id):
    """Update or get status of a service for a user."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
        SELECT status, last_updated, id as application_id
        FROM services
        WHERE user_id = %s AND service_id = %s
        """, (user_id, service_id))
        
        service = cursor.fetchone()
        if not service:
            return {'status': 'not_applied'}
        
        return {
            'status': service['status'],
            'last_updated': service['last_updated'].isoformat(),
            'application_id': service['application_id']
        }
    finally:
        cursor.close()
        conn.close()

def add_service_application(user_id, service_id, documents):
    """Add a new service application."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        INSERT INTO services (user_id, service_id, documents, status)
        VALUES (%s, %s, %s, 'pending')
        """, (user_id, service_id, str(documents)))
        
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

def add_chat_history(user_id, message, response):
    """Add a chat message to history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        INSERT INTO chat_history (user_id, message, response)
        VALUES (%s, %s, %s)
        """, (user_id, message, response))
        
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_chat_history(user_id, limit=10):
    """Get recent chat history for a user."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
        SELECT message, response, timestamp
        FROM chat_history
        WHERE user_id = %s
        ORDER BY timestamp DESC
        LIMIT %s
        """, (user_id, limit))
        
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def add_feedback(name, rating, comment):
    """Add user feedback."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        INSERT INTO feedback (name, rating, comment)
        VALUES (%s, %s, %s)
        """, (name, rating, comment))
        
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_feedback(limit=10):
    """Get recent feedback."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
        SELECT name, rating, comment, timestamp
        FROM feedback
        ORDER BY timestamp DESC
        LIMIT %s
        """, (limit,))
        
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def update_service_status(application_id, status):
    """Update the status of a service application."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        UPDATE services
        SET status = %s
        WHERE id = %s
        """, (status, application_id))
        
        conn.commit()
    finally:
        cursor.close()
        conn.close()
