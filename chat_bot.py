from settings import me
import importlib
import traceback
import threading
import commands
import utils

database = utils.VkUsers()

def processing(event):
    importlib.reload(commands)
    importlib.reload(utils)

    if database.scan_user(event['from_id']):
        return

    try:
        user_id = event['from_id']
        message_id = event['conversation_message_id']
        text = event['text']
        attachments = event['attachments']
        payload = event.get('payload')
        modal = database.get_modal(user_id)

        utils.freeze(user_id, 'w')

        if modal == 'detect' and payload is None:
            data = dict(user_id=user_id)
            data['message'], data['keyboard'], done = utils.Modal().detect(attachments)
            if done: database.set_modal(user_id, None)
            utils.sendMessage(**data)
            threading.Thread(target=utils.freeze,args=(user_id, 'd')).start()
            return

        if len(attachments) != 0:
            if 'type' in attachments[0].keys() and 'market' in attachments[0].values():
                text = 'товар'

        if not '# ' in text:
            message, option = commands.create_answer(text, payload)
        else:
            message, option = '', ''

        if '# ' in text and str(user_id) == me:
            info = eval(text.split('# ')[1])
            message = commands.getServiceNotice('complete') + str(info)

        if option == 'start' or message_id == 0:
            message = message.format(utils.getFirstName(user_id))

        if option == 'notResponse':
            threading.Thread(target=utils.freeze,args=(user_id, 'd')).start()
            return

        #--------
        data = dict(user_id=user_id, keyboard=getattr(utils.Keyboard(),'main')())
        #--------

        if type(message) is str:
            data['message'] = message
        else:
            data['sticker_id'] = message

        if option == 'main' or option == 'cancel':
            data['keyboard'] = getattr(utils.Keyboard(), 'main')()

        if option == 'ads':
            utils.markUser(user_id)
            utils.sendMessage(me, commands.getServiceNotice(option).format(user_id))
            database.freeze(user_id,'w')
            data['keyboard'] = getattr(utils.Keyboard(), 'empty')()

        if option == 'art':
            data['attachment'] = utils.getRandomArt()

        if option == 'anime':
            data['message'], data['attachment'] = utils.getRandomAnime00()

        if option == 'gif':
            data['attachment'] = utils.getRandomGif00(user_id)

        if option == 'detect':
            database.set_modal(user_id, 'detect')
            data['keyboard'] = getattr(utils.Keyboard(), option)()

        utils.sendMessage(**data)

        if option != 'ads':
            threading.Thread(target=utils.freeze,args=(user_id, 'd')).start()

    except:
        utils.sendMessage(user_id, commands.getServiceNotice('exception'), keyboard=getattr(utils.Keyboard(),'main')())
        utils.sendMessage(me, traceback.format_exc())
        database.set_modal(user_id, 'NULL')
        utils.freeze(user_id, 'd')
        return