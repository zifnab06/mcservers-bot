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
    r = BooleanField()

connect('mcservers')

stats=dict(tags=0, notags=0, length=0, offline=0, tfs=0, rules=0, removed=0)

for submission in Submission.objects():
    
    tags = re.findall(r'\[(.*?)\]', submission.t)

    comment = 'Your submission has been removed because:'


    #Remove posts with invalid tags
    for tag in tags:
        if not tag.lower() in config.APPROVED_TAGLIST:
            stats['tags']+=1
            break

    #Remove posts with no tags
    if len(tags) == 0:
        stats['notags']+=1
    #Remove posts with <350 body
    if submission.s and len(submission.s) < 350:
        stats['length']+=1

    #Nuke offline servers
    offline = ['offline', 'cracked', 'hamachi']
    if any(word in submission.t.lower() for word in offline) or any (word in submission.s.lower() for word in offline):
        stats['offline']+=1

    #nuke 24/7
    tfs = ['24/7', '24x7']
    if any (word in submission.t.lower() for word in tfs) or any (word in submission.s.lower() for word in tfs):
        stats['tfs']+=1

    #make sure they have rules
    rules = ['rules', 'racism', 'sexism', 'griefing', 'greifing', 'mature']
    if not any(word in submission.s.lower() for word in rules) and not '[wanted]' in submission.t.lower():
        stats['rules']+=1

stats['removed'] = len(Submission.objects(r=True))

print stats
