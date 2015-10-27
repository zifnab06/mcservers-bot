import praw
import yaml
import time
import re
import slack
import slack.chat

import local_config as config
from mongoengine import *
from datetime import datetime

class Submission(Document):
    i = StringField() #id
    u = StringField() #user
    t = StringField() #title
    s = StringField() #selftext
    d = DateTimeField() #date
    r = BooleanField() #removed (by bot)

def strip_utf8(str):
    '''Used for removing utf8 characters - fixes errors in py2.7 for slack/mongo'''
    return ''.join([x if ord(x) < 128 else "" for x in str])

connect('mcservers')

slack.api_token = config.SLACK_API_TOKEN

r = praw.Reddit(user_agent=u"/u/mcservers-bot v1.1")

r.login(config.USERNAME, config.PASSWORD)

moderators = [x.name for x in r.get_subreddit('mcservers').get_moderators()]
slack.chat.post_message(u'#bot-log', u'Bot Started', username=config.USERNAME)

#needs to be moved to a wiki config
with open('reasons.yml') as f:
    reasons = yaml.load(f.read())

print(u'{0} posts in database'.format(len(Submission.objects())))

#Main loop. Loop forever, do things in a try/catch for when reddit dies. 
while True:
    try: 
        for post in r.get_subreddit(config.SUBREDDIT).get_new(limit=10):
            #TODO: claen this up. already_done used to contain a list of all posts, but bot was using 100% mem after a year
            already_done = Submission.objects(i=post.id).first()
            if already_done is not None:
                continue
            chat_message = u'{0} - {1} \n user: {2}'.format(post.title, post.url, post.author.name)
            slack.chat.post_message(u'#mcservers-feed', chat_message, username=config.USERNAME)


            #Tag check. Find everything within square braces
            tags = re.findall(r'\[(.*?)\]', post.title)

            #List of removal reasons
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
            if post.selftext and len(post.selftext) < 350:
                remove.append(reasons['shorttext'])

            #nuke 24/7
            tfs = ['24/7', '24x7']
            if any (word in post.title.lower() for word in tfs) or any (word in post.selftext.lower() for word in tfs):
                remove.append(reasons['24x7'])

            #make sure they have rules
            rules = ['rules', 'racism', 'sexism', 'griefing', 'greifing']
            if not any(word in post.selftext.lower() for word in rules) and not '[wanted]' in post.title.lower():
                remove.append(reasons['rules'])


            #Remove posts with only wanted tag (require at least one other tag)
            if len(tags) == 1 and tags[0].lower() == 'wanted':
                remove.append(reasons['wantednotags'])


            #Remove posts that ask for donations
            donations = ['donate', 'donation']
            if any(word in post.selftext.lower() for word in donations):
                remove.append(reasons['donate'])

            #NEVER remove mod posts
            if post.author.name in moderators:
                remove = False

            #Remove post if any of above tests passed
            if remove:
                remove.append(reasons['append'].format(post.url))
                comment = u'Your post has been removed because:\n\n' + u'\n\n'.join(remove)
                c = post.add_comment(comment)
                c.distinguish()
                post.remove()
                remove_message = u'Post was removed: {0} - {1} - {2}'.format(post.id, strip_utf8(post.title), post.url)
                print remove_message
                slack.chat.post_message(u'#bot-log', remove_message, username=config.USERNAME)
                slack.chat.post_message(u'#mcservers-feed', remove_message, username=config.USERNAME)

            Submission(i=post.id, u=post.author.name, t=post.title, s=post.selftext, d=datetime.utcnow(), r=bool(remove)).save()
        #Sleep for 30 seconds, current max rate being 10 posts / 30 seconds
        time.sleep(30)

    except Exception as e:
        '''We do nothing on an error but print the error - keeps bot from dying when reddit goes down'''
        print (e)
        pass
