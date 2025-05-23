import os
import requests
import datetime
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
GROUP_TOKEN = os.getenv('GROUP_TOKEN')

class VkBotApi:

    def __init__(self, user_id, access_token=ACCESS_TOKEN,  version='5.89'):
        self.token = access_token
        self.version = version
        self.params = {'access_token': self.token, 'v':self.version}
        self.base = 'https://api.vk.com/method/'

        self.id = user_id
        self.first_name = ''
        self.last_name = ''
        self.birthday = None
        self.city = None
        self.age = None
        self.sex = 0
        self.candidates_list = []
        self.age_from = 18
        self.age_to = 99
        self.offset = 0

    def get_user_info(self) -> dict:
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
            self.age = self.get_user_age(user_info['bdate'])
        except Exception as e:
            f"Ошибка {e} дата рождения не указана"
        self.sex = user_info['sex']
        return response.json()['response'][0]

    def get_user_age(self, birthday: str, deviation=5) -> int:
        # Вычисляем возраст пользователя
        current_date = datetime.datetime.now()
        birthday_date = datetime.datetime.strptime(birthday.replace('.', '-'), "%d-%m-%Y")
        if not birthday_date.year:
            return None
        else:
            birthday_not_passed = (current_date.month, current_date.day) < (birthday_date.month, birthday_date.day)
            age = current_date.year - birthday_date.year - birthday_not_passed
            self.age_from = 18 if age - deviation < 18 else age - deviation
            self.age_to = 99 if age + deviation > 99 else age + deviation
            return age

    def top_vk_photos(self, user_id: int, album='profile', photo_count=3) -> list:
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
            sorted_photos = sorted(all_photos, key=lambda x: x['likes']['count'], reverse=True)[0:int(photo_count)]
            for current_photo in sorted_photos:
                max_size_photo = max(current_photo['sizes'], key=lambda x: x['height'])
                photo_data = {'url': max_size_photo['url']}
                top_photo_list.append(photo_data)
        except Exception as e:
            f"Ошибка {e} фото отсутствует"
        return top_photo_list

    def candidates_search(self, count=1000) -> list:
        # поиск кандидатов
        select_sex = {1: 2, 2: 1}
        vk_url = f"{self.base}users.search"
        fields = "is_closed, can_access_closed"
        params = {
            'offset': self.offset,
            'count': count,
            'sex': select_sex[self.sex],
            'has_photo': 1,
            'age_from': self.age_from,
            'age_to': self.age_to,
            'fields': fields
        }
        if self.city:
            params['city'] = self.city
        response = requests.get(vk_url, params={**self.params, **params})
        candidates = response.json()['response']['items']
        for candidate in candidates:
            if not candidate['is_closed'] == True or candidate['can_access_closed'] == True:
                candidate['top_photo'] = self.top_vk_photos(candidate['id'])
                candidate['profile'] = f"https://vk.com/id{candidate['id']}"
                if candidate['top_photo']:
                    self.candidates_list.append(candidate)
        self.offset += count
        return self.candidates_list

    def __str__(self):
        return (
            f"Имя: {self.first_name}\n"
            f"Фамилия: {self.last_name}\n"
        )


if __name__ == '__main__':
    vkbot = VkBotApi('') # для теста ввести ID пользователя на VK
    pprint(vkbot.get_user_info())
    pprint(vkbot.candidates_search())


