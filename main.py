import json
import requests
import vk_api
import threading
import logging

from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange

from database import VkBotDatabase
from keyboards import keyboard, keyboard_start
from vk import VKBot, GROUP_TOKEN

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    filename="vk_bot.log", filemode="a",
                    format='%(asctime)s - %(levelname)s – %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    encoding='utf-8')

vk = vk_api.VkApi(token=GROUP_TOKEN)

upload = vk_api.VkUpload(vk)
longpoll = VkLongPoll(vk)
vk_bots = {}
vk_db = VkBotDatabase()
vk_db.recreate_tables()
candidate_id = ''

def write_msg(user_id, message, keyboard=None):
    values = {
        'user_id': user_id,
        'message': message,
        'random_id': randrange(10 ** 7)
    }
    if keyboard:
        values['keyboard']=json.dumps(keyboard)
    vk.method('messages.send', values)

def send_photo(user_id, photo_urls, message=''):
    attachments = []
    for photo in photo_urls:
        image = requests.get(photo, stream=True)
        upload_img = upload.photo_messages(photos=image.raw)[0]
        attachment=f"photo{upload_img['owner_id']}_{upload_img['id']}"
        attachments.append(attachment)
    try:
        logger.debug(f"send {len(photo_urls)} photos")
        values = {
            'peer_id':user_id,
            'message':message,
            'attachment': ','.join(attachments),
            'random_id': randrange(10 ** 7),
            'keyboard': json.dumps(keyboard)
        }
        vk.method('messages.send', values=values)
    except Exception as e:
        logger.error(f'{e}')

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
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_id_str = str(event.user_id)


        print()
        if event.to_me:
            request = event.text.lower()
            logger.info(f'Сообщение от {event.user_id}: {request}')

            if request == "привет":
                write_msg(event.user_id, f"Привет", keyboard_start)
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            elif request == "start" or request == "next":
                if not vk_db.user_exists(user_id_str):
                    current_bot = VKBot(event.user_id)
                    vk_bots[event.user_id] = current_bot
                    current_bot.get_user_info()
                    vk_db.add_user(user_id_str)
                    t = threading.Thread(target=add_candidates_to_bd, args=(current_bot, vk_db))
                    t.start()
                    write_msg(event.user_id, "Подождите, идёт создание списка кандидатов")
                    t.join()
                candidate = vk_db.get_random_none_candidate(user_id_str)
                candidate_id = candidate.vk_id
                photo_urls = [url.link for url in vk_db.get_photos(candidate.vk_id)]
                message = f'{candidate.first_name} {candidate.last_name}\n{candidate.link}'
                send_photo(event.user_id, photo_urls, message=message)
            elif request == "add favorite":
                vk_db.add_reaction(user_id_str, candidate_id, True)
                write_msg(event.user_id, f"Кандидат добавлен в Избранное, нажмите Next", keyboard)
            elif request == "to ignore":
                vk_db.add_reaction(user_id_str, candidate_id, False)
                write_msg(event.user_id, f"Кандидат добавлен в Чёрный список, нажмите Next", keyboard)
            elif request == "favorites":
                favorites = vk_db.get_candidates_with_mark(user_id=user_id_str, mark=True)
                if favorites:
                    favorites_list = ""
                    for favorite in favorites:
                        favorites_list += f"{favorite.first_name} {favorite.last_name}, https://vk.com/id{favorite.vk_id}\n"
                    write_msg(event.user_id, f"Избранное:\n{favorites_list}", keyboard_start)
                else:
                    write_msg(event.user_id, f"Список пуст", keyboard_start)
            else:
                write_msg(event.user_id, "Нажмите Start для начала работы", keyboard_start)
