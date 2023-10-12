from flask import (
    Flask,
    request,
    render_template,
    redirect,
    flash,
    get_flashed_messages,
    url_for,
    session
)

from repository import User
import os

app = Flask(__name__)

# Установка секретного ключа для подписи сессий
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Использование серверной сессии (в данном примере, используем файловую сессию)
app.config['SESSION_TYPE'] = 'filesystem'


repo = User()


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']

        # Проверяем, что введенный email совпадает с валидным email
        users_data = repo.load_user_data()  # Загружаем данные пользователей
        valid_emails = [user['email'] for user in users_data]

        if email in valid_emails:
            # Устанавливаем флаг аутентификации в сессии
            session['authenticated'] = True
            flash('Вы успешно выполнили вход', 'success')
            return redirect(url_for('users'))
        else:
            return render_template('users/login.html', error='Неверный email')

    return render_template('users/login.html', error=None)


@app.route('/logout')
def logout():
    # Удаляем флаг аутентификации из сессии
    session.pop('authenticated', None)
    return redirect(url_for('login'))


@app.route('/')
def index():
    if 'count' not in session:
        session['count'] = 0
    else:
        session['count'] += 1

    return f'Count: {session["count"]}'


@app.route('/users')
def users():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

    users_data = repo.load_user_data()
    search = request.args.get('term', '')

    if search:
        users_data = [user for user in users_data if repo.filter_name(user, search)]

    page = request.args.get('page', 1, type=int)
    per_page = 5
    offset = (page - 1) * per_page

    users_on_page = users_data[offset:page * per_page]

    messages = get_flashed_messages(with_categories=True)

    return render_template(
        'users/index.html',
        search=search,
        messages=messages,
        page=page,
        users=users_on_page,
    )


@app.route('/users/<int:id>')
def get_user(id):
    user = None
    users_data = repo.load_user_data()
    for u in users_data:
        if u['id'] == str(id):
            user = u
            break

    if user:
        return render_template(
            'users/show.html',
            user=user
        )

    else:
        return "No user found", 404


@app.route('/users/new', methods=['GET', 'POST'])
def users_new():
    if request.method == 'GET':
        user = {}
        errors = {}
        return render_template('users/new.html',
                               user=user,
                               errors=errors
                               ), 422

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        user = {'name': name, 'email': email}

        errors = repo.validate_user(user)

        if errors:
            return render_template('users/new.html',
                                   user=user,
                                   errors=errors
                                   )

        users_data = repo.load_user_data()
        user['id'] = repo.generate_user_id(users_data)

        users_data.append(user)
        repo.save_user_data(users_data)

        flash(f'Пользователь c именем {name} успешно зарегистрирован', 'success')

        return redirect(url_for('users'))


@app.route('/users/<int:id>/edit', methods=['GET', 'POST'])
def edit_user(id):
    users_data = repo.load_user_data()
    user = next((u for u in users_data if u['id'] == str(id)), None)

    if request.method == 'POST':
        data = request.form.to_dict()
        errors = repo.validate_user(data)

        if errors:
            return render_template('users/edit.html', user=user, errors=errors), 422

        if user:
            user['name'] = data['name']
            repo.save_user_data(users_data)

            flash('Информация о пользователе успешно обновлена', 'success')

            return redirect(url_for('get_user', id=id))
        else:
            return "Пользователя с таким id не существует", 404

    elif request.method == 'GET':
        errors = []
        if user:
            return render_template('users/edit.html', user=user, errors=errors)
        else:
            return "Пользователя с таким id не существует", 404


@app.route('/users/<int:id>/delete', methods=['POST'])
def delete_user(id):
    repo.destroy(id)
    flash('Пользователь был удален', 'success')

    return redirect(url_for('users'))
