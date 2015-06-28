from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import QTimer
from PyQt5 import QtCore
from gtweet import StatusWidget
import http.client
import pickle


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.hide()
        f = open("last_tweet", 'r')
        last_id = int(f.read())
        print(last_id)
        f.close()

        self.tweets = []

        self.fetch_tweets()
        self.tim = QTimer(self)
        self.tim.timeout.connect(self.fetch_tweets)
        self.tim.start(60000)

        self.show()

    def fetch_tweets(self):
        if len(self.tweets) == 0:
            id = 0
        else:
            id = self.tweets[-1].tid

        conn = http.client.HTTPConnection("127.0.0.2", 8080)
        conn.request("GET", "/status/from_id/" + str(id))
        resp = conn.getresponse()
        if resp.status == 200:
            tw = pickle.load(resp)
            tw.sort()
            for i in tw:
                self.addTweet(i)
            f = open("last_tweet", 'w')
            f.write(str(tw[-1].tid))
            f.close()

    def initUI(self):
        self.setWindowTitle('Twitter Client')

        lay = QVBoxLayout(self)
        scr = QScrollArea(self)
        scr.setWidgetResizable(True)
        scr.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        lay2 = QVBoxLayout()
        self.setLayout(lay)
        placehold = QWidget()
        lay.addWidget(scr)
        scr.setWidget(placehold)
        placehold.setLayout(lay2)
        self.lay = lay2

        lay2.setSpacing(0)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)

        self.show()

    def addTweet(self, tweet):
        self.tweets.append(tweet)
        widget = StatusWidget(tweet)
        widget.delete_tweets.connect(self.deleteTweets)
        self.lay.insertWidget(0, widget)

    def deleteTweets(self, id):
        print("Delete : " + str(id))
