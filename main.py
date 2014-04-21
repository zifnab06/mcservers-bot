import praw;
import re;
from pprint import pprint
import time

approved_taglist = ['vanilla', 'semi-vanilla', 'smp', 'pve', 'pvp', 'creative', 'anarchy', 'chaos', 'hardcore', 'tekkit', 'ftb', 'adventure', 'hub', 'minigames']

r = praw.Reddit(user_agent="zifnab06_test_bot")

already_done = []
while True:
    for submission in r.get_subreddit('mcservers').get_new(limit=5):
        if submission.id in already_done:
            continue
        #pprint(vars(submission))
        if submission.approved_by:
            continue
        title = submission.title
        tags = re.findall(r'\[([\w+\-]+)\]', title)
        for tag in tags:
            if not tag.lower() in approved_taglist:
                print 'INVALID - TAGS'
        print (submission.title, submission.url)
        already_done.append(submission.id)
    time.sleep(45)
