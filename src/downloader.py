import os
import yt_dlp
from PyQt5 import QtCore

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

user_agent = os.getenv('USER_AGENT')


def set_user_agent() -> dict:
    headers = {'User-Agent': user_agent}

    return headers


def check_path(path: str, file_class: str, name_channel: str) -> str:
    folder_path = path + '/video download/' + file_class + '/' + remove_name_video_simbols(name_channel) + '/'

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return folder_path


def remove_name_video_simbols(name_video: str) -> str:
    try:
        remove_symbols = '!@#$%^&*()/|=+-_:;?><}{[]№".,'

        for symbol in remove_symbols:
            name_video = name_video.replace(symbol, '')

    except OSError:
        pass

    return name_video


class FindVideo(QtCore.QObject):
    video_found_signal = QtCore.pyqtSignal()
    video_not_found_signal = QtCore.pyqtSignal()

    def __init__(self, link: str, quality: str):
        super().__init__()

        self.link = link
        self.quality = quality

        self.name_video = None
        self.name_channel = None
        self.description_video = None
        self.preview_video = None

    def info_about_video(self):
        ydl_opts = {'quiet': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.link, download=False)

                self.name_video = remove_name_video_simbols(info.get('title', 'Unknown Title'))
                self.name_channel = info.get('uploader', 'Unknown Channel')
                self.description_video = info.get('description', 'No Description')
                self.preview_video = info.get('thumbnail', '')

                self.video_found_signal.emit()

        except Exception:
            self.video_not_found_signal.emit()


class DownloadVideo(QtCore.QObject):
    progress_signal = QtCore.pyqtSignal(float)
    completion_signal = QtCore.pyqtSignal()
    error_signal = QtCore.pyqtSignal()

    def __init__(self, link: str, quality: str, name_video: str, name_channel: str):
        super().__init__()

        self.get_path_catalog = None
        self.save_path = None
        self.output_path = None

        self.link = link
        self.quality = quality

        self.name_video = name_video
        self.name_channel = name_channel

        self.output_file = self.output_name_file()

    def output_name_file(self):
        return f'{self.name_video}.mp4'

    def get_download_folder(self):
        get_path_catalog = os.path.dirname(os.path.abspath('../app.py'))
        save_path = check_path(get_path_catalog, 'video', self.name_channel)
        output_path = os.path.abspath(save_path + self.output_file)

        return get_path_catalog, save_path, output_path

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            progress = d['_percent_str'].strip('%')
            self.progress_signal.emit(float(progress))

    def starting_download(self):
        self.get_path_catalog, self.save_path, self.output_path = self.get_download_folder()

        ydl_opts = {
            'format': f'bestvideo[ext=mp4][height<={self.quality}]+bestaudio[ext=m4a]/best[ext=mp4]',
            'outtmpl': f'{self.save_path}/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
            'progress_hooks': [self.progress_hook],
            'n_threads': 4,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:

                if not os.path.isfile(self.output_path):
                    ydl.download([self.link])

                self.completion_signal.emit()

        except Exception:
            self.error_signal.emit()

