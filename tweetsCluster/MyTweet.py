from urlparse import urlparse
import time,re

class MyTweet(object):
    """
    Parse and preprocess raw tweet object

    Reference:
    Tweets Object https://goo.gl/d1hExF
    Entity Object https://goo.gl/Sj7TuJ

    """
    def __init__(self,tweet):
        self.text = tweet.text

        self.cleanText = self.process(tweet.text,
                                     tweet.user.screen_name,
                                     tweet.in_reply_to_user_id_str,
                                     tweet.in_reply_to_status_id)
        self.lang = tweet.lang
        self.domains, self.urlpPaths, self.hasPhoto = self.parseUrl(tweet.entities)
        self.timezone = tweet.user.utc_offset if tweet.user.utc_offset else 0

        # For "best" results
        self.time = time.mktime(time.strptime(tweet.created_at,'%a %b %d %H:%M:%S +0000 %Y'))
        self.retweetCnt = tweet.retweet_count
        self.isRetweet = self.isRetweet(tweet.text)
        self.favCnt = tweet.user.favourites_count
        self.followers = tweet.user.followers_count

    def process(self,rawTweet, creatorName, *args):
        rawTweet = rawTweet.lower()

        # remove url and media link
        text = re.sub(r"http\S+", "", rawTweet)

        text += "@{} ".format(creatorName)
        for arg in args:
            if arg:
                text += "{} ".format(str(arg))
        return text

    def parseUrl(self,entities):
        """
        Unzip the url and parse it to extract features
        """
        domains, urlPaths = [], []
        hasPhoto = 0


        # urls
        for item in entities.urls:
            try:
                url = item.expanded_url if hasattr(item,'expanded_url') else item.url
            except AttributeError:
                continue
            parsed = urlparse(url)
            domains.append(parsed.netloc)
            urlPaths.append(parsed.path.strip("/"))

        # medias
        if hasattr(entities,'media'):
            for item in entities.media:
                try:
                    hasPhoto = item.type == "photo"
                except AttributeError:
                    continue
                mediaUrl = item.media_url
                parsed = urlparse(mediaUrl)
                domains.append(parsed.netloc)

        return domains, urlPaths, hasPhoto

    def isRetweet(self,tweet):
        return 'rt' in tweet.lower()