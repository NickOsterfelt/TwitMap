from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import urllib.request
import urllib.parse

track = ["trump"]
consumer_key = ""
consumer_secret = ""
access_key = ""
access_secret = ""
sentiment_load = 0
sentiment_index = 0

class listener(StreamListener):


    def on_data(self,data):
         coords = ""
         jd = json.loads(data)
         if 'text' in jd:
             text = jd['text'] #urllib.parse doesnt like json, storing tweet text in var as string
             values = {'txt': text} #API request parameters
             parsed_values = urllib.parse.urlencode(values) #URL encoding request
             bytes_data = parsed_values.encode('ascii') #Parsing data for post request
             sentiment = urllib.request.urlopen("http://sentiment.vivekn.com/api/text/", bytes_data) #POST request to sentiment analysis API
             json_sentiment = json.loads(sentiment.read().decode('utf-8')) #getting rid of noise in json
             confidence = json_sentiment["result"]["confidence"]
             sent = json_sentiment["result"]["sentiment"]
             if float(confidence) > 75:
                 global sentiment_load
                 sentiment_load += 1
                 count = 0
                 if sent == 'Negative':
                     count = -1
                 if sent == 'Positive':
                     count = 1
                 global sentiment_index
                 sentiment_index += count
                 if sentiment_load != 0 and sentiment_load % 30 == 0:
                     print("Total sentiment:", (sentiment_index/sentiment_load))
                 #if sentiment_load != 0 and sentiment_load % 30 == 0:
                     #print(sentiment_index/sentiment_load)
             if('geo' in jd and 'coordinates' in jd and 'place' in jd): #if coordinate fields exist
                 if(jd['geo'] != None):
                     coords = jd['geo']['coordinates']
                 elif(jd['coordinates'] != None):
                     coords = jd['coordinates']['coordinates']
                 elif(jd['place'] != None): #most relevant coordinates first
                     coords = jd['place']['bounding_box']['coordinates'][0][1]
                 if coords != "": #if coords variable is not, empty, begin Sentiment analysis
                     print(text, "\n", "Coords:", coords, "\n", "Sentiment:", sent, "\n", "Confidence:", confidence, "\n")
             return




    def on_error(self, status):
        print(status)

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
twitterStream = Stream(auth, listener())
sentiment_load = 0
sentiment_index = 0
twitterStream.filter(track=track)
