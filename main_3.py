import json
import requests
import vk_api
import logging

from threading import Thread
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange

from database import VkBotDatabase
from keyboards import keyboard, keyboard_start
from vk import VKBotApi, GROUP_TOKEN


class VkBotServer:
    def __init__(self, group_token):
        self.vk = vk_api.VkApi(token=group_token)
        self.vk_db = VkBotDatabase()
        self.vk_bots = {}
        self.event = None
        self.user_id = None
        self.current_bot = None

    def start(self):
        for event in VkLongPoll(self.vk).listen():
            self.event = event
            if self.event.type == VkEventType.MESSAGE_NEW and self.event.to_me:
                self.user_id = str(self.event.user_id)
                if self.event.to_me:
                    request = self.event.text.lower()

                    if request == "start" and not self.vk_db.user_exists(self.user_id):
                        self.current_bot = VKBotApi(self.user_id)
                        self.vk_bots[self.user_id] = self.current_bot
                        self.current_bot.get_user_info()
                        self.vk_db.add_user(self.user_id)
                        self.threading_adding_candidate()

                        candidate = self.get_and_show_next_candidate()

                    elif request == "start" or request == "next":
                        candidate = self.get_and_show_next_candidate()

                    elif request == "❤":
                        message = "{} {} добавлен(a) в Избранное -> ⭐"
                        self.add_mark(candidate, True, message)
                        candidate = self.get_and_show_next_candidate()

                    elif request == "👎":
                        message = "{} {} добавлен(a) в Чёрный список"
                        self.add_mark(candidate, False, message)
                        candidate = self.get_and_show_next_candidate()

                    elif request == "⭐":
                        favorites = self.vk_db.get_candidates_with_mark(user_id=self.user_id, mark=True)
                        if favorites:
                            favorites_list = ""
                            for favorite in favorites:
                                favorites_list += (f"{favorite.first_name.upper()} {favorite.last_name.upper()},"
                                                   f" https://vk.com/id{favorite.vk_id}\n")
                            self.write_msg(f"Избранное:\n{favorites_list}", keyboard_start)
                        else:
                            self.write_msg(f"Список пуст", keyboard_start)
                    else:
                        self.write_msg("Нажмите Start для начала работы", keyboard_start)

    def add_mark(self, candidate, mark, message):
        id = candidate.vk_id
        first_name = candidate.first_name
        last_name = candidate.last_name
        self.vk_db.add_reaction(self.user_id, id, mark)
        self.write_msg(message.format(first_name, last_name), keyboard)

    def threading_adding_candidate(self):
        t = Thread(target=self.add_candidates_to_bd)
        t.start()
        self.write_msg("Подождите, подбираем кандидатов для вас 💙")
        t.join()
        self.write_msg("Подобрали кандидатов, можете приступать!")

    def get_and_show_next_candidate(self):
        candidate = self.vk_db.get_random_none_candidate(self.user_id)
        self.send_candidate(candidate)
        return candidate

    def send_candidate(self, candidate):
        link = candidate.link
        photo_urls = [url.link for url in self.vk_db.get_photos(id)]
        message = f'{candidate.first_name} {candidate.last_name}\n{link}'
        self.send_photo(photo_urls, message=message)

    def write_msg(self, message, keyboard=None):
        values = {
            'user_id': self.user_id,
            'message': message,
            'random_id': randrange(10 ** 7)
        }
        if keyboard:
            values['keyboard'] = json.dumps(keyboard)
        self.vk.method('messages.send', values)  # тут надо добавить логирование

    def add_candidates_to_bd(self):
        self.current_bot.candidates_search()
        for candidate in self.current_bot.candidates_list:
            candidate_id = str(candidate['id'])
            if not self.vk_db.candidate_exists(candidate_id):
                params = {
                    'vk_id': candidate_id,
                    'first_name': candidate['first_name'],
                    'last_name': candidate['last_name'],
                    'link': candidate['profile']
                }
                self.vk_db.add_candidate(**params)
                self.vk_db.add_reaction(self.user_id, candidate_id)
                if candidate['top_photo']:
                    for photo in candidate['top_photo']:
                        self.vk_db.add_photo(candidate_id, photo['url'])

    def send_photo(self, photo_urls, message=''):
        upload = vk_api.VkUpload(self.vk)
        attachments = []
        for photo_url in photo_urls:
            image = requests.get(photo_url, stream=True)
            upload_img = upload.photo_messages(photos=image.raw)[0]
            attachment = f"photo{upload_img['owner_id']}_{upload_img['id']}"
            attachments.append(attachment)
        try:
            values = {
                'peer_id': self.user_id,
                'message': message,
                'attachment': ','.join(attachments),
                'random_id': randrange(10 ** 7),
                'keyboard': json.dumps(keyboard)
            }
            self.vk.method('messages.send', values=values)
        except Exception as e:
            print(f'{e}')

    def recreate_tables(self):
        self.vk_db.recreate_tables()


if __name__ == '__main__':
    VKinder = VkBotServer(GROUP_TOKEN)
    VKinder.recreate_tables()
    VKinder.start()
