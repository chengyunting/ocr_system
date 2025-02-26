class History:
    @staticmethod
    def save(user_id, document_type, recognition_text, mysql):
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO recognition_history (user_id, document_type, recognition_text) VALUES (%s, %s, %s)",
            (user_id, document_type, recognition_text)
        )
        mysql.connection.commit()
        cursor.close()

    @staticmethod
    def update(record_id, recognition_text, mysql):
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE recognition_history SET recognition_text = %s WHERE id = %s",
            (recognition_text, record_id)
        )
        mysql.connection.commit()
        cursor.close()

    @staticmethod
    def get_all(user_id, mysql):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM recognition_history WHERE user_id = %s", (user_id,))
        records = cursor.fetchall()
        cursor.close()
        return records

    @staticmethod
    def delete(record_id, mysql):
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM recognition_history WHERE id = %s", (record_id,))
        mysql.connection.commit()
        cursor.close()

    # 新增方法：根据 record_id 获取单条记录
    @staticmethod
    def get_by_id(record_id, mysql):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM recognition_history WHERE id = %s", (record_id,))
        record = cursor.fetchone()
        cursor.close()
        return record

