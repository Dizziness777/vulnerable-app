from flask import Flask, render_template, request, redirect, session
import psycopg2

app = Flask(__name__)
app.secret_key = 'super_secret_key'


#ПОДКЛЮЧЕНИЕ К БД
def get_db():
    return psycopg2.connect(host="localhost", database="vuln_db", user="vuln_user", password="weakpassword")

#-----------------ОБРАБОТЧИК-----------------
#ГЛАВНАЯ СТРАНИЦА
@app.route('/')
def index():
    print("Main str")
    return render_template('index.html')



#ВХОД
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("login str")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        query = f"SELECT * FROM uyazvimosti_web.users WHERE username='{username}' AND password='{password}'"
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(query)
            user = cur.fetchone()
            if user:
                session['username'] = user[1]
                session['is_admin'] = user[3]
                return redirect('/profile')
            else:
                return "Ошибка входа"
        except Exception as e:
            return f"Ошибка: {e}"
        finally:
            if 'conn' in locals():
                conn.close()
    return render_template('login.html')



#РЕГИСТРАЦИЯ
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(f"INSERT INTO uyazvimosti_web.users (username, password, is_admin) VALUES ('{username}', '{password}', FALSE)")
            conn.commit()
            return "Регистрация успешна <a href='/login'>Войти</a>"
        except Exception as e:
            return f"Ошибка: {e}"
        finally:
            if 'conn' in locals():
                conn.close()
    return render_template('register.html')



#ПРОФИЛЬ
@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect('/login')
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT username, is_admin FROM uyazvimosti_web.users WHERE username = %s", (session['username'],))
        user_data = cur.fetchone()
        if not user_data:
            return "Пользователь не найден", 404
    except Exception as e:
        return f"Ошибка: {e}", 500
    finally:
        if 'conn' in locals():
            conn.close()
    #передача на странцу
    return render_template('profile.html', username=user_data[0], is_admin=user_data[1])



#ВЫХОД
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



#БАЗА ДАННЫХ ПОЛЬЗОВАТЕЛЕЙ
@app.route('/hidden_users_list')
def users_list():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, username, password, is_admin FROM uyazvimosti_web.users")
        users = cur.fetchall()
        return render_template('users_list.html', users=users)
    except Exception as e:
        return f"Ошибка: {e}", 500
    finally:
        if 'conn' in locals():
            conn.close()



#ВЫДАЧА АДМИНКИ            
@app.route('/make_admin', methods=['POST'])
def make_admin():
    user_id = request.form['user_id']
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE uyazvimosti_web.users SET is_admin = TRUE WHERE id = %s", (user_id,))
        conn.commit()
        return redirect('/hidden_users_list')
    except Exception as e:
        return f"Ошибка: {e}", 500
    finally:
        if 'conn' in locals():
            conn.close()
            
                   
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)