import sys

import requests
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QThread, pyqtSlot

from src.design_app import Ui_MainWindow
from src.downloader import FindVideo, DownloadVideo


def check_internet():
    """ Check internet on the pc. """
    try:
        res_internet = requests.get('http://google.com')
        if res_internet.status_code == 200:
            return True

    except OSError:
        return False


class StartThread(QThread):
    """ Find video stream initializer. """
    def __init__(self, link: str, quality: str):
        super().__init__()

        self.link = link
        self.quality = quality

        self.check_video = FindVideo(link, quality)

    def run(self):
        """ When a stream is created, the find video function from downloader.py is executed. """
        self.check_video.info_about_video()

    def get_name_video(self) -> str:
        """ Get name of the video. """
        return str(self.check_video.name_video)

    def get_name_channel(self) -> str:
        """ Get info about the channel name. """
        return str(self.check_video.name_channel)

    def get_description_video(self) -> str:
        """ Get a description for the video. """
        return str(self.check_video.description_video)

    def get_preview_video(self) -> str:
        """ Get a preview of the video. """
        return str(self.check_video.preview_video)


class DownloadThread(QThread):
    """ Downloading video stream initializer. """
    def __init__(self, link: str, quality: str, name_video: str, name_channel: str):
        super().__init__()

        self.link = link
        self.quality = quality

        self.download_video = DownloadVideo(link, quality, name_video, name_channel)

    def run(self):
        """ When a stream is created, the download function from downloader.py is executed. """
        self.download_video.starting_download()


