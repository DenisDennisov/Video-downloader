import sys
import json
import subprocess

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject

from src.core.find_video import extract_info_about_video
from src.core.utils import (SymbolVideoNameCleaner, DefaultUserAgentProvider,
                            CheckerInternetPC, CheckerValidLink)


class FindVideoWorker(QObject):
    """ Video find class. """
    video_found_signal = pyqtSignal(str, str, str, str)
    video_not_found_signal = pyqtSignal()
    video_found_error_signal = pyqtSignal(str)
    internet_error_signal = pyqtSignal()
    not_valid_link_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._clean_symbols_name = SymbolVideoNameCleaner()
        self._get_headers = DefaultUserAgentProvider()
        self.check_internet = CheckerInternetPC()
        self.check_valid_link = CheckerValidLink()
        self.process_find_video = None

    def stop_process_find_video(self):
        """ Stop subprocess to find video. """
        if self.process_find_video and self.process_find_video.poll() is None:
            self.process_find_video.terminate()
            self.process_find_video.kill()

    @pyqtSlot(str)
    def get_info_about_video(self, link_video: str):
        """ Get information about video: (video title, channel name, video description and preview). """
        if not self.check_internet.check_internet():
            self.internet_error_signal.emit()        #type: ignore
            return False
        if not self.check_valid_link.valid_link(link_video):
            self.not_valid_link_signal.emit()      #type: ignore
            return False
        # !! I started yt-dlp as a separate subprocess because it conflicts directly with QObject.
        # The error is generated at the OS/CRT (C Runtime) level. !!
        try:
            params = extract_info_about_video(url=link_video, user_agent=self._get_headers.get_user_agent())
            self.process_find_video = subprocess.Popen(
                [sys.executable, *params],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                universal_newlines=True
            )
            stdout, stderr = self.process_find_video.communicate(timeout=15)

            if self.process_find_video.returncode == 0:
                info = json.loads(stdout)
                name_video = self._clean_symbols_name.clean_video(info.get('title', 'Unknown Title'))
                name_channel = info.get('uploader', 'Unknown Channel')
                description_video = info.get('description', 'No Description')
                preview_video = info.get('thumbnail', '')
                self.video_found_signal.emit(name_video, name_channel, description_video, preview_video)  # type: ignore
            else:
                self.video_not_found_signal.emit()          # type: ignore

        except Exception as e:
            error_type = type(e).__name__
            if hasattr(e, 'timeout'):
                error_msg = f"timed out after {e.timeout} seconds."
            elif hasattr(e, 'stderr') and e.stderr:
                error_msg = e.stderr.decode().strip()
            else:
                error_msg = str(e)
            self.video_found_error_signal.emit(str(f"{error_type}: {error_msg}"))      # type: ignore
        finally:
            self.stop_process_find_video()
