import os
import sys
import subprocess

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject

from src.core.download_video import download_process_video
from src.core.utils import (SymbolVideoNameCleaner, DefaultUserAgentProvider,
                            CheckerInternetPC, CheckerValidLink)


class DownloadVideoWorker(QObject):
    """ Video upload class. """
    progress_signal = pyqtSignal(float)
    completion_signal = pyqtSignal()
    download_error_signal = pyqtSignal(str)
    internet_error_signal = pyqtSignal()
    not_valid_link_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._clean_symbols_name = SymbolVideoNameCleaner()
        self._get_headers = DefaultUserAgentProvider()
        self.check_internet = CheckerInternetPC()
        self.check_valid_link = CheckerValidLink()
        self.process_download_video = None

    def check_path(self, path: str, file_class: str, name_channel: str) -> str:
        """ Check the download folder. """
        folder_path = f"{path}/video download/{file_class}/{self._clean_symbols_name.clean_video(name_channel)}/"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return folder_path

    def get_download_folder(self, name_video: str, name_channel: str) -> (str, str, str):
        """ Get the standard path to the folder for saving videos. """
        get_path_catalog = os.path.dirname(os.path.abspath('../main.py'))
        save_path = self.check_path(get_path_catalog, 'video', str(name_channel))
        output_path = os.path.abspath(f'{save_path}{name_video}.mp4')
        return get_path_catalog, save_path, output_path

    def _progress_hook(self, loading_percent: str):
        """ Transferring the loading percent to the progress bar of the GUI. """
        if '[download]' in loading_percent and '%' in loading_percent:
            try:
                percent = float(loading_percent.split('%')[0].split()[-1])
                self.progress_signal.emit(percent)      #type: ignore
            except (ValueError, IndexError):
                pass

    def stop_process_download_video(self):
        """ Stop subprocess to download video. """
        if self.process_download_video and self.process_download_video.poll() is None:
            self.process_download_video.terminate()
            self.process_download_video.kill()

    @pyqtSlot(str, str, str, str)
    def starting_download(self,
                          link_video: str,
                          quality_video: str,
                          name_video: str,
                          name_channel: str):
        """ Uploading files and gluing video and audio. """
        if not self.check_internet.check_internet():
            self.internet_error_signal.emit()        #type: ignore
            return False
        # !! I started yt-dlp as a separate subprocess because it conflicts directly with QObject.
        # The error is generated at the OS/CRT (C Runtime) level. !!
        try:
            get_path_catalog, save_path, output_path = self.get_download_folder(name_video, name_channel)
            if os.path.isfile(output_path):
                self.completion_signal.emit()       #type: ignore
                return False

            safe_title = self._clean_symbols_name.clean_video(name_video)
            output_path = os.path.join(save_path, f"{safe_title}.%(ext)s")

            params = download_process_video(url=link_video,
                                            quality=quality_video,
                                            user_agent=self._get_headers.get_user_agent(),
                                            output_path=output_path)
            self.process_download_video = subprocess.Popen(
                [sys.executable, *params],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                universal_newlines=True
            )
            while True:
                loading_percent = self.process_download_video.stdout.readline()
                if not loading_percent and self.process_download_video.poll() is not None:
                    break
                if loading_percent:
                    self._progress_hook(loading_percent)

            if self.process_download_video.returncode == 0:
                self.completion_signal.emit()           #type: ignore
            else:
                self.download_error_signal.emit(        # type: ignore
                    self.process_download_video.stderr.read() or "Unknown error")

        except Exception as e:
            self.download_error_signal.emit(str(e))     #type: ignore
        finally:
            self.stop_process_download_video()
