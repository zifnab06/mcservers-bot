import praw;
import re;
from pprint import pprint
import time
import codecs


def strip_utf8(str):
    return ''.join([x if ord(x) < 128 else "" for x in str])

r = praw.Reddit(user_agent="zifnab06_test_bot")
already_done = []

with codecs.open('listing.txt', 'r', 'utf-8-sig') as file:
    for line in file:
        already_done.append(line[:6])

print already_done


with codecs.open('listing.txt', 'a', 'utf-8-sig') as file:
    while True:
        for submission in r.get_subreddit('mcservers').get_new(limit=10):
            if submission.id in already_done:
                continue
#            pprint(vars(submission))
            print (submission.id, submission.title, submission.url, str(submission.author))
            file.write(u'%s %s - %s\n' % (submission.id, strip_utf8(submission.title), submission.url))
            already_done.append(submission.id)
        time.sleep(30)


