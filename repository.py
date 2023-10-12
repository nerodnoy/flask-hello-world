import json
import os

DATA_FILE_PATH = 'data/data.json'


class User:
    @staticmethod
    def filter_name(user, search):
        return user['name'].lower().startswith(search.lower())

    @staticmethod
    def generate_user_id(user_data):
        return str(len(user_data) + 1)

    @staticmethod
    def validate_user(user):
        errors = {}

        if not user.get('name'):
            errors['name'] = "Имя пользователя не может быть пустым"

        if not user.get('email'):
            errors['email'] = "Email не может быть пустым"

        if 0 < len(user.get('name')) < 5:
            errors['name'] = "Имя пользователя должно быть длиннее 4-ех символов"

        return errors

    @staticmethod
    def save_user_data(user_data):
        with open(DATA_FILE_PATH, 'w') as file:
            json.dump(user_data, file, indent=2)

    @staticmethod
    def load_user_data():
        if os.path.exists(DATA_FILE_PATH) and os.path.getsize(DATA_FILE_PATH) > 0:
            with open(DATA_FILE_PATH, 'r') as file:
                return json.load(file)
        else:
            return []

    @staticmethod
    def destroy(user_id):
        user_data = User.load_user_data()
        updated_user_data = [user for user in user_data if user['id'] != str(user_id)]
        User.save_user_data(updated_user_data)
