from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from settings import access_key, gid, me, v
import threading
import traceback
import importlib
import commands
import vk_api
import utils
import bot
import vk

vk_session = vk_api.VkApi(token=access_key)
api = vk.API(vk.Session(access_token=access_key), v=v, lang='ru')

if __name__ == '__main__':
    database = utils.VkUsers()

    while True:
        try:
            longpoll = VkBotLongPoll(vk_session, gid)

            for event in longpoll.listen():
                database.reconnect()

                if event.type == VkBotEventType.MESSAGE_REPLY and 'admin_author_id' in event.obj.keys():
                    importlib.reload(utils)

                    if event.obj.text == 'freeze':
                        utils.deleteMsg(event.obj.id)
                        database.freeze(event.obj.peer_id,'w')
                        utils.sendMessage(event.obj.peer_id, commands.getServiceNotice('freeze'), keyboard=getattr(utils.Keyboard(),'empty')())
                    if event.obj.text == 'unfreeze':
                        utils.deleteMsg(event.obj.conversation_message_id)
                        threading.Thread(target=database.freeze,args=(event.obj.peer_id,'d')).start()
                        utils.sendMessage(event.obj.peer_id, commands.getServiceNotice('ready'), keyboard=getattr(utils.Keyboard(),'main')())
                    continue

                if event.type == VkBotEventType.MESSAGE_NEW:
                    importlib.reload(chat_bot)

                    event = event.obj.message

                    if database.scan_user(event['from_id']):
                        continue

                    if utils.freeze(event['from_id'], 'r'):
                        utils.sendMessage(event['from_id'], commands.getServiceNotice('wait'))
                        continue

                    threading.Thread(target=bot.processing, args=(event, database)).start()
                    continue
        except:
            utils.sendMessage(me, traceback.format_exc())
            continue