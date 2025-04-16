import json
import requests
import vk_api
import logging
from threading import Thread
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange

from database import VkBotDatabase
from keyboards import kb_choice, kb_start, kb_continue
from vk import VkBotApi, GROUP_TOKEN

logging_level = logging.DEBUG
logging.basicConfig(level=logging_level,
                    filename="db_log.log", filemode="w",
                    format='%(asctime)s - %(levelname)s – %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    encoding='utf-8')

class VkBotServer:

    def __init__(self, group_token):
        self.vk = vk_api.VkApi(token=group_token)
        self.vk_db = VkBotDatabase()
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
                    logging.info(f"User id{self.event.user_id}: {request}")

                    if request == "start":
                        if not self.vk_db.user_exists(self.user_id):
                            self.current_bot = VkBotApi(self.user_id)
                            self.current_bot.get_user_info()
                            self.vk_db.add_user(self.user_id)
                            self._threading_adding_candidate()
                        self._write_msg(f"База собрана.\n"
                                        f"Для перехода к списку кандидатов нажмите CONTINUE", kb_continue)

                    elif request == "next" or request == "continue":
                        candidate_id, candidate_first_name, candidate_last_name = self._get_random_none_candidate()

                    elif request == "❤":
                        self.vk_db.add_reaction(self.user_id, candidate_id, True)
                        msg = f"{candidate_first_name} {candidate_last_name} добавлен(a) в Избранное -> ⭐"
                        self._write_msg(msg)
                        candidate_id, candidate_first_name, candidate_last_name = self._get_random_none_candidate()

                    elif request == "👎":
                        self.vk_db.add_reaction(self.user_id, candidate_id, False)
                        msg = f"{candidate_first_name} {candidate_last_name} добавлен(a) в Чёрный список"
                        self._write_msg(msg)
                        candidate_id, candidate_first_name, candidate_last_name = self._get_random_none_candidate()

                    elif request == "⭐":
                        favorites = self.vk_db.get_candidates_with_mark(user_id=self.user_id, mark=True)
                        if favorites:
                            favorites_list = ""
                            for favorite in favorites:
                                favorites_list += (f"{favorite.first_name.upper()} {favorite.last_name.upper()},"
                                                   f" https://vk.com/id{favorite.vk_id}\n")
                            self._write_msg(f"Избранное:\n{favorites_list}", kb_continue)
                        else:
                            self._write_msg(f"Список пуст", kb_start)

                    else:
                        self._write_msg("Нажмите START для начала работы", kb_start)


    def _threading_adding_candidate(self):
        t = Thread(target=self._add_candidates_to_bd)
        t.start()
        self._write_msg("Подождите, собираем базу для вас 💙\n"
                        "Для получения более точных результатов, "
                        "пожалуйста, заполните свой возраст и "
                        "город в профиле ВК")
        t.join()

    def _send_photo(self, photo_urls, message=''):
        upload = vk_api.VkUpload(self.vk)
        attachments = []
        for photo_url in photo_urls:
            image = requests.get(photo_url, stream=True)
            upload_img = upload.photo_messages(photos=image.raw)[0]
            attachment=f"photo{upload_img['owner_id']}_{upload_img['id']}"
            attachments.append(attachment)
        try:
            values = {
                'peer_id':self.user_id,
                'message':message,
                'attachment': ','.join(attachments),
                'random_id': randrange(10 ** 7),
                'keyboard': json.dumps(kb_choice)
            }
            self.vk.method('messages.send', values=values) 
        except Exception as e:
            print(f'{e}')

    def _get_random_none_candidate(self):
        candidate = self.vk_db.get_random_none_candidate(self.user_id)
        id = candidate.vk_id
        first_name = candidate.first_name
        last_name = candidate.last_name
        link = candidate.link
        photo_urls = [url.link for url in self.vk_db.get_photos(id)]
        message = f'{first_name} {last_name}\n{link}'
        try:
            self._send_photo(photo_urls, message=message)
        except Exception as e:
            logging.warning(f"Не получилось скачать фото. Ошибка: {e}")
            self._write_msg(message, kb_continue)
        return id, first_name, last_name


    def _write_msg(self, message, keyboard=None):
        values = {
            'user_id': self.user_id,
            'message': message,
            'random_id': randrange(10 ** 7)
        }
        if keyboard:
            values['keyboard']=json.dumps(keyboard)
        self.vk.method('messages.send', values)

    def _add_candidates_to_bd(self):
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

    def recreate_tables(self):
        self.vk_db.recreate_tables()


if __name__ == '__main__':
    bot = VkBotServer(GROUP_TOKEN)
    bot.recreate_tables()
    bot.start()



