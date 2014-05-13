import praw, time
from wordnik import *

### CONFIG ###
bot_user = raw_input("Bot username? >")
bot_pass = raw_input("Bot password? >")

r = praw.Reddit("Dictionary bot by /u/DjManEX")
r.login(username = bot_user, password = bot_pass)
print "Logged in to Reddit."

apiUrl = 'http://api.wordnik.com/v4'
apiKey = 'd62ea5e532f697a4391060c8cf20d1fe1fa7e8901e5a4fcfc'
client = swagger.ApiClient(apiKey, apiUrl)
wordApi = WordApi.WordApi(client)
print "Logged in to Wordnik API.\n"
### END CONFIG ###

def formatPost(defins, comment):
    if defins == None:
        post = "---\n> [**%s**](http://www.wordnik.com/words/%s)\n\n> *No definitions found.*\n\n ^Scrabble ^score: ^N/A\n\n---\n\n" % (searchword, searchword) + \
        "[^Report ^a ^problem](http://www.np.reddit.com/message/compose?to=djmanex&subject=DictBot Problem&message=Problem: %s)" % comment
    else:
        pro = wordApi.getTextPronunciations(searchword, limit = 1)
        sScore = wordApi.getScrabbleScore(searchword)
        post = "---\n> [**%s**](http://www.wordnik.com/words/%s) %s" % (searchword, searchword, pro[0].raw)
        for defin in defins:
            post = '\n\n> * '.join([post, defin.text])
        post = '\n'.join([post, "\n\n ^Scrabble ^score: ^%s\n\n---\n [^Report ^a ^problem](http://www.np.reddit.com/message/compose?to=djmanex&subject=DictBot Problem&message=Problem: %s) ^| \
            [^Source ^code](https://github.com/SpeedOfSmell/RedditBots/blob/master/DictBot/DictBot.py) ^| \
            [^More ^info](https://github.com/SpeedOfSmell/RedditBots/blob/master/DictBot/README.md)" % (sScore.value, comment)])
    return post

def replied(comment):
	children = comment.replies
	
	if children:
		for child in children:
			if child.author.name in ["DictBot", bot_user]:
				return True

if __name__ == '__main__':
	while True:
		try:
			commentList = r.get_comments('all', limit = 1000)
			
			for comment in commentList:
				replied(comment) #check if bot has already replied
				if (comment.body.lower()[0:15] == "dictbot define ") and not replied(comment):
					searchword = comment.body.lower()[15:]
					print "\"%s\" requested in /r/%s by /u/%s" % (searchword, comment.subreddit.display_name, comment.author.name)
					definitions = wordApi.getDefinitions(searchword)
					formatted = formatPost(definitions, comment.id)
					comment.reply(formatted)

		except praw.requests.HTTPError:
			print "No connection to Reddit.\n"
			time.sleep(20)
			continue
		
		except praw.errors.RateLimitExceeded as error:
			print "Bot posting too much. Sleeping for %s seconds." % error.sleep_time
			time.sleep(error.sleep_time)
			print "Done sleeping.\n"
			continue
		
		except Exception as error:
			print "Unknown error occured while attempting to retrieve comments.\n" + str(error)
			continue
			