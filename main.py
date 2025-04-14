import requests
import vk_api
import threading

from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
from vk_api.upload import VkUpload
from database import VkBotDatabase
from vk import VKBot, GROUP_TOKEN


vk = vk_api.VkApi(token=GROUP_TOKEN)
upload = VkUpload(vk)

longpoll = VkLongPoll(vk)
vk_bots = {}
vk_db = VkBotDatabase()
vk_db.recreate_tables()

photos = [
    {'url': 'https://sun9-42.userapi.com/s/v1/if1/5IgwCVpxjx9tLUz56kgq4GO9-p3xOeyxnC9tteZeyQrDRm-VNrio8ZPovmFiNnKDiY7qBB6v.jpg?quality=96&as=32x40,48x60,72x90,108x135,160x200,240x300,360x449,480x599,540x674,640x799,720x899,750x936&from=bu&cs=750x936'},
    {'url': 'https://sun9-23.userapi.com/s/v1/if1/iyAm4_RvQGXXcHQRxjCPwHP_M8JlzMa7WIR5bcj51hSD25eTzp_fGCgw_bFg_DrlSdq8Qr69.jpg?quality=96&as=32x50,48x74,72x112,108x167,160x248,240x372,360x558,480x744,540x837,640x992,697x1080&from=bu&cs=697x1080'},
    {'url': 'https://sun9-45.userapi.com/s/v1/if1/rgBvnNDx9Z01dNDOIOJHz418zaQvmZbsmSDVZRTyODhMtkpnN7Dd0RlXarjsijrtIllOzw.jpg?quality=96&as=32x48,48x72,72x108,108x162,160x240,240x360,360x540,480x720,540x810,640x960,682x1023&from=bu&cs=682x1023'}
]

def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})

def send_photo(user_id, photo_list, message=''):
    for photo in photo_list:
        image = requests.get(url=photo['url'], stream=True)
        upload_img = upload.photo_messages(photos=image.raw)[0]
        attachment=f"photo{upload_img['owner_id']}_{upload_img['id']}"
        vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), 'attachment': attachment})




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
            elif request == "p":
                send_photo(event.user_id, photos, '')
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")


