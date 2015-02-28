#!/usr/bin/env python2
# -*- coding: utf-8 -*- #

from twitterbot import TwitterBot
from collections import deque
import itertools as it
from random import choice
import random
import time

class TwitterParty(TwitterBot):
    def bot_init(self):
        """
        Initialize and configure your bot!

        Use this function to set options and initialize your own custom bot
        state (if any).
        """


        ############################
        # REQUIRED: LOGIN DETAILS! #
        ############################
        self.config['api_key'] = 'gZO350tR68xqoGyYD2CcWR2RN'
        self.config['api_secret'] = 'b1LfQqNf07wbxptNpOt37aJ66wbIusIDXckrpCsYwB4ss8C8VV'
        self.config['access_key'] = '3015729825-IT3Fg6NYclpfZJU8ITY9k72ICfMPweDihwal2J6'
        self.config['access_secret'] = 'rfMj0KBjcM1WoVK2DlT736RQDmhXiH7qGV0lrEWQNeP3p'


        ######################################
        # SEMI-OPTIONAL: OTHER CONFIG STUFF! #
        ######################################

        # how often to tweet, in seconds
        self.config['tweet_interval'] = 1 * 60     # default: 30 minutes

        # use this to define a (min, max) random range of how often to tweet
        # e.g., self.config['tweet_interval_range'] = (5*60, 10*60) # tweets every 5-10 minutes
        self.config['tweet_interval_range'] = None

        # only reply to tweets that specifically mention the bot
        self.config['reply_direct_mention_only'] = False

        # only include bot followers (and original tweeter) in @-replies
        self.config['reply_followers_only'] = True

        # fav any tweets that mention this bot?
        self.config['autofav_mentions'] = True

        # fav any tweets containing these keywords?
        self.config['autofav_keywords'] = ["social", "charity", "peace"]

        # follow back all followers?
        self.config['autofollow'] = True


        ###########################################
        # CUSTOM: your bot's own state variables! #
        ###########################################
        
        # If you'd like to save variables with the bot's state, use the
        # self.state dictionary. These will only be initialized if the bot is
        # not loading a previous saved state.

        # self.state['butt_counter'] = 0

        self.state['people'] = {}
        self.state['reply_to'] = {}
        self.state['recieved'] = {}

        self.state['conversations'] = deque()
        self.state['counter'] = {}
        self.state['DavidRoads'] = deque()



        with open('/usr/share/dict/words') as f:
            self.words = [w.strip() for w in f.readlines()]
        with open('names.txt') as f:
            self.names = [w.strip() for w in f.readlines()]
        with open('top_names.txt') as f:
            self.top_names = [w.strip() for w in f.readlines()]

        self.hashtags = "#lifecoach #truth #joy #minimalism #motherhood #emotion #motivational #feelings \
        #bodybuilding #gogetit #achievement #inspiration #accomplish #rage #accomplishment #fitness #emotional\
        #real #get #i #plz #fast #better #food #teeth #wanna #dailyverse #christian #rise\
        #meaning #bible #conquer #instadaily #victoryverse #yahweh #yeshua #strength #christ #victoryphoto\
        #theword #victorious #entervictorious #victory #scripture #messiah #olderandwiser #whimsical #perspective \
        #encouragement #beautiful #classic #instalike #dope #justsaying #instagood #photooftheday #sweet #comedy #picoftheday\
        #fact #happy #nature #focus #lifestyle #motivationwall #yoga #universe #wordsofwisdom #amazing #bestoftheday #light #smile\
        #instagramhub".split()

        self.wisdom = "#quote #alberteinstein #wisdom #breathing #creating #atpeace #relaxed #practice \
        #innerfocus #moving #mental #expertadvice #guru #union #guidance #yogi #yuj #calm #detroityogi #peaceful #movingmeditation \
        #physical #noted #spiritual #prayers #compassion #believe #mind #life #thankful".split()

        self.positive = "focused positive calm motivated".split()

        self.mediahashtags = ['#fun','#funny','#vine', '#gif']
        self.r = random.Random()


        #self.register_custom_handler(self.cleanup_followers, 60*60*24)

        #Searches: 450 / 90
        #Followers: 15 / 3
        #Timeline: 300 / 60


        # You can also add custom functions that run at regular intervals
        # using self.register_custom_handler(function, interval).
        #
        # For instance, if your normal timeline tweet interval is every 30
        # minutes, but you'd also like to post something different every 24
        # hours, you would implement self.my_function and add the following
        # line here:
        
        # self.register_custom_handler(self.my_function, 60 * 60 * 24)


    def cleanup_followers(self):
        for x in self.state['followers']:
            if not (x in self.state['people']):
                self.api.destroy_friendship(x)

    def remove_person(self, ID):
        self.api.destroy_friendship(ID)
        self.api.destroy_friendship(self.state['people'][ID])

        self.state['people'].pop(ID)
        self.state['counter'].pop(ID)


    def add_person(self, user, partner, reply_id):
        if hasattr(user, 'status'):
            try:
                self.api.create_favorite(user.status.id)
                self.log('Adding @%s AND favoriting tweet in add_person():\n%s' % (user.screen_name, user.status.text))
            except: pass
        else:
            self.log('Adding @%s in add_person(), but User has no .status object to favorite.' % user.screen_name)
        try:
            self.api.create_friendship(user.id)
        except: 
            pass
        self.state['conversations'].append(user.id) #to remove if he gets old
        self.state['reply_to'][user.id] = reply_id
        self.state['counter'][user.id] = 0

        self.state['people'][user.id] = partner.id



    def reply(self, tweet, prefix):

        #If we know this person, reply to his partner.
        #We are now waiting for the partner instead. So queue him for removal.

        if tweet.author.id in self.state['people'] and tweet.author.id != self.id:
            self.state['counter'][tweet.author.id] += 1

            self.log('got the mention: \n%s \nfrom @%s. Trying to reply. ' % (tweet.text, tweet.author.screen_name))

            recipentID = self.state['people'][tweet.author.id]
            recipent = self.api.get_user(recipentID)

            if not recipentID in self.state['people']:
                try:
                    self.add_person(recipent, tweet.author, tweet.id)
                except:
                    pass
            else:
                self.state['counter'][recipentID] += 1
                self.state['conversations'].append(recipentID)
            try:
                self.api.create_favorite(self.state['reply_to'][tweet.author.id])
            except:
                pass

            text = self.clean_tweet(tweet.text, recipent)

            self.log('Tweeting %s char REPLY by @%s: \n"%s"' % (len(text), tweet.author.screen_name, text))
            try:
                lastTweet = self.api.update_status(status=text[0:140], in_reply_to_status_id=self.state['reply_to'][tweet.author.id])
                self.state['recieved'][recipentID] = lastTweet.id
            except: pass

        elif tweet.author.id != self.id:
            text = '@' + tweet.author.screen_name + ' ' + self.random_reply()
            try:
                self.api.update_status(status=text, in_reply_to_status_id=tweet.id)
                self.log('Replying to @%s:s unknown tweet:\n%s \n with:' % (tweet.author.screen_name, tweet.text, text))

            except: self.log('Could not reply to unknown tweet by: @%s' % tweet.author.screen_name)



    def random_reply(self):
        return choice(["Hi, I just want to start a random conversation with you :). %s." % choice(self.words).capitalize(), 
                        'Hey, %s%s :).' % ('I like the word ', choice(self.words).lower())])

    def clean_tweet(self, text, recipent):
        words = text.split()
        mention = '@' + recipent.screen_name + ' hi :),'
        if 'hi' in text.lower():
            mention = '@' + recipent.screen_name 
        name = '@' + recipent.screen_name
        insertFirst = True

        for i in range(len(words)):
            if '@' in words[i]:
                if i == 0:
                    words[0] = mention
                    mention = ''
                else:
                    words[i] = name
                if mention != '':
                    mention = 'Hi,' # Will only replace on the first mention
                name = ''
            if 'thora' in words[i].lower():
                words[i] = recipent.name.split()[0]

        #if no replace -> add the mention in the beginning anyways.
        words = [x for x in it.chain([mention], words) if x != '']
        cleaned = ' '.join(words)
        return cleaned.replace('&amp;', '&')

    def bump(self, ID):
        """takes ID of user to bump"""
        try:
            user = self.api.get_user(ID)
        except:
            return
        self.log('Bumping %s' % (user.screen_name))

        text=self.clean_tweet("hi. I just wanted to start a random conversation with you. <3.", user)

        #Try to send as a reply to last message.
        if ID in self.state['recieved']:
            lastTweet = self.api.update_status(status=text, in_reply_to_status_id=self.state['recieved'][ID])
        else:
            try:
                lastTweet = self.api.update_status(status=text)
                self.state['recieved'][ID] = lastTweet.id

            except:
                self.log('Could not duplicate bump to @%s, failed' % user.screen_name)



        recipentID = self.state['people'][ID]
        try:
            recipent = self.api.get_user(recipentID)


            text = self.clean_tweet(self.random_reply(), recipent)
            self.log('Thanking @%s for tweet that got no reply with: %s' % (recipent.screen_name, text))
            self.api.create_favorite(self.state['reply_to'].get(ID))

            lastTweet = self.api.update_status(status=text[0:140], in_reply_to_status_id=self.state['reply_to'][ID])

            self.state['recieved'][recipentID] = lastTweet.id
        except:
            pass

    def find_matches(self):

        def ok_tweet(tweet):
            #No api calls used
            if tweet == []:
                return False
            if isinstance(tweet, list):
                tweet = tweet[0]
            if tweet.author.lang != 'en':
                return False
            #if tweet.author.possibly_sensitive:
            #    return False
            if self.id == tweet.author.id:
                return False
            if 'RT' in tweet.text:
                return False
            if 'follow' in tweet.text.lower():
                return False
            if len(tweet.author.screen_name) > 13:
                return False
            if tweet.author.id in self.state['people'].values():
                return False
            if tweet.author.id in self.state['people']:
                return False
            if tweet.author.followers_count > 1500:
                return False
            if tweet.author.friends_count > 1100:
                return False
            return True

        def ok_user(user):
            #No api calls used
            if self.id == user.id:
                return False
            #if user.possibly_sensitive:
            #    return False
            if user.id in self.state['people']:
                return False
            if user.id in self.state['people'].values():
                return False
            if user.lang != 'en':
                return False
            if len(user.screen_name) > 13:
                return False
            if user.statuses_count < 12:
                return False
            if user.followers_count > 1500:
                return False
            if user.friends_count > 1100:
                return False
            return True


        queries=[]
        queries.append('stay %s' % choice(self.positive))
        #queries.append(choice(choice([self.wisdom, self.hashtags])))
        queries.append( '%s %s %s' % tuple(self.r.sample([choice(self.hashtags), choice(self.wisdom), 'best', 'love', '?', '?',  ''], 3)))
        queries.append( choice(self.words) + choice(['', ' love ?']))
        queries.append(choice(self.mediahashtags))


        #returns tweets. Maximum 15
        #questions is a list of results for each query
        questions = [[x for x in self.api.search(q, 'en')] for q in queries]

        #API Rate here is limited to 60 per 15 min. danger.
        #FIX: Retweet is a list of empty lists
        #import pdb;pdb.set_trace()

        #retweets are now a list of lists for each search. With many retweets for each search.

        questions = map(lambda l: list(filter(ok_tweet, l)), questions)


        userqueries = [choice(self.wisdom), choice(self.hashtags), choice(self.names), choice(self.top_names), choice(self.words)]


        users = [[x for x in self.api.search(uq) if ok_tweet(x)]
                for uq in userqueries]

        self.log('%s OK questions for "%s"' % (
                ', '.join([str(len(x)) for x in questions]), '", "'.join(queries)))
        self.log('%s OK users for "%s"' % (
            ', '.join([str(len(x)) for x in users]), '", "'.join(userqueries)))
        

        # retweets = [[[t for t in self.api.retweets(x.id, 5) if ok_tweet(t)] for x in q] for q in questions]

        # self.log('%s OK retweets for "%s"' % (
        #     ', '.join([str(len(filter(lambda a: len(a)>0, x))) for x in retweets]), '", "'.join(queries)))

        # nq = sum(map(len,questions))
        # nu = sum(map(len,users))

        # #Each l is a list of retweet-lists for each tweet. Just take the first.
        # for l in retweets:
        #     new = [x[0] for x in l if len(x) > 0]

        #     if nq > nu:
        #         nu += len(new)
        #         users += [new]
        #     else:
        #         nq += len(new)
        #         questions += [new]
        return map(lambda status: status.author, it.chain.from_iterable(users)), it.chain.from_iterable(questions)


    def remove_old(self):
        ID = self.state['conversations'].popleft() # = None? Conversations is empty queue.
        if self.state['counter'][ID] > 0:
            self.state['counter'][ID] -= 1
            #This person was added because he should reply. Did not reply. Send one more tweet before removing:
        elif self.state['counter'][ID] == 0:
            self.state['conversations'].append(ID)
            self.state['counter'][ID] -= 1
            self.bump(ID)
        else: #counter == -1
            self.remove_person(ID)


    def on_scheduled_tweet(self):
        """
        Make a public tweet to the bot's own timeline.

        It's up to you to ensure that it's less than 140 characters.

        Set tweet frequency in seconds with TWEET_INTERVAL in config.py.
        """

        self.log('We have %s active conversations. ' % len(self.state['conversations']))


        if len(self.state['conversations']) > 2000:
            #Removing old people
            self.remove_old()
                
        else:


            users, questions = self.find_matches()

            for user, tweet in zip(users, questions):
                self.add_person(user, tweet.author, tweet.id)

                text = self.clean_tweet(tweet.text, user)
                self.log('Tweeting %s chars by %s: \n"%s"' % (len(text), tweet.author.screen_name, text))
                try:
                    lastTweet = self.api.update_status(status=text[0:140])
                    self.state['recieved'][user.id] = lastTweet.id
                except:
                    pass
                self.log('')
                time.sleep(6)



            text, ID =  self.state['DavidRoads'].popleft()
            text =  text.replace('&amp;', '&')

            self.log('Tweeting quote:\n%s' % text)
            if len(self.state['DavidRoads']) == 0:
                self.state['DavidRoads'].extend([(tweet.text, tweet.id) for tweet in self.api.user_timeline('DavidRoads', max_id=ID)])
            try: 
                self.api.update_status(status="%s%s" % (text, choice([' #quotestoliveby', ''])))
            except: 
                self.log('Could not tweet quote by DavidRoads.')
                pass

    def on_mention(self, tweet, prefix):
        """
        Defines actions to take when a mention is recieved.

        tweet - a tweepy.Status object. You can access the text with
        tweet.text

        prefix - the @-mentions for this reply. No need to include this in the
        reply string; it's provided so you can use it to make sure the value
        you return is within the 140 character limit with this.

        It's up to you to ensure that the prefix and tweet are less than 140
        characters.

        When calling post_tweet, you MUST include reply_to=tweet, or
        Twitter won't count it as a reply.
        """
        if tweet.author.screen_name.lower() != 'spiritLaunch':
            self.reply(tweet, prefix)


    def on_timeline(self, tweet, prefix):
        """
        Defines actions to take on a timeline tweet. 
        Things from people we follow show up on the timeline.

        tweet - a tweepy.Status object. You can access the text with
        tweet.text

        prefix - the @-mentions for this reply. No need to include this in the
        reply string; it's provided so you can use it to make sure the value
        you return is within the 140 character limit with this.

        It's up to you to ensure that the prefix and tweet are less than 140
        characters.

        When calling post_tweet, you MUST include reply_to=tweet, or
        Twitter won't count it as a reply.
        """
        #if 'wanna hear u echo' in tweet.text.lower():
        #    self.post_tweet(prefix + ' ECHO (ECHO) ECHO (ECHO)', reply_to=tweet)


if __name__ == '__main__':
    #if  :

    bot = TwitterParty()
    bot.run()
