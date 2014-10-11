import praw, time, urlparse, requests

str_suffix    = '''**[Citation Needed]**

*I am a bot. For questions, please contact /u/slickytail*'''
max_comments  = 250
sleeptime     = 50
subreddits    = ['askreddit','dataisbeautiful','gaming','news','pics','science','technology']
terms         = ['studies show', 'study shows', 'research shows', 'data shows']
username      = 'citation-is-needed'
password      = raw_input('Enter the password for account ' + username + ' : ')
agent         = 'Silly Citing Bot - Maintained by /u/slickytail'
cachefile     = open('cachedposts.txt','a+')
queue         = []
r             = praw.Reddit(agent)

def main():
    print 'Cite your posts! by /u/slickytail'
    print 'Logging in to Reddit...'
    r.login(username, password)
    print 'Succesfully logged into reddit!'
    print '\n'

    checkmail()

    cachelist = cachefile.read().splitlines()
    if str(subreddits[0]) != 'all':
        combined_subs = ('%s') % '+'.join(subreddits)
        print('Looking at the following subreddits: "' + combined_subs + '".')
    else:
        comments = praw.helpers.comment_stream(r, 'all', limit=None)
        print('Looking at r/all.')

    running = True
    while running:
        try:
            if str(subreddits[0]) != 'all':
                    subs = r.get_subreddit(combined_subs)
                    comments = subs.get_comments(limit=None)
            for comment in comments:
                comment_body = comment.body.encode('utf-8')
                if not comment.id in cachelist:
                    if check_if_all(comment_body):
                        print 'Found a comment!'
                        print comment_body
                        print '-' * 25
                        print '\n'
                        queue.append(comment.permalink)
                cachelist.append(comment.id)
        except Exception as e:
                print 'ERROR:', e
                print 'Stopping Gracefully.'
                running = False
        print 'Found ', len(queue), ' comments.'

        if not cachelist == []:
            write_to_cachefile(cachelist)
        if not queue == []:
            for _ in queue:
                reply_to_queue()
            time.sleep(30)
    cachefile.close()
    print 'Cachefile closed. Exiting...'


def write_to_cachefile(cachedlist):
    cachefile.seek(0,0)
    cachefile.truncate()
    for postid in cachedlist:
        cachefile.write("\n")
        cachefile.write(postid)

def reply_to_queue():

    try:
        comment = r.get_submission(url=queue[0]).comments[0]
        comment.reply(str_suffix)
        print 'Successfully replied to a comment!'
        print comment.body.encode('utf-8')[:30] + '...'
    except praw.errors.RateLimitExceeded as e:
        print 'Error: Rate limit exceeded.'
        print e
    except Exception as e:
        print e
        queue.pop(0)
    else:
        queue.pop(0)

def check_if_valid(text):
    for term in terms:
        if term in text.lower():
            return True
    return False

def check_if_link(strig):
    if not urlparse.urlparse(extract_link(strig)).scheme == '':
        return True
    return False

def extract_link(body):
    for word in body.replace('(',' ').replace(')',' ').split():
        if 'http' in word:
            return word
    return ''

def exists(path):
    try:
        z = requests.head(path)
    except Exception as e:
        print str(e)
        return False
    else:
        return z.status_code < 400

def check_if_all(comment_body):
    v = check_if_valid(comment_body)
    if not v: return False
    l = check_if_link(comment_body)
    t = False
    if l: t = exists(extract_link(comment_body))
    if (v and not l): return True
    return v and l and not t

def checkmail():
    mail = False
    for _ in r.get_unread(limit=None):
        mail = True
    if mail:
        print 'You have new mail!'
if __name__ == '__main__':
    main()
