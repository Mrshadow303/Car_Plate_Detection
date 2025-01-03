import mysql.connector


def init_db():
    conn = mysql.connector.connect(
        host="localhost",  # MySQL 服务器地址
        user="root",  # MySQL 用户名
        password="20021119lyq",  # MySQL 密码
        database="car_plate_detection",  # 数据库名称
    )
    cursor = conn.cursor()

    # 创建用户表
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """
    )

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    init_db()