class MainWindow(QtWidgets.QMainWindow):
    """ GUI logic. """
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.QualityBox.setCurrentText("720p")

        self.percent_loading = 0

        self.thread_check_start = None
        self.thread_download_start = None

        self.url = None
        self.quality = None

        self.name_video = None
        self.name_channel = None

        self.search_word = ''
        self.search_latter_word = 0
        self.timer_video_found = QtCore.QTimer()
        self.timer_video_found.setInterval(125)
        self.timer_video_found.timeout.connect(self.timer_search_video)

        self.time_cancel_search = 0
        self.timer_cancel_search = QtCore.QTimer()
        self.timer_cancel_search.setInterval(1000)
        self.timer_cancel_search.timeout.connect(self.timer_off_search)

        self.oldPos = None
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.center()

        self.ui.frame.installEventFilter(self)

        self.ui.Close_MinimizeButton.clicked.connect(lambda: self.close())
        self.ui.Roll_MinimizeButton.clicked.connect(lambda: self.showMinimized())
        self.ui.Check_Video_Button.clicked.connect(lambda: self.start_check_video())
        self.ui.Choose_Folder_Button.clicked.connect(lambda: self.delete_info_video())
        self.ui.Download_Button.clicked.connect(lambda: self.starting_download())

    def center(self):
        """ Center the window on the screen. """
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def eventFilter(self, obj, event):
        """ Filter events to enable dragging the window by clicking and dragging a specific widget (titleBar). """
        if obj == self.ui.frame and event.type() in (QtCore.QEvent.Type.MouseButtonPress, QtCore.QEvent.Type.MouseMove):

            if event.type() == QtCore.QEvent.Type.MouseButtonPress:
                self.oldPos = event.globalPos()

            elif event.type() == QtCore.QEvent.Type.MouseMove and self.oldPos:
                delta = QtCore.QPoint(event.globalPos() - self.oldPos)
                self.move(self.x() + delta.x(), self.y() + delta.y())
                self.oldPos = event.globalPos()

            return True

        return super(MainWindow, self).eventFilter(obj, event)

    def mousePressEvent(self, event):
        """ Capture the mouse position when the left mouse button is pressed, for window dragging. """
        self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        """ Reset the stored mouse position when the mouse button is released, ending the drag. """
        self.oldPos = None

    def close(self):
        """ Close app button. """
        if self.thread_check_start:
            self.thread_check_start.terminate()
            self.thread_check_start.quit()

        if self.thread_download_start:
            self.thread_download_start.terminate()
            self.thread_download_start.quit()

        QtWidgets.QApplication.instance().quit()
        sys.exit(1)

    def start_check_video(self):
        """ Processing the Find video button click. If all filled fields are successfully checked,
            the search for information about the video begins. """
        self.url = self.ui.Link_Video_LineEdit.text()
        self.quality = self.ui.QualityBox.currentText()

        internet = check_internet()

        if not internet:
            self.ui.Name_Program_Label_2.setText("ERROR: Not Internet in computer.")
            self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(205, 0, 0);')
            return

        if not self.url:
            self.ui.Name_Program_Label_2.setText("ERROR: Please enter a valid URL.")
            self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(205, 0, 0);')
            return

        self.thread_check_start = StartThread(self.url, self.quality)
        self.ui.Link_Video_LineEdit.setText('')

        self.thread_check_start.check_video.video_found_signal.connect(self.on_video_found)
        self.thread_check_start.check_video.video_not_found_signal.connect(self.on_video_not_found)
        self.thread_check_start.start()
        
        self.ui.Check_Video_Button.setEnabled(False)
        self.ui.Choose_Folder_Button.setEnabled(False)
        self.ui.Download_Button.setEnabled(False)

        self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(255, 127, 0);')

        self.timer_video_found.start()
        self.timer_cancel_search.start()

    def timer_search_video(self):
        """ Dynamic timer during video search. """
        search_sentence = ('V', 'i', 'd', 'e', 'o', ' ', 's', 'e', 'a', 'r', 'c', 'h', '.', ' ',
                           'P', 'l', 'e', 'a', 's', 'e', ',', ' ', 'w', 'a', 'i', 't', '.', '.', '.', '')

        self.ui.Name_Program_Label_2.setText(f"{self.search_word}")
        self.search_word += search_sentence[self.search_latter_word]
        self.search_latter_word += 1

        if self.search_latter_word == 29:
            self.search_latter_word = 0
            self.search_word = ''

    def timer_off_search(self):
        """ Timer that disables search if video is not found after 30 seconds. """
        self.time_cancel_search += 1

        if self.time_cancel_search == 30:
            self.thread_check_start.check_video.video_not_found_signal.emit()

    def update_video_info(self):
        """ Function for updating video information in the GUI, when it is located in downloader.py. """
        self.ui.ButtonsPanel.setMinimumHeight(111)
        self.ui.ButtonsPanel.setMaximumHeight(111)

        self.name_channel = self.thread_check_start.get_name_channel()
        self.name_video = self.thread_check_start.get_name_video()

        description = self.thread_check_start.get_description_video()
        preview = self.thread_check_start.get_preview_video()

        if self.name_video != '':
            self.ui.Name_Video.setText(self.name_video)

        if description != '':
            self.ui.Video_Info.setPlainText(description)

        if preview != '':
            image = QImage()
            image.loadFromData(requests.get(preview).content)
            self.ui.Prew_Label.setPixmap(QPixmap(image))
            self.ui.Prew_Label.show()

    def starting_download(self):
        """ Handle the download button click. The download thread starts. """
        internet = check_internet()

        if not internet:
            self.ui.Name_Program_Label_2.setText("ERROR: Not Internet in computer.")
            self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(205, 0, 0);')
            return

        if self.ui.Name_Program_Label_2.text() == "Video found. Select quality and start downloading.":
            self.quality = self.ui.QualityBox.currentText()

            self.ui.Check_Video_Button.setEnabled(False)
            self.ui.Choose_Folder_Button.setEnabled(False)

            self.ui.Name_Program_Label_2.setText("Console messages...")
            self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(205, 205, 205);')

            self.ui.ButtonsPanel.setMinimumHeight(0)
            self.ui.ButtonsPanel.setMaximumHeight(0)

            self.thread_download_start = DownloadThread(self.url, self.quality, self.name_video, self.name_channel)
            self.thread_download_start.download_video.progress_signal.connect(self.update_progress_bar)
            self.thread_download_start.download_video.completion_signal.connect(self.on_download_completed)
            self.thread_download_start.download_video.error_signal.connect(self.on_error_progress)
            self.thread_download_start.start()

        else:
            self.ui.Name_Program_Label_2.setText("ERROR: Please enter a valid URL.")
            self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(205, 0, 0);')
            return

    def delete_info_video(self):
        """ Handle te download button nickname. The download thread starts. """
        self.ui.Name_Video.setText("Name video...")

        self.ui.Name_Program_Label_2.setText("Console messages...")
        self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(205, 205, 205);')

        self.ui.Video_Info.setText('')
        self.ui.Link_Video_LineEdit.setText('')

        self.ui.Prew_Label.setPixmap(QPixmap(":/videologo/video logo.png"))
        self.ui.Prew_Label.show()

    @pyqtSlot()
    def on_video_found(self):
        """ Signal processing when a video is found. """
        self.time_cancel_search = 0
        self.search_latter_word = 0

        self.search_word = ''

        self.timer_cancel_search.stop()
        self.timer_video_found.stop()

        self.thread_check_start.terminate()
        self.thread_check_start.quit()

        self.ui.Check_Video_Button.setEnabled(True)
        self.ui.Choose_Folder_Button.setEnabled(True)
        self.ui.Download_Button.setEnabled(True)

        self.ui.Name_Program_Label_2.setText("Video found. Select quality and start downloading.")
        self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(0, 205, 0);')
        self.update_video_info()

    @pyqtSlot()
    def on_video_not_found(self):
        """ Signal processing when video is not found. """
        self.time_cancel_search = 0
        self.search_latter_word = 0

        self.search_word = ''

        self.timer_cancel_search.stop()
        self.timer_video_found.stop()

        self.thread_check_start.terminate()
        self.thread_check_start.quit()

        self.ui.Check_Video_Button.setEnabled(True)
        self.ui.Choose_Folder_Button.setEnabled(True)
        self.ui.Download_Button.setEnabled(True)

        self.ui.Name_Program_Label_2.setText("ERROR: Video not found. Please enter valid link.")
        self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(205, 0, 0);')

    @pyqtSlot(float)
    def update_progress_bar(self, progress):
        """ Progress bar update function in GUI. """
        if progress > self.percent_loading:
            self.percent_loading = int(progress)
            self.ui.progressBar.setValue(self.percent_loading)

        if progress == 100:
            self.percent_loading = 0

    @pyqtSlot()
    def on_download_completed(self):
        """ Function to complete download progress. """
        self.thread_download_start.terminate()
        self.thread_download_start.quit()

        self.ui.Check_Video_Button.setEnabled(True)
        self.ui.Choose_Folder_Button.setEnabled(True)

        self.ui.Name_Program_Label_2.setText(f'Success! Video has been download!')
        self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(0, 205, 0);')

        self.ui.ButtonsPanel.setMinimumHeight(111)
        self.ui.ButtonsPanel.setMaximumHeight(111)

        self.percent_loading = 0
        self.ui.progressBar.setValue(0)

        self.ui.Name_Video.setText("Name video...")
        self.ui.Video_Info.setText('')
        self.ui.Link_Video_LineEdit.setText('')
        self.ui.Prew_Label.setPixmap(QPixmap(":/videologo/video logo.png"))
        self.ui.Prew_Label.show()

    @pyqtSlot()
    def on_error_progress(self):
        """ Function error download progress. """
        self.thread_download_start.terminate()
        self.thread_download_start.quit()
        self.delete_info_video()

        self.ui.Check_Video_Button.setEnabled(True)
        self.ui.Choose_Folder_Button.setEnabled(True)

        self.ui.Name_Program_Label_2.setText(f'Error loading... Please, try again.')
        self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(205, 0, 0);')

        self.ui.ButtonsPanel.setMinimumHeight(111)
        self.ui.ButtonsPanel.setMaximumHeight(111)

        self.percent_loading = 0
        self.ui.progressBar.setValue(0)

        self.ui.Name_Video.setText("Name video...")
        self.ui.Video_Info.setText('')
        self.ui.Link_Video_LineEdit.setText('')
        self.ui.Prew_Label.setPixmap(QPixmap(":/videologo/video logo.png"))
        self.ui.Prew_Label.show()
