import hashlib
import os
import cv2  # 加入 OpenCV 导入
from flask import Flask, render_template, request, redirect, url_for, session
from ocr.recognizer import recognize_document  # 假设你有这个OCR识别函数
from models.user_model import User
from models.history_model import History
from config import Config
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config.from_object(Config)  # 加载配置文件

mysql = MySQL(app)  # 在这里初始化数据库连接


@app.route('/')
def index():
    return render_template('index.html')  # 首页


@app.route('/home')
def home():
    return render_template('home.html')


# 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 登录逻辑
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and hashlib.sha256(password.encode()).hexdigest() == user[2]:  # user[2]是密码字段
            session['user_id'] = user[0]  # 保存用户id到session
            return redirect(url_for('upload'))
        else:
            return "Invalid credentials!"

    return render_template('login.html')


# 注册路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 密码加密
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))

    return render_template('register.html')

# 查看历史记录
@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # 如果没有登录，重定向到登录页

    user_id = session.get('user_id')
    records = History.get_all(user_id, mysql)  # 获取当前用户的历史记录
    return render_template('history.html', records=records)


# 上传文件并识别
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # 如果没有登录，重定向到登录页

    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"

        # 使用 os.path.join 来构建路径，确保跨平台兼容
        filename = os.path.join('uploads', file.filename)

        # 确保上传的文件路径是绝对路径
        absolute_path = os.path.abspath(filename)

        # 保存上传的文件
        file.save(absolute_path)

        # 打印保存的文件路径
        print(f"Uploaded file saved at {absolute_path}")

        # 尝试读取文件，确保文件有效
        try:
            # 使用 OpenCV 检查图片是否可以读取
            img = cv2.imread(absolute_path)

            if img is None:
                return f"Error: The file at {absolute_path} is not a valid image file or is corrupted."

            # 使用 EasyOCR 识别图片内容
            recognized_text = recognize_document(absolute_path)

            # 存储识别结果到数据库
            user_id = session.get('user_id')  # 获取当前用户的ID
            document_type = '身份证'  # 假设用户上传的是身份证
            History.save(user_id, document_type, recognized_text, mysql)  # 传递mysql实例

            return render_template('result.html', text=recognized_text)

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template('upload.html')



# 查看历史记录
@app.route('/save_recognition', methods=['POST'])
def save_recognition():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # 如果没有登录，重定向到登录页

    # 获取识别的文本
    recognized_text = request.form.get('recognized_text')

    # 获取当前登录的用户ID
    user_id = session.get('user_id')

    # 假设文档类型是身份证
    document_type = '身份证'

    # 将识别结果保存到数据库
    try:
        History.save(user_id, document_type, recognized_text, mysql)  # 调用 save 方法保存到数据库
        return redirect(url_for('history'))  # 重定向到历史记录页面
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/view_record/<int:record_id>')
def view_record(record_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))  # 如果没有登录，重定向到登录页

    # 获取指定记录
    record = History.get_by_id(record_id, mysql)
    if record:
        return render_template('view_record.html', record=record)
    else:
        return "Record not found", 404


# 删除历史记录
@app.route('/history/delete/<int:record_id>', methods=['POST'])
def delete_history(record_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))  # 如果没有登录，重定向到登录页

    # 调用History模型删除记录
    History.delete(record_id, mysql)  # 传递mysql实例

    return redirect(url_for('history'))


# 登出
@app.route('/logout')
def logout():
    session.clear()  # 清除当前会话中的用户信息
    return redirect(url_for('login'))  # 登出后重定向到登录页面


if __name__ == '__main__':
    app.run(debug=True)