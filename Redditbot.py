import praw, time, urlparse, requests, string, re, ConfigParser

## Config section

str_suffix    = '''>%s.

**[Citation Needed]**

*^I ^am ^a ^bot. ^For ^questions ^or ^comments, ^please ^contact ^/u/slickytail*'''

filetemplate  = '''[Configuration]
Username = username
Password = password'''
try:
    open('config.cfg','r+').close()
except:
    filething = open('config.cfg','w+')
    filething.write(filetemplate)
    filething.close()
config = ConfigParser.ConfigParser()
config.read('config.cfg')
username  = config.get('Configuration', 'Username')
password  = config.get('Configuration', 'Password')

max_comments  = 750
sleeptime     = 50
subreddits    = ['all']
terms         = ['studies show', 'study shows', 'research shows', 'data shows']
agent         = 'Silly Citing Bot - Maintained by /u/slickytail'
mode          = 'ping'  ## Mode is ping or stream
blacklist     = ['askreddit','pics']

cachefile     = open('cachedposts.txt','a+')
queue         = []
r             = praw.Reddit(agent)



def main():
    print 'Cite your posts! by /u/slickytail'
    print 'Logging in to Reddit...'
    r.login(username, password)
    print 'Succesfully logged into reddit! \n'

    checkmail()


    cachelist = cachefile.read().splitlines()
    del cachelist[:-1000]
    combined_subs = ('%s') % '+'.join(subreddits)
    if mode == 'ping':
        print 'Looking at the following subreddits: "' + combined_subs + '".'
    else:
        comments = praw.helpers.comment_stream(r, 'all', limit=None)
        print 'Looking at a stream of the following subreddits: "' + combined_subs + '".' 

    running = True
    while running:
        try:

            if mode == 'ping':
                    subs = r.get_subreddit(combined_subs)
                    comments = subs.get_comments(limit=None)
            for comment in comments:
                comment_body = comment.body.encode('utf-8')
                ## Determine if a comment should be replied to
                if comment.subreddit.display_name.lower() not in blacklist:
                    if str(comment.author).lower() != username.lower():
                        if comment.id not in cachelist:
                            if check_if_all(comment_body):
                            
                                ## Print a comment if one is found and add it to the queue
                                print 'Found a comment in /r/%s' % (comment.subreddit.display_name.lower())
                                print '-' * 25
                                print comment_body
                                print '-' * 25
                                print '\n'
                                queue.append(comment.permalink)
                            cachelist.append(comment.id)
                
        ## Allows the program to reply to comments and write to the cachefile when it stops
        except Exception as e:
                print 'ERROR:', e
                print 'Stopping Gracefully.'
                running = False


        ## Write to the cachefile and reply to comments in the queue
        write_to_cachefile(cachelist)
        if not queue == []:
            print 'Replying to', len(queue), 'comments.'
            for _ in queue:
                reply_to_queue()
                time.sleep(30)
                
    ## Perform a final cachewrite and reply to any remaining comments
    write_to_cachefile(cachelist)
    if not queue == []:
        print 'Replying to', len(queue), 'comments.'
        for _ in queue:
            reply_to_queue()
            time.sleep(30)

    ## Close the cachefile and exit the program


## Function that erases the cachefile (safe because cachedlist is a copy of the cachefile) and rewrite it
def write_to_cachefile(cachedlist):
    cachefile.seek(0,0)
    cachefile.truncate()
    for postid in cachedlist:
        cachefile.write(postid)
        cachefile.write("\n")


## Function that takes the first comment from the queue, and replies to it
def reply_to_queue():
    try:
        comment = r.get_submission(url=queue[0]).comments[0]

        ## Find the sentence that contains the phrase
        for sentence in re.split('[?.!:"]', comment.body.encode('utf-8')):
            if check_if_valid(sentence):
                st = sentence
            
        replyto = str_suffix % (st)
        comment.reply(replyto)
        print 'Successfully replied to a comment!'
        print st[:50] + '...'
        print '-' * 25
        print '\n'
    except praw.errors.RateLimitExceeded as e:
        print 'Error: Rate limit exceeded.'
        print e
    except Exception as e:
        print e
        queue.pop(0)
    else:
        queue.pop(0)

## Function that checks if a comment contains a keyword
def check_if_valid(text):
    text = text.lower( )
    for line in text.splitlines( ):
        if line == '': return False
        elif line[0] == '>' or line[0] == '"': return False
        else:
            for term in terms:
                if term in line:
                    return True
    return False

## Function that uses urlparse to detect a proper link
def check_if_link(strig):
    if not urlparse.urlparse(extract_link(strig)).scheme == '':
        return True
    return False
                                                                            ## These two functions should be rewritten
## Function that extracts a link from a body of text
def extract_link(body):
    for word in body.replace('(',' ').replace(')',' ').split():
        if 'http' in word:
            if not urlparse.urlparse(word).scheme == '':
                return word
    return ''

## Function that visits a web url to determine if it exists
def exists(path):
    try:
        z = requests.head(path).status_code
    except Exception as e:
        print str(e)
        return False
    if z == 405:
        return True
    else:
        return not 400 < z < 500


## Does most of the logic for comment parsing
def check_if_all(comment_body):
    v = check_if_valid(comment_body)
    if not v: return False
    l = check_if_link(comment_body)
    t = False
    if l: t = exists(extract_link(comment_body))
    if (v and not l): return True
    return v and l and not t

## Self explanatory - checks mail
def checkmail():
    mail = False
    for _ in r.get_unread(limit=1):
        mail = True
    if mail:
        print 'You have new mail!'


if __name__ == '__main__':
    while True:
        main()
        time.sleep(10)
    

cachefile.close()
print 'Exiting...'
