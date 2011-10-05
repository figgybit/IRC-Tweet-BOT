import tweepy
import Queue

import logging
import re
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers

##CUSTOMIZE_THIS_START
HOST = 'irc.freenode.net'
PORT = 6667
NICK = 'YOUR_NICK_NAME'
CHANNEL = '#CHANNEL_NAME'
##CUSTOMIZE_THIS_END

class StreamWatcherListener(tweepy.StreamListener):

    def __init__(self, status_queue):
        super( StreamWatcherListener, self ).__init__()
        self.status_queue = status_queue

    def on_status(self, status):
        try:
            print 'new tweet'
            print status.text
            self.status_queue.put(status)
        except:
            # Catch any unicode errors while printing to console
            # and just ignore them to avoid breaking application.
            pass

    def on_error(self, status_code):
        print 'An error has occured! Status code = %s' % status_code
        if status_code == '420':
            return False
        return True  # keep stream alive

    def on_timeout(self):
        print 'Snoozing Zzzzzz'



class MyHandler(DefaultCommandHandler):
    def privmsg(self, nick, chan, msg):
        global api
        msg = msg.decode()
        match = re.match('\!say (.*)', msg)
        if match:
            to_say = match.group(1).strip()
            api.update_status(to_say)
            print('Saying, "%s"' % to_say)


def connect_cb(cli):
    helpers.join(cli, CHANNEL)


def main():
    logging.basicConfig(level=logging.DEBUG)
    cli = IRCClient(MyHandler, host=HOST, port=PORT, nick=NICK)#,connect_cb=connect_cb)
    conn = cli.connect()
    i = 0
    while True:
        if i < 1000000:
            i+=1
        if i == 1000:
            print 'joining'
            helpers.join(cli, CHANNEL)
        if i == 1000000:
            print 'joining'
            helpers.join(cli, CHANNEL)
            helpers.msg(cli, CHANNEL, 'connected')
            i+=1
        try:
            item = status_queue.get(False)
            print str(item.author.screen_name)
            if str(item.author.screen_name) != NICK:
                helpers.msg(cli, CHANNEL, str(item.author.screen_name)+' -- '+str(item.text))
                api.update_status(str(item.author.screen_name)+' -- '+str(item.text))
        except:
            pass
        conn.next()      ## python 2



if __name__ == '__main__':
    status_queue = Queue.Queue()

    ##CUSTOMIZE_THIS_START
    consumer_key = 'YOUR_APP_KEY'
    consumer_secret = 'YOUR_APP_SECRET'
    key = 'YOUR_TOKEN_KEY'
    secret = 'YOUR_TOKEN_SECRET'
    ##CUSTOMIZE_THIS_END

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(key, secret)
    api = tweepy.API(auth)
    stream = tweepy.Stream(auth=auth, listener=StreamWatcherListener(status_queue))

    ##CUSTOMIZE_THIS_START
    follow_list = ['YOUR_TWITTER_USERID']
    ##CUSTOMIZE_THIS_END

    track_list = []
    stream.filter(follow_list, track_list, True)
    main()



