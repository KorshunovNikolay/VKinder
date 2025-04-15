import json
import requests
import vk_api
import logging

from threading import Thread
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange

from database import VkBotDatabase
from keyboards import keyboard, keyboard_start
from vk import VKBot, GROUP_TOKEN


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
            # задается self.event
            self.event = event

            if self.event.type == VkEventType.MESSAGE_NEW and self.event.to_me:
                # задается self.user_id
                self.user_id = str(self.event.user_id)

                if self.event.to_me:
                    request = self.event.text.lower()
                    if request == "start" or request == "next":
                        if not self.vk_db.user_exists(self.user_id):
                            # задается self.current_bot
                            self.current_bot = VKBot(self.user_id)

                            self.vk_bots[self.user_id] = self.current_bot
                            self.current_bot.get_user_info()
                            self.vk_db.add_user(self.user_id)
                            
                            self._threading_adding_candidate() 

                        candidate_id, candidate_first_name, candidate_last_name = self._get_random_none_candidate()
                    elif request == "❤":
                        self.vk_db.add_reaction(self.user_id, candidate_id, True)
                        self._write_msg(f"{candidate_first_name} {candidate_last_name} добавлен(a) в Избранное -> ⭐", keyboard) 
                        self._get_random_none_candidate()
                    elif request == "👎":
                        self.vk_db.add_reaction(self.user_id, candidate_id, False)
                        self._write_msg(f"{candidate_first_name} {candidate_last_name} добавлен(a) в Чёрный список", keyboard) 
                        self._get_random_none_candidate()
                    elif request == "⭐":
                        favorites = self.vk_db.get_candidates_with_mark(user_id=self.user_id, mark=True)
                        if favorites:
                            favorites_list = ""
                            for favorite in favorites:
                                favorites_list += f"{favorite.first_name.upper()} {favorite.last_name.upper()}, https://vk.com/id{favorite.vk_id}\n"
                            self._write_msg(f"Избранное:\n{favorites_list}", keyboard_start) 
                        else:
                            self._write_msg(f"Список пуст", keyboard_start) 
                    else:
                        self._write_msg("Нажмите Start для начала работы", keyboard_start) 

    def _threading_adding_candidate(self):
        t = Thread(target=self._add_candidates_to_bd)
        t.start()
        self._write_msg("Подождите, собираем базу для вас 💙")
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
                'keyboard': json.dumps(keyboard)
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
        self._send_photo(photo_urls, message=message)
        return id, first_name, last_name

    def _write_msg(self, message, keyboard=None):
        values = {
            'user_id': self.user_id,
            'message': message,
            'random_id': randrange(10 ** 7)
        }
        if keyboard:
            values['keyboard']=json.dumps(keyboard)
        self.vk.method('messages.send', values) #тут надл добавтить логирование

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



