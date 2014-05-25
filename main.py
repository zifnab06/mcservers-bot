import praw;
import re;
from pprint import pprint
import time
import codecs
import local_config as config
from mongoengine import *
from datetime import datetime

class Submission(Document):
    i = StringField()
    u = StringField()
    t = StringField()
    s = StringField()
    d = DateTimeField()

    meta = {
        'indexes': [
            { 'fields': ['d'], 'expiresAfterSeconds': 1123200}
        ]
    }
def strip_utf8(str):
    return ''.join([x if ord(x) < 128 else "" for x in str])

connect('mcservers')

r = praw.Reddit(user_agent="mcservers-bot")

r.login(config.USERNAME, config.PASSWORD)

#Throw credentials in next line, uncomment
#r.login('user', 'pass')

already_done = []

for object in Submission.objects():
    already_done.append(object.i)

print already_done
while True:
    try: 
        for submission in r.get_subreddit(config.SUBREDDIT).get_new(limit=5):
            if submission.id in already_done:
                continue
            title = submission.title
            tags = re.findall(r'\[([\w+\-]+)\]', title)
            for tag in tags:
                if not tag.lower() in config.APPROVED_TAGLIST:
                    comment = submission.add_comment('Your submission has been removed because your title has incorrect tags. Please read our [rules](http://www.reddit.com/r/mcservers/wiki/index) and create a new post with [valid tags](http://www.reddit.com/r/mcservers/wiki/index#wiki_.5Btags.5D_.26_.7Bbrackets.7D)\n\n*I am a bot, this action was performed automatically. If you feel this was a mistake, please [message the moderators](http://reddit.com/message/compose?to=/r/mcservers)*')
                    comment.distinguish()
                    submission.remove()
                    print 'Post has invalid tags and was removed: {0} - {1} - {2}'.format(submission.id, strip_utf8(submission.title), submission.url)
                    break
            Submission(i=submission.id, u=submission.author.name, t=submission.title, s=submission.selftext, d=datetime.utcnow()).save()
            already_done.append(submission.id)
#        print 'Post has valid tags: {0} - {1} - {2}'.format(submission.id, submission.title, submission.url)
        time.sleep(5)
    except:
        pass
