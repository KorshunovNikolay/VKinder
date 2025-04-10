import os
import requests
import datetime

from pprint import pprint
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
GROUP_TOKEN = os.getenv('GROUP_TOKEN')

class VKBot:

    def __init__(self, user_id, access_token=ACCESS_TOKEN,  version='5.199'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v':self.version}
        self.base = 'https://api.vk.com/method/'


        self.first_name = ''
        self.last_name = ''
        self.birthday = None
        self.city = None
        self.sex = 0
        self.select_sex = {0: 0, 1: 2, 2: 1}
        self.age = None
        self.candidates_list = []

    def get_user_info(self):
        # Получаем информацию о пользователе
        url = f"{self.base}users.get"
        fields = '''bdate,
                    sex,
                    city'''
        params = {'user_ids': self.id, 'fields':fields}
        response = requests.get(url, params={**self.params, **params})
        user_info = response.json()['response'][0]
        self.first_name = user_info['first_name']
        self.last_name = user_info['last_name']
        self.sex = user_info['sex']
        try:
            self.city = user_info['city']['id']
        except Exception as e:
            f"Ошибка {e} город не указан"
        try:
            self.birthday = user_info['bdate']
            self.age = self.get_user_age()
        except Exception as e:
            f"Ошибка {e} дата рождения не указана"
        self.sex = user_info['sex']

        print(user_info)

        return response.json()['response'][0]

    def get_user_age(self):
        # Вычисляем возраст пользователя
        current_date = datetime.datetime.now()
        birthday_date = datetime.datetime.strptime(self.birthday.replace('.', '-'), "%d-%m-%Y")
        if not birthday_date.year:
            return None
        else:
            birthday_not_passed = (current_date.month, current_date.day) < (birthday_date.month, birthday_date.day)
            age = current_date.year - birthday_date.year - birthday_not_passed
            return age

    def top_vk_photos(self, user_id, album='wall', count=3):
        # Получаем топ-3 фото (макс размер)
        top_photo_list = []
        vk_url = f"{self.base}photos.get?"
        params = {
            'owner_id': user_id,
            'album_id': album,
            'extended': 1
        }
        response = requests.get(vk_url, params={**self.params, **params})
        try:
            all_photos = response.json()['response']['items']
            sorted_photos = sorted(all_photos, key=lambda x: x['likes']['count'], reverse=True)[0:int(count)]
            for current_photo in sorted_photos:
                max_size_photo = max(current_photo['sizes'], key=lambda x: x['height'])
                photo_data = {'url': max_size_photo['url']}
                top_photo_list.append(photo_data)
        except Exception as e:
            f"Ошибка {e} фото отсутствует"

        return top_photo_list

    def candidates_search(self, count=30):
        # поиск кандидатов
        vk_url = f"{self.base}users.search"
        params = {
            'count': count,
            'city': self.city,
            'sex': self.select_sex[self.sex],
            'has_photo': 1,
            'is_closed': 0,
            'can_access_closed': 1,
            'age_from': 18,
            'age_to': 50
        }
        response = requests.get(vk_url, params={**self.params, **params})
        candidates = response.json()['response']['items']
        del_key_list = ['can_access_closed', 'is_closed', 'track_code']
        for candidate in candidates:
            for key in del_key_list:
                del candidate[key]
            candidate['top_photo'] = self.top_vk_photos(candidate['id'])
            candidate['profile'] = f"https://vk.com/id{candidate['id']}"
        self.candidates_list = candidates
        return self.candidates_list


    def __str__(self):
        return (
            f"Имя: {self.first_name}\n"
            f"Фамилия: {self.last_name}\n"
        )


if __name__ == '__main__':
    vkbot = VKBot('') # для теста ввести ID пользователя на VK
    print(vkbot)
    vkbot.get_user_info()
    pprint(vkbot.candidates_search())

