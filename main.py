import praw
import re
import time

import local_config as config
from mongoengine import *
from datetime import datetime

class Submission(Document):
    i = StringField()
    u = StringField()
    t = StringField()
    s = StringField()
    d = DateTimeField()

def strip_utf8(str):
    return ''.join([x if ord(x) < 128 else "" for x in str])

connect('mcservers')

r = praw.Reddit(user_agent="mcservers-bot")

r.login(config.USERNAME, config.PASSWORD)

moderators = [x.name for x in r.get_subreddit('mcservers').get_moderators()]
already_done = []

for object in Submission.objects():
    already_done.append(object.i)

print (already_done)
while True:
    try: 
        for post in r.get_subreddit(config.SUBREDDIT).get_new(limit=5):
            if post.id in already_done:
                continue
            if post.author.name in moderators:
                continue


            tags = re.findall(r'\[([\w+\-]+)\]', post.title)

            comment = 'Your submission has been removed because:'

            #Remove posts with invalid tags
            for tag in tags:
                if not tag.lower() in config.APPROVED_TAGLIST:
                    comment += '\n\n- your title has incorrect primary tags. Please read our [rules](http://www.reddit.com/r/mcservers/wiki/index) and create a new post with [valid primary tags](http://www.reddit.com/r/mcservers/wiki/index#wiki_.5Btags.5D_.26_.7Bbrackets.7D)'
                    break

            #Remove posts with no tags
            if len(tags) == 0:
                comment += '\n\n- it does not have any primary tags. Please read our [rules](http://www.reddit.com/r/mcservers/wiki/index) and create a new post with [valid primary tags](http://www.reddit.com/r/mcservers/wiki/index#wiki_.5Btags.5D_.26_.7Bbrackets.7D)'

            #Remove posts with <350 body
            if post.selftext and len(post.selftext) < 350:
                comment += '\n\n- your post is shorter than 350 characters. Typically, this means that your post does not conform to our [description formatting](http://www.reddit.com/r/mcservers/wiki/index#wiki_description_example). Please reformat your post and [send the moderators a message](http://www.reddit.com/message/compose?to=%2Fr%2Fmcservers&subject=Spam+Filter&message=Please%20put%20link%20to%20post%20here:%0A%0AName%20of%20your%20server:%0A%0AAdditional%20comments:) to have them look over the post and approve it.'

            #Nuke offline servers
            offline = ['offline', 'cracked', 'hamachi']
            if any(word in post.title.lower() for word in offline) or any (word in post.selftext.lower() for word in offline):
                comment += '\n\n- Hamachi, Cracked, Offline, or test servers are not allowed here here, please post them in [MCTestServers](http://www.reddit.com/r/mctestservers).'

            #nuke 24/7
            tfs = ['24/7', '24x7']
            if any (word in post.title.lower() for word in tfs) or any (word in post.selftext.lower() for word in tfs):
                comment += "\n\n- it is labeled as 24/7. All servers are required to be online 24/7 to be posted to /r/mcservers. Please remove any reference to your server being 24/7 and repost."

            #make sure they have rules
            rules = ['rules', 'racism', 'sexism', 'griefing', 'greifing', 'mature']
            if not any(word in post.selftext.lower() for word in rules) and not '[wanted]' in post.title.lower():
                comment += '\n\n- your server appears to have no rules. Please edit your post to include some rules, then [message the moderators to have your post approved](http://www.reddit.com/message/compose?to=%2Fr%2Fmcservers}).'

            #Remove post if any of above tests passed
            if comment != 'Your submission has been removed because:':
                comment +='\n\n*I am a bot, this action was performed automatically. If you feel this was a mistake, please [message the moderators](http://reddit.com/message/compose?to=/r/mcservers&subject={0})*'.format(post.url)
                c = post.add_comment(comment)
                c.distinguish()
                post.remove()
                print('Post was removed tags: {0} - {1} - {2}'.format(post.id, strip_utf8(post.title), post.url))
            Submission(i=post.id, u=post.author.name, t=post.title, s=post.selftext, d=datetime.utcnow()).save()
            already_done.append(post.id)
        time.sleep(5)
    except Exception as e:
        print (e)
        pass
