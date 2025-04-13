import requests
import vk_api
import threading
import logging

from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange

from database import VkBotDatabase
from vk import VKBot, GROUP_TOKEN

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    filename="vk_bot.log", filemode="a",
                    format='%(asctime)s - %(levelname)s – %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    encoding='utf-8')


vk_session = vk_api.VkApi(token=GROUP_TOKEN)
vk = vk_session.get_api()
upload = vk_api.VkUpload(vk)
longpoll = VkLongPoll(vk_session)
vk_bots = {}
vk_db = VkBotDatabase()
# vk_db.recreate_tables()
def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})

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


def send_photo(user_id, photo_urls, message=''):
    attachments = []
    for photo in photo_urls:
        image = requests.get(photo, stream=True)
        upload_img = upload.photo_messages(photos=image.raw)[0]
        attachment=f"photo{upload_img['owner_id']}_{upload_img['id']}"
        attachments.append(attachment)
    try:
        logger.debug(f"send {len(photo_urls)} photos")
        vk.messages.send(peer_id=user_id, message=message, attachment=attachments, random_id=0)
    except Exception as e:
        logger.error(f'{e}')

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_id_str = str(event.user_id)
        message = event.text.lower()
        if message == 'start':
            if not vk_db.user_exists(user_id_str):
                current_bot = VKBot(event.user_id)
                vk_bots[event.user_id] = current_bot
                current_bot.get_user_info()
                vk_db.add_user(user_id_str)
                t = threading.Thread(target=add_candidates_to_bd, args=(current_bot, vk_db))
                t.start()
            else:
                current_bot = vk_bots[event.user_id]
        elif message == 'get_candidate':
            candidate = vk_db.get_random_none_candidate(user_id_str)
            photo_urls = [url.link for url in vk_db.get_photos(candidate.vk_id)]
            message = f'{candidate.first_name} {candidate.last_name}\n{candidate.link}'
            send_photo(event.user_id, photo_urls, message=message)
            

