from settings import me
from lxml import html
import traceback
import requests
import utils

url = 'https://danbooru.donmai.us/posts?page={}&tags={}'
tag = ''
min_score = 5

ban = [
]

def search(db):
    try:
        tags = []
        page,elem = db.get_pagination_history()[0]

        for _ in range(10):
            webpage = requests.get(url.format(page, tag))
            tree = html.fromstring(webpage.content)
            items = len(tree.xpath('//article'))+1

            for x in range(elem, items):
                post = int(tree.xpath('//article[{}]/@id'.format(x))[0].split('_')[1])
                tags = tree.xpath('//article[{}]/@data-tags'.format(x))[0].split(' ')
                score = int(tree.xpath('//article[{}]/@data-score'.format(x))[0])

                if (len(set(tags) & set(ban)) != 0) or (score < min_score) or (post in [x[0] for x in db.get_posts_history(post)]):
                    tags = []
                    continue
                else:
                    db.set_posts_history(post)
                    break
            else:
                page += 1
                elem = 1
                continue
            break

        db.set_pagination_history(page, elem+1)

        return tree.xpath('//article[{}]/@data-file-url'.format(x))[0]
    except:
        utils.sendMessage(me, traceback.format_exc())
        exit(1)