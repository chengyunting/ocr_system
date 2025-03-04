import hashlib
import json
# gh browse --commit d0724b0f41d4ea0ab8fc5cc1d9046ad8ee70fdb4
# import os
# import cv2  # 加入 OpenCV 导入
from flask import Flask, render_template, request, redirect, url_for, session
from models.history_model import History
from config import Config
from flask_mysqldb import MySQL
#upload新添加
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object(Config)  # 加载配置文件
app.secret_key = 'sup3r_s3cr3t_k3y!123'  # 必须设置
csrf = CSRFProtect(app)  # 新增此行初始化 CSRF
mysql = MySQL(app)  # 在这里初始化数据库连接
# 证件类型中英对照
DOCUMENT_TYPE_NAMES = {
    "id_card": "身份证",
    "driver_license": "驾驶证",
    "social_security": "社保卡"
}

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


from werkzeug.utils import secure_filename
import os
import cv2

@app.route('/upload', methods=['GET', 'POST'])  # 允许GET和POST方法
def upload():
    # ========== 登录状态检查 ==========
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # ========== POST请求处理文件上传 ==========
    if request.method == 'POST':
        try:
            # 原有的文件处理逻辑保持完全一致
            if 'file' not in request.files:
                return "No file part"

            file = request.files['file']
            if file.filename == '':
                return "No selected file"

            # 安全处理文件名
            filename = secure_filename(file.filename)
            upload_dir = 'uploads'
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)

            # 验证图片有效性
            img = cv2.imread(file_path)
            if img is None:
                os.remove(file_path)
                return "Invalid image file"

            # OCR识别（修改此处）
            document_type = request.form.get('document_type')

            # OCR识别部分修改后代码
            if document_type == "id_card":
                document_type='身份证'
                from recognizers.id_recognizer import recognize_id_card
                structured_data = recognize_id_card(file_path)  # 变量名改为 structured_data
            elif document_type == "driver_license":
                document_type = '驾驶证'
                from recognizers.driver_recognizer import recognize_driver_license
                structured_data = recognize_driver_license(file_path)
            elif document_type == "social_security":
                document_type = '社保卡'
                from recognizers.social_recognizer import recognize_social_security
                structured_data = recognize_social_security(file_path)

            # 存储时带上证件类型
            History.save(session['user_id'], document_type, structured_data, mysql)

            # 确保传递名为 fields 的字典参数
            return render_template('result.html',
                                   doc_type=document_type,  # 证件类型（如"身份证"）
                                   fields=structured_data  # 结构化字典（必须包含键值对）
                                   )

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template('upload.html')


#保存识别结果__meiyong
@app.route('/save_recognition', methods=['POST','GET'])
def save_recognition():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # 获取表单数据
    recognized_text = request.form.get('recognized_text')
    document_type = request.form.get('document_type')  # 新增此行

    # 获取用户ID
    user_id = session.get('user_id')

    # 保存到数据库（document_type 动态传入）
    try:
        History.save(user_id, document_type, recognized_text, mysql)
        return redirect(url_for('history'))
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