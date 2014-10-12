import praw, time, urlparse, requests

## Config section

str_suffix    = '''>%s

**[Citation Needed]**

*^I ^am ^a ^bot. ^For ^questions, ^please ^contact ^/u/slickytail*'''
max_comments  = 500
sleeptime     = 50
subreddits    = ['askreddit','gaming','news','technology', 'botwatch']
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

    ## Code from /u/NetflixBot - Establish a subreddit object

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
            
            ## Also from /u/NetflixBot - Update subreddit object
            if str(subreddits[0]) != 'all':
                    subs = r.get_subreddit(combined_subs)
                    comments = subs.get_comments(limit=None)
            for comment in comments:
                comment_body = comment.body.encode('utf-8')
                ## Determine if a comment should be replied to
                if not comment.id in cachelist:
                    if check_if_all(comment_body) and str(comment.author).lower() != username.lower():
                        
                        ## Print a comment if one is found and add it to the queue
                        print 'Found a comment!'
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
    cachefile.close()
    print 'Exiting...'


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
        for sentence in comment.body.encode('utf-8').split('.'):
            if check_if_valid(sentence):
                st = sentence
            
        replyto = str_suffix % (st)
        comment.reply(replyto)
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

## Function that checks if a comment contains a keyword
def check_if_valid(text):
    for term in terms:
        if term in text.lower():
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
        z = requests.head(path)
    except Exception as e:
        print str(e)
        return False
    else:
        return not 400 < z.status_code < 500

## Does most of the logic for comment parsing
def check_if_all(comment_body):
    v = check_if_valid(comment_body)
    if not v: return False
    l = check_if_link(comment_body)
    t = False
    if l: t = exists(extract_link(comment_body))
    if (v and not l): return True
    return v and l and not t

## Self explanitory - checks mail
def checkmail():
    mail = False
    for _ in r.get_unread(limit=None):
        mail = True
    if mail:
        print 'You have new mail!'


if __name__ == '__main__':
    main()
