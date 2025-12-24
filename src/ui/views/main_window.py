from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import pyqtSlot, QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

from src.resources.design_app import Ui_MainWindow


class MainWindow(QMainWindow):
    """ GUI logic. """
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._network_manager = QNetworkAccessManager(self)

        self.setWindowTitle('Video Downloader')
        self.ui.QualityBox.setCurrentText("720p")
        self.percent_loading = 0

        self.search_word = ''
        self.search_latter_word = 0
        self.timer_video_found = QtCore.QTimer()
        self.timer_video_found.setInterval(125)
        self.timer_video_found.timeout.connect(self.timer_search_video)

        self.oldPos = None
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.center()

        self.ui.frame.installEventFilter(self)

    def center(self):
        """ Center the window on the screen. """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
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

    def get_url_video_info(self) -> str:
        """ After clicking the Find button, we get the video link from the field. """
        return self.ui.Link_Video_LineEdit.text()

    def get_quality_video_info(self) -> str:
        """ After clicking the Find button, we get the video quality from the field. """
        return self.ui.QualityBox.currentText()

    def check_valid_url(self) -> bool:
        return self.ui.Name_Program_Label_2.text() == "Video found. Select quality and start downloading."

    def _load_preview(self, url: str):
        req = QNetworkRequest(QUrl(url))
        req.setAttribute(QNetworkRequest.RedirectPolicyAttribute, True)
        reply = self._network_manager.get(req)
        reply.finished.connect(lambda: self._on_preview_loaded(reply))          # type: ignore

    def delete_info_video(self):
        """ Delete info about video in UI. """
        self.ui.Name_Video.setText("Name video...")
        self.ui.Name_Program_Label_2.setText("Console messages...")
        self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(205, 205, 205);')
        self.ui.Video_Info.setText('')
        self.ui.Link_Video_LineEdit.setText('')
        self.ui.Prew_Label.setPixmap(QPixmap(":/videologo/video logo.png"))
        self.ui.Prew_Label.show()

    def update_ui_start_check_video(self):
        """ Interface update when searching for videos. """
        self.ui.Link_Video_LineEdit.setText('')
        self.ui.Check_Video_Button.setEnabled(False)
        self.ui.Choose_Folder_Button.setEnabled(False)
        self.ui.Download_Button.setEnabled(False)
        self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(255, 127, 0);')
        self.timer_video_found.start()

    def update_ui_start_download_video(self):
        """ Handle the download button click. The download thread starts. """
        self.ui.Check_Video_Button.setEnabled(False)
        self.ui.Choose_Folder_Button.setEnabled(False)
        self.ui.Name_Program_Label_2.setText("Console messages...")
        self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(205, 205, 205);')
        self.ui.ButtonsPanel.setMinimumHeight(0)
        self.ui.ButtonsPanel.setMaximumHeight(0)

    def update_video_info(self, name_video, description_video, preview_video):
        """ Signal processed updating UI when video been founded. """
        if preview_video:
            self._load_preview(preview_video)
        else:
            self.ui.Prew_Label.clear()
            self.ui.Prew_Label.hide()
        if name_video != '':
            self.ui.Name_Video.setText(name_video)
        if description_video != '':
            self.ui.Video_Info.setPlainText(description_video)

        self.search_latter_word = 0
        self.search_word = ''
        self.timer_video_found.stop()
        self.ui.Check_Video_Button.setEnabled(True)
        self.ui.Choose_Folder_Button.setEnabled(True)
        self.ui.Download_Button.setEnabled(True)
        self.ui.Name_Program_Label_2.setText("Video found. Select quality and start downloading.")
        self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(0, 205, 0);')
        self.ui.ButtonsPanel.setMinimumHeight(111)
        self.ui.ButtonsPanel.setMaximumHeight(111)

    @pyqtSlot()
    def no_internet_on_pc(self):
        """ Signal updating UI when no internet on PC. """
        self.timer_video_found.stop()
        self.ui.Check_Video_Button.setEnabled(True)
        self.ui.Choose_Folder_Button.setEnabled(True)
        self.ui.Download_Button.setEnabled(True)
        self.ui.Name_Program_Label_2.setText("ERROR: Not Internet in computer.")
        self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(205, 0, 0);')

    @pyqtSlot()
    def not_valid_url_address(self):
        """ Signal updating UI when no valid url address. """
        self.timer_video_found.stop()
        self.ui.Check_Video_Button.setEnabled(True)
        self.ui.Choose_Folder_Button.setEnabled(True)
        self.ui.Download_Button.setEnabled(True)
        self.ui.Name_Program_Label_2.setText("ERROR: Please enter a valid URL.")
        self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(205, 0, 0);')

    @pyqtSlot()
    def _on_preview_loaded(self, reply):
        """ Helper function for updating the UI label. """
        img = QImage()
        if img.loadFromData(reply.readAll()):
            self.ui.Prew_Label.setPixmap(QPixmap.fromImage(img))
            self.ui.Prew_Label.show()
        else:
            self.ui.Prew_Label.clear()
        reply.deleteLater()

    @pyqtSlot()
    def on_video_not_found(self):
        """ Signal processing when video is not found. """
        self.search_latter_word = 0
        self.search_word = ''
        self.timer_video_found.stop()
        self.ui.Check_Video_Button.setEnabled(True)
        self.ui.Choose_Folder_Button.setEnabled(True)
        self.ui.Download_Button.setEnabled(True)
        self.ui.Name_Program_Label_2.setText("ERROR: Video not found.")
        self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(205, 0, 0);')

    @pyqtSlot(str)
    def on_video_error(self, error: str):
        """ Signal processing when error find video. """
        self.search_latter_word = 0
        self.search_word = ''
        self.timer_video_found.stop()
        self.ui.Check_Video_Button.setEnabled(True)
        self.ui.Choose_Folder_Button.setEnabled(True)
        self.ui.Download_Button.setEnabled(True)
        self.ui.Name_Program_Label_2.setText(f"ERROR - {error}")
        self.ui.Name_Program_Label_2.setStyleSheet('font: 10pt "Rubik Medium"; color: rgb(205, 0, 0);')

    @pyqtSlot(float)
    def update_progress_bar(self, progress: float):
        """ Progress bar update function in GUI. """
        if progress > self.percent_loading:
            self.percent_loading = int(progress)
            self.ui.progressBar.setValue(self.percent_loading)
        if progress == 100:
            self.percent_loading = 0

    @pyqtSlot()
    def on_download_completed(self):
        """ Function to complete download progress. """
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

    @pyqtSlot(str)
    def on_error_progress(self, error: str):
        """ Function error download progress. """
        self.delete_info_video()
        self.ui.Check_Video_Button.setEnabled(True)
        self.ui.Choose_Folder_Button.setEnabled(True)
        self.ui.Name_Program_Label_2.setText(f'ERROR: {error}')
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