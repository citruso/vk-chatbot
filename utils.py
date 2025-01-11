# -*- coding: utf-8 -*-

from settings import access_token, access_key, headers, cookies, frozen_users, lang, gid, me, v
from vk_api.keyboard import VkKeyboard
from vk_api.upload import VkUpload
from lxml import html
import mysql.connector
import traceback
import requests
import commands
import urllib
import random
import vk_api
import json
import time
import os
import vk

vk_session = vk_api.VkApi(token=access_key)
api = vk.API(vk.Session(access_token=access_key), v=v, lang=lang)

def freeze(user_id, mode, sec=2):
    if mode == 'r':
        return True if user_id in frozen_users else False
    if mode == 'w':
        frozen_users.append(user_id)
    if mode == 'd':
        time.sleep(sec)
        frozen_users.remove(user_id)

def markUser(target):
    api.messages.markAsImportantConversation(peer_id=target, important=1)

def sendMessage(user_id='', message='', **kwargs):
    api.messages.send(user_id=user_id, message=message, random_id=get_random_id(), **kwargs)

def deleteMsg(message_ids):
    api.messages.delete(message_ids=message_ids, group_id=gid, delete_for_all=1)

def mailingToAll(message):
    count = api.messages.getConversations(count=1, group_id=gid)['count']

    for offset in range(0, count, 100):
        items = api.messages.getConversations(count=100, offset=offset, group_id=gid)['items']
        user_ids = [x['conversation']['peer']['id'] for x in items]
        sendMessage(user_ids=user_ids, message=message)
        time.sleep(0.5)

def uploadMessagePhoto(filename):
    upload = VkUpload(vk_session)
    res = upload.photo_messages(filename)[0]
    return 'photo{}_{}_{}'.format(res['owner_id'], res['id'], res['access_key'])

def uploadMessageDocument(filename, name, user_id):
    upload = VkUpload(vk_session)
    res = upload.document_message(filename, name, peer_id=user_id)['doc']
    return 'doc{}_{}'.format(res['owner_id'], res['id'])

def downloadFile(url, ext):
    filename = '/temp/file.{}'.format(ext)
    headers = urllib.request.build_opener()
    headers.addheaders = headers
    urllib.request.install_opener(headers)
    urllib.request.urlretrieve(url, filename)
    return filename

def getFirstName(user_id):
    return api.users.get(user_ids=user_id)[0]['first_name']

def getMessageCount(user_id):
    return api.messages.getHistory(user_id=user_id, count=1, offset=0, start_message_id=-1)['count']

def getLastMessageTime(msg_id):
    return api.messages.getById(message_ids=msg_id, preview_length=1)['items'][0]['date']

def get_random_id():
    random = random.SystemRandom()
    return random.getrandbits(64) * random.choice([-1, 1])

def getRandomArt():
    random = random.SystemRandom()
    data = dict(
        owner_id = '-' + gid,
        album_id = 'wall',
        count = 1,
        offset = random.randint(0, 680),
        rev = random.randint(0,1),
        access_token = access_token,
        v = v
    )
    res = requests.post('https://api.vk.com/method/photos.get?', data)
    item = json.loads(res.text)['response']['items'][0]
    return 'photo{}_{}'.format(item['owner_id'], item['id'])

def getRandomAnime():
    try:
        url = 'https://animevost.club/random'
        page = requests.session().get(url, headers=headers, cookies=cookies)
        tree = html.fromstring(page.content)
        name = tree.xpath('//*[@id="content"]/div[1]/div[1]/a/h2/text()')[0]
        link = tree.xpath('//*[@id="content"]/div[1]/div[2]/div[1]/img/@src')[0]
        link = url.replace('/random','') + link.replace(os.path.basename(link),os.path.basename(link).replace('s',''))
    except:
        sendMessage(me, traceback.format_exc())

    return name, uploadMessagePhoto(downloadFile(link,'jpg'))

def getRandomGif(user_id):
    data = dict(key='', q='', limit=1)
    response = requests.get('https://api.tenor.com/v1/random?key={key}&q={q}&limit={limit}'.format(**data))
    result = json.loads(response.text)['results'][0]
    url, name = result['media'][0]['mediumgif']['url'], result['itemurl'].split('/')[-1]
    return uploadMessageDocument(downloadFile(url,'gif'), name, user_id)

def detectImage(url):
    response = requests.get('https://yandex.ru/images/search?rpt=imageview&url='+url, headers=headers, cookies=cookies)
    tree = html.fromstring(response.content)
    items = tree.xpath('//div[@class="tags__wrapper"]/a/text()')
    return items if items else ''

# ------------------------------------------

class Database(object):
    def __init__(self, db):
        self.connection = mysql.connector.MySQLConnection(
            user='',
            password='',
            host='',
            database=db
        )
        self.cursor = self.connection.cursor(buffered=True)

    def request_sql(self, command):
        self.cursor.execute(command)
        self.connection.commit()

        if 'select' in command:
            try:
                return self.cursor.fetchall()
            except:
                sendMessage(me, traceback.format_exc())
                return

class VkUsers(Database):
    def __init__(self):
        super().__init__('vk_users')

    def scan_user(self, user_id):
        user = super().request_sql('select * from users where user_id={};'.format(user_id))

        if not user:
            super().request_sql('insert into users (user_id, manually) values ({}, 0);'.format(user_id))
            return False
        else:
            return True if bool(user[0][1]) else False

    def delete_user(self, user_id):
        super().request_sql('delete from users where user_id={}'.format(user_id))

    def get_modal(self, user_id):
        return super().request_sql('select modal from users where user_id={};'.format(user_id))[0][0]

    def set_modal(self, user_id, modal):
        super().request_sql('update users set modal="{}" where user_id={};'.format(modal, user_id))

    def freeze(self, user_id, mode):
        if mode == 'w':
            super().request_sql('update users set manually=1 where user_id={};'.format(user_id))
        if mode == 'd':
            super().request_sql('update users set manually=0 where user_id={};'.format(user_id))

class PostsHistory(Database):
    def __init__(self):
        super().__init__('posts_history')

    def get_pagination_history(self):
        return super().request_sql('select * from pagination;')

    def set_pagination_history(self,page,elem):
        super().request_sql('update pagination set page={}, element={};'.format(page, elem))

    def get_posts_history(self,post):
        return super().request_sql('select * from history where post={};'.format(post))

    def set_posts_history(self,post):
        super().request_sql('insert into history values ({});'.format(post))

class Keyboard(object):
    def __init__(self, one_time=False, inline=False):
        self.keyboard = VkKeyboard(one_time=one_time, inline=inline)

    def empty(self):
        return self.keyboard.get_empty_keyboard()

    def main(self):
        self.keyboard.add_button('&#127912; Арт', color='primary', payload='{"command":"art"}')
        self.keyboard.add_button('&#10024; Гифка', color='primary', payload='{"command":"gif"}')
        self.keyboard.add_line()
        self.keyboard.add_button('&#128064; Случайное аниме', color='primary', payload='{"command":"anime"}')
        self.keyboard.add_button('&#128373; Угадай', color='primary', payload='{"command":"detect"}')
        return self.keyboard.get_keyboard()

    def detect(self):
        self.keyboard.add_button('Отмена', color='negative', payload='{"command":"cancel"}')
        return self.keyboard.get_keyboard()

class Modal(object):
    def detect(self, attachments):
        message = 'Кажется, на картинке: \n'
        keyboard = getattr(Keyboard(),'detect')()
        done = False

        if len(attachments) == 1:
            if attachments[0]['type'] == 'photo':
                url = attachments[0]['photo']['sizes'][-1]['url']
                response = detectImage(url)

                if len(response) != 0:
                    message += response
                else:
                    message = commands.getServiceNotice('notDetected')

                keyboard = getattr(Keyboard(),'main')()
                done = True
            else:
                message = commands.getServiceNotice('wrongType').format(attachments[0]['type'])
        elif len(attachments) > 1:
            message = commands.getServiceNotice('manyFiles')
        else:
            message = commands.getServiceNotice('emptyAttachments')

        return message, keyboard, done
# ------------------------------------------