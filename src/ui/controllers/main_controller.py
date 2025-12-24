import sys

from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication

from src.models.info_video import LinkVideoInfo
from src.ui.views.main_window import MainWindow
from src.ui.workers.find_video_worker import FindVideoWorker
from src.ui.workers.download_video_worker import DownloadVideoWorker


class MainController(QObject):
    """ Class that manages threads and signals. """
    start_check_video_signal = pyqtSignal(str)
    start_download_video_signal = pyqtSignal(str, str, str, str)

    def __init__(self):
        super().__init__()
        self._view = MainWindow()
        self._model = LinkVideoInfo()

        # I'm making 1 stream because video checking and downloading are done sequentially.
        self._thread_video = QThread()
        self._worker_check_video = FindVideoWorker()
        self._worker_download_video = DownloadVideoWorker()
        self._worker_check_video.moveToThread(self._thread_video)
        self._worker_download_video.moveToThread(self._thread_video)

        self._connect_signals_worker_check_video()
        self._connect_signals_worker_download_video()
        self._connect_signals_ui_buttons()

        self._thread_video.start()
        self._view.show()

    def _connect_signals_worker_check_video(self):
        """ Connecting video check worker signals. """
        self._worker_check_video.video_found_signal.connect(self._model_update_info_founded_video)
        self._worker_check_video.video_not_found_signal.connect(self._view.on_video_not_found)
        self._worker_check_video.video_found_error_signal.connect(self._view.on_video_error)
        self._worker_check_video.internet_error_signal.connect(self._view.no_internet_on_pc)
        self._worker_check_video.not_valid_link_signal.connect(self._view.not_valid_url_address)
        self.start_check_video_signal.connect(self._worker_check_video.get_info_about_video)          # type: ignore

    def _connect_signals_worker_download_video(self):
        """ Connecting video download worker signals. """
        self._worker_download_video.progress_signal.connect(self._view.update_progress_bar)
        self._worker_download_video.completion_signal.connect(self._view.on_download_completed)
        self._worker_download_video.download_error_signal.connect(self._view.on_error_progress)
        self._worker_download_video.internet_error_signal.connect(self._view.no_internet_on_pc)
        self._worker_download_video.not_valid_link_signal.connect(self._view.not_valid_url_address)
        self.start_download_video_signal.connect(self._worker_download_video.starting_download)       # type: ignore

    def _connect_signals_ui_buttons(self):
        """ Connecting the interface button signals. """
        self._view.ui.Close_MinimizeButton.clicked.connect(lambda: self._close_app_btn())
        self._view.ui.Roll_MinimizeButton.clicked.connect(lambda: self._view.showMinimized())
        self._view.ui.Choose_Folder_Button.clicked.connect(lambda: self._delete_info_video_btn())
        self._view.ui.Check_Video_Button.clicked.connect(lambda: self._start_check_video_btn())
        self._view.ui.Download_Button.clicked.connect(lambda: self._start_download_video_btn())

    @pyqtSlot()
    def _close_app_btn(self):
        """ Button close app. """
        if self._worker_check_video.process_find_video:
            self._worker_check_video.stop_process_find_video()
        if self._worker_download_video.process_download_video:
            self._worker_download_video.stop_process_download_video()

        if self._thread_video.isRunning():
            self._thread_video.quit()
        QApplication.instance().quit()
        sys.exit(0)

    @pyqtSlot()
    def _delete_info_video_btn(self):
        """ Logic clear information about founded video and sys messages. """
        self._model.clear_video_info()
        self._view.delete_info_video()

    @pyqtSlot()
    def _start_check_video_btn(self):
        """ Processing the Find video button click. If all filled fields are successfully checked,
            the search for information about the video begins. """
        get_url = self._view.get_url_video_info()
        if not get_url:
            return self._view.not_valid_url_address()
        self._model.url = get_url
        self.start_check_video_signal.emit(get_url)        # type: ignore
        self._view.update_ui_start_check_video()

    @pyqtSlot()
    def _start_download_video_btn(self):
        """ Start process downloading video. """
        if not self._model.url and not self._view.check_valid_url():
            self._view.not_valid_url_address()
        else:
            self.start_download_video_signal.emit(        # type: ignore
                self._model.url,
                self._view.get_quality_video_info(),
                self._model.name_video,
                self._model.name_channel
            )
            self._view.update_ui_start_download_video()


    @pyqtSlot(str, str, str, str)
    def _model_update_info_founded_video(self,
                                         name_video: str,
                                         name_channel: str,
                                         description_video: str,
                                         preview_video: str):
        """ Updating info about founded video in model class. """
        self._model.name_video = name_video
        self._model.name_channel = name_channel
        self._model.description_video = description_video
        self._model.preview_video = preview_video
        self._view.update_video_info(name_video, description_video, preview_video)

