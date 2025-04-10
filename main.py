import requests
import vk_api
import threading

from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange

from database import VkBotDatabase
from vk import VKBot, GROUP_TOKEN


vk = vk_api.VkApi(token=GROUP_TOKEN)
longpoll = VkLongPoll(vk)
vk_bots = {}
vk_db = VkBotDatabase()
vk_db.recreate_tables()

def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})
#
def add_candidates_to_bd(bot, db):
    bot.candidates_search()
    for candidate in bot.candidates_list:
        candidate_id_str = str(candidate['id'])
        if not db.candidate_exists(candidate_id_str):
            params = {
                'vk_id': candidate_id_str,
                'first_name': candidate['first_name'],
                'last_name': candidate['last_name'],
                'link': candidate['profile']
            }
            db.add_candidate(**params)
            db.add_reaction(user_id_str, candidate_id_str)
            if candidate['top_photo']:
                for photo in candidate['top_photo']:
                    db.add_photo(candidate_id_str, photo['url'])


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        user_id_str = str(event.user_id)
        if not vk_db.user_exists(user_id_str):
            current_bot = VKBot(event.user_id)
            vk_bots[event.user_id] = current_bot
            current_bot.get_user_info()
            vk_db.add_user(user_id_str)
            t = threading.Thread(target=add_candidates_to_bd, args=(current_bot, vk_db))
            t.start()
        else:
            current_bot = vk_bots[event.user_id]
#

        print()
        if event.to_me:
            request = event.text.lower()

            if request == "привет":
                write_msg(event.user_id, f"Хай, {current_bot.first_name}")
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")

