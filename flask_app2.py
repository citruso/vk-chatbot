# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request
import vk_api
from vk_api.utils import get_random_id


confirmation_code = ''
secret_key = ''
group_token = ''


app = Flask(__name__)

vk_session = vk_api.VkApi(token=group_token)
vk = vk_session.get_api()


@app.route('/233827550198009856', methods=['POST'])
def callbackPOST():
    data = request.get_json(force=True, silent=True)

    if not data or 'type' not in data:
        return 'not ok'

    if request.headers.get('X-Retry-Counter'):
        return 'ok'

    if data['type'] == 'confirmation':
        return confirmation_code

    if 'secret' in data.keys() and data['secret'] == secret_key:
        event = data['object']['message']

        if data['type'] == 'message_new':
            vk.messages.send(
                message=event['text'],
                random_id=get_random_id(),
                peer_id='331864571'
            )

        if data['type'] == '':
            #Thread(target=,args=()).start()
            pass

        return 'ok'

    return 'ok'

@app.route('/', methods=['GET'])
def callbackGET():
    return 'haha go away'

if __name__ == "__main__":
    app.run(debug=True)
