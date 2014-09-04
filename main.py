import praw
import yaml
import time
import re

import local_config as config
from mongoengine import *
from datetime import datetime

class Submission(Document):
    i = StringField()
    u = StringField()
    t = StringField()
    s = StringField()
    d = DateTimeField()
    r = BooleanField()

def strip_utf8(str):
    return ''.join([x if ord(x) < 128 else "" for x in str])

connect('mcservers')

r = praw.Reddit(user_agent="mcservers-bot")

r.login(config.USERNAME, config.PASSWORD)

moderators = [x.name for x in r.get_subreddit('mcservers').get_moderators()]
already_done = []

for object in Submission.objects():
    already_done.append(object.i)

print ('Posts imported: {0}'.format(len(already_done)))

with open('reasons.yml') as f:
    reasons = yaml.load(f.read())
from pprint import pprint
pprint(reasons)

while True:
    try: 
        for post in r.get_subreddit(config.SUBREDDIT).get_new(limit=5):
            if post.id in already_done:
                continue
            #if post.author.name in moderators:
            #    continue


            tags = re.findall(r'\[(.*?)\]', post.title)

            remove = []
            bad_tags = []
            #Remove posts with invalid tags
            for tag in tags:
                if not tag.lower() in config.APPROVED_TAGLIST:
                    bad_tags.append(tag)

            for bad_tag in bad_tags:
                remove.append(reasons['badtag'].format(bad_tag))

            #Remove posts with no tags
            if len(tags) == 0:
                remove.append(reasons['notags'])

            #Remove posts with <350 body
            if post.selftext and len(post.selftext) < 250:
                remove.append(reasons['shorttext'])

            #Nuke offline servers
            offline = ['offline', 'cracked', 'hamachi']
            if any(word in post.title.lower() for word in offline) or any (word in post.selftext.lower() for word in offline):
                remove.append(reasons['offline'])

            #nuke 24/7
            tfs = ['24/7', '24x7']
            if any (word in post.title.lower() for word in tfs) or any (word in post.selftext.lower() for word in tfs):
                remove.append(reasons['24x7'])

            #make sure they have rules
            rules = ['rules', 'racism', 'sexism', 'griefing', 'greifing', 'mature']
            if not any(word in post.selftext.lower() for word in rules) and not '[wanted]' in post.title.lower():
                remove.append(reasons['rules'])


            #Remove posts with only wanted tag
            if len(tags) == 1 and tags[0].lower() == 'wanted':
                remove.append(reasons['wantednotags'])


            #Remove posts that ask for donations
            donations = ['donate', 'donation']
            if any(word in post.selftext.lower() for word in donations):
                remove.append(reasons['donate'])

            #Remove post if any of above tests passed
            if remove:
                remove.append(reasons['append'].format(post.url))
                comment = 'Your post has been removed because:\n\n' + '\n\n'.join(remove)
                c = post.add_comment(comment)
                c.distinguish()
                post.remove()
                print('Post was removed: {0} - {1} - {2}'.format(post.id, strip_utf8(post.title), post.url))
            Submission(i=post.id, u=post.author.name, t=post.title, s=post.selftext, d=datetime.utcnow(), r=bool(remove)).save()
            already_done.append(post.id)
        time.sleep(5)
    except Exception as e:
        print (e)
        pass
