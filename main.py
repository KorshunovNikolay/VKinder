import requests
import vk_api

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

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if not vk_db.user_exists(str(event.user_id)):
            vk_bots[event.user_id] = VKBot(event.user_id)
            vk_bots[event.user_id].get_user_info()
            vk_db.add_user(str(event.user_id))


        current_bot = vk_bots[event.user_id]


        print()
        if event.to_me:
            request = event.text.lower()

            if request == "привет":
                write_msg(event.user_id, f"Хай, {current_bot.first_name}")
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")

