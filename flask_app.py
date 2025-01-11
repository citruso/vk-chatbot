# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, json
from settings import secret_key
import commands
import utils
import bot

app = Flask(__name__)

@app.route('/', methods=['POST'])
def receiving():
    data = json.loads(request.data)
    if 'secret' in data.keys() and data['secret'] == secret_key:
        if data['type'] == 'message_reply' and 'admin_author_id' in data['object'].keys():
            event = data['object']
            database = utils.VkUsers()

            if event['text'] == 'freeze':
                utils.deleteMsg(event['id'])
                database.freeze(event['peer_id'], 'w')
                utils.sendMessage(event['peer_id'], commands.getServiceNotice('freeze'), keyboard=getattr(utils.Keyboard(),'empty')())
            if event['text'] == 'unfreeze':
                utils.deleteMsg(event['id'])
                database.freeze(event['peer_id'],'d')
                utils.sendMessage(event['peer_id'], commands.getServiceNotice('ready'), keyboard=getattr(utils.Keyboard(),'main')())

        if data['type'] == 'message_new':
            bot.processing(data['object']['message'])
    return 'ok'

if __name__ == '__main__':
    app.run()
