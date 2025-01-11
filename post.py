from settings import access_token, lang, gid, me, v
from vk_api.upload import VkUpload
import traceback
import datetime
import commands
import vk_api
import utils
import time
import vk

import searchPics

def main(hour):
    filename = None

    try:
        url = searchPics.search(db)
        filename = utils.downloadFile(url, url.split('.')[-1])
    except:
        utils.sendMessage(me, traceback.format_exc())
        exit(1)

    #check.check(filename)

    try:
        response = upload.photo_wall(filename, group_id=gid)[0]

        if hour == -3: # there is a problem with VK Servers
            d = 0
            h = 24
        else:
            d = 1
            h = 0

        shema = '{}-{}-{} {}:00:00'.format(time.strftime('%Y'), time.strftime('%m'), time.strftime('%d'), hour+h)
        date = datetime.datetime.strptime(shema, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days=d)
        publish_date = int(time.mktime(time.strptime(str(date),'%Y-%m-%d %H:%M:%S')))
        data = dict(
            owner_id = '-' + gid,
            attachments = 'photo{}_{}'.format(response['owner_id'], response['id']),
            publish_date = publish_date,
            from_group = 1
        )
        api.wall.post(**data)
    except:
        utils.sendMessage(me, traceback.format_exc())
        utils.sendMessage(me, response)
        exit(1)

if __name__ == '__main__':
    db = utils.PostsHistory()

    upload = VkUpload(vk_api.VkApi(token=access_token))
    api = vk.API(vk.Session(access_token=access_token), v=v, lang=lang)

    for x in range(-3, 21, 3):
        main(x)

    del db

    utils.sendMessage(me, commands.getServiceNotice('posts'))