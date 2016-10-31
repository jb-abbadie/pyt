from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QTextBrowser,\
        QFrame, QPushButton
from PyQt5.QtGui import QPixmap, QTextCursor, QIcon, QImage, QPainter,\
        QDesktopServices
from datetime import timezone
from gui.media_display import MediaWidget


class StatusWidget(QWidget):
    delete_tweets = pyqtSignal(str)

    def __init__(self, tweet, cache):
        super().__init__()

        self.tid = tweet.tid
        self.tweet = tweet
        self.cache = cache
        if tweet.rt:
            self.rt = True
            self.st = tweet.status
            self.rtst = tweet.o_status
        else:
            self.rt = False
            self.st = tweet.status

        self.initUI(tweet)

    def getPix(self, url1, url2=None):
        img1 = self.cache.get_resource(url1)
        i1 = QImage.fromData(img1)
        i1 = i1.scaledToHeight(60, Qt.SmoothTransformation)
        if url2 is not None:
            img2 = self.cache.get_resource(url2)
            i2 = QImage.fromData(img2)
            i2 = i2.scaledToHeight(30, Qt.SmoothTransformation)
            p = QPainter()
            p.begin(i1)
            p.drawImage(0, 30, i2)
            p.end()

        ret = QLabel()
        ret.setPixmap(QPixmap.fromImage(i1))
        return ret

    def choose_video(self, vids):
        chosen = vids['expanded_url']
        max_br = -1
        for i in vids['video_info']['variants']:
            try:
                if i['bitrate'] > max_br:
                    max_br = i['bitrate']
                    chosen = i['url']
            except:
                pass
        return(chosen)

    def process_text(self, status):
        print("---")
        if (self.tweet.status.truncated):
            print("extended")
            # status.text = self.tweet.status.extended_tweet['full_text']
            print(status.text)
            print(self.tweet.status.extended_tweet['entities'])
            print("o")
            print(self.tweet.status.extended_entities)
            # self.status.extended_entities = self.status.extended_tweet['entities']
        html_text = self.tweet.text
        pretty_text = self.tweet.text

        html_text = html_text.replace("\n", "<br>")
        html_text = html_text.replace("<br><br>", "<br>")

        for i, j in self.tweet.ent['pic']:
            html_text = html_text.replace(i, "")
            html_text += " <a href='pic://t?{0}'>Pic</a>".format(j)
            pretty_text = pretty_text.replace(i, '')
            pretty_text += ' Pic'
        for i, j in self.tweet.ent['gif']:
            html_text = html_text.replace(i, "")
            html_text += " <a href='gif://t?{0}'>Gif</a>".format(j)
            pretty_text = pretty_text.replace(i, '')
            pretty_text += ' Gif'
        for i, j in self.tweet.ent['vid']:
            html_text = html_text.replace(i, '')
            html_text += " <a href='vid://t?{0}'>Vid</a>".format(j)
            pretty_text = pretty_text.replace(i, "")
            pretty_text += ' Vid'
        for i, j, k in self.tweet.ent['url']:
            to_rep = self.tweet.text[i[0]:i[1]]
            html_text = html_text.replace(to_rep, "<a href='{0}'>\
                    {1}</a>".format(k, j))
            pretty_text = pretty_text.replace(to_rep, j)

        self.text = html_text

        splitted = pretty_text.split("\n")
        nb = len(splitted)
        for i in splitted:
            nb += int(len(i)/72)
            if len(i) == 0:
                nb -= 1

        return nb

    def add_pic(self):
            if not self.rt:
                pic = self.getPix(self.tweet.ent['profile'][0])
            else:
                pic = self.getPix(self.tweet.ent['profile'][0],
                                  self.tweet.ent['profile'][1])

            self.lay.addWidget(pic, 0, 0, 2, 1)

    def add_time(self):
        time = self.st.created_at.replace(tzinfo=timezone.utc)\
                .astimezone(tz=None)
        string = time.strftime("%d/%m - %H:%M")

        self.lay.addWidget(QLabel(string), 0, 3)

    def add_text(self):
        nb_linebreak = self.process_text(self.st)
        text = QTextBrowser()
        text.setHtml(self.text)
        text.setOpenLinks(False)
        text.moveCursor(QTextCursor.End)
        if nb_linebreak == 1:
            text.setFixedSize(500, 30)
        elif nb_linebreak == 2:
            text.setFixedSize(500, 48)
        elif nb_linebreak == 3:
            text.setFixedSize(500, 68)
        elif nb_linebreak == 4:
            text.setFixedSize(500, 88)
        else:
            text.setFixedSize(500, 108)

        text.anchorClicked.connect(self.link_clicked)

        self.lay.addWidget(text, 1, 1, 1, 3)

    def add_username(self):
        name = "<b>" + self.st.user.name + "</b> <i>@" +\
                self.st.user.screen_name + "</i>"

        self.lay.addWidget(QLabel(name), 0, 1)

    def add_button(self):
        icon = QIcon.fromTheme("edit-delete")
        self.button = QPushButton(icon, "")
        self.button.pressed.connect(self.send_delete)

        self.lay.addWidget(self.button, 1, 4)

    def send_delete(self):
        if self.rt:
            self.delete_tweets.emit(self.rtst.id_str)
        else:
            self.delete_tweets.emit(self.st.id_str)

    def link_clicked(self, url):
        sc = url.scheme()
        if sc == "pic" or sc == "gif" or sc == "vid":
            self.media = MediaWidget(url.query(), sc, self.cache)
        else:
            QDesktopServices.openUrl(url)

    def initUI(self, tweet):
        layout = QGridLayout()
        self.setLayout(layout)
        self.lay = layout

        layout.setColumnStretch(10, 100)

        self.add_pic()
        self.add_time()
        self.add_text()
        self.add_username()
        self.add_button()

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line, 4, 0, 1, -1)

        self.setLayout(layout)

        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
