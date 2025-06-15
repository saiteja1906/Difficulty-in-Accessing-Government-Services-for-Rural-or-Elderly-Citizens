import mysql.connector
from config import MYSQL_CONFIG

def create_database():
    # First connect without database to create it
    config = MYSQL_CONFIG.copy()
    del config['database']
    
    try:
        # Connect to MySQL server
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
        print(f"Database '{MYSQL_CONFIG['database']}' created successfully!")
        
        # Switch to the database
        cursor.execute(f"USE {MYSQL_CONFIG['database']}")
        
        # Create tables
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
        print("Users table created successfully!")

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
        print("Services table created successfully!")

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
        print("Chat history table created successfully!")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            rating INT,
            comment TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("Feedback table created successfully!")

        # Add some sample data
        cursor.execute("""
        INSERT IGNORE INTO users (name, age, address, phone, aadhaar, dob)
        VALUES 
        ('Test User', 65, '123 Village Road, Rural Area', '9876543210', '123456789012', '1959-06-05'),
        ('Sample Elder', 70, '456 Gram Panchayat, District', '9876543211', '987654321098', '1954-03-12')
        """)
        print("Sample users added successfully!")

        cursor.execute("""
        INSERT IGNORE INTO services (user_id, service_id, status)
        VALUES 
        (1, 'pension', 'active'),
        (1, 'ration', 'pending'),
        (2, 'pension', 'active')
        """)
        print("Sample services added successfully!")

        cursor.execute("""
        INSERT IGNORE INTO feedback (name, rating, comment)
        VALUES 
        ('Village User', 5, 'Very helpful for elderly citizens'),
        ('Gram Panchayat', 4, 'Easy to use interface')
        """)
        print("Sample feedback added successfully!")

        conn.commit()
        print("\nDatabase setup completed successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_database() 