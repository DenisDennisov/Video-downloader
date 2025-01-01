from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from PyQt5.QtTest import QSignalSpy

import src.downloader as downloader


class TestCheckPath(TestCase):
    """ Test func check_path. """
    def test_empty_arg_check_path(self):
        with self.assertRaises(TypeError) as e:
            downloader.check_path()
        self.assertEqual("check_path() missing 3 required positional arguments: 'path', 'file_class', "
                         "and 'name_channel'", e.exception.args[0])

    def test_one_arg_check_path(self):
        with self.assertRaises(TypeError) as e:
            downloader.check_path('hello', '')
        self.assertEqual("check_path() missing 1 required positional argument: 'name_channel'", e.exception.args[0])

    def test_empty_pass_arg_check_path(self):
        self.assertEqual(downloader.check_path('', '', ''), '/video download///')

    def test_three_arg_check_path(self):
        self.assertEqual(downloader.check_path('How', 'to', 'download'), 'How/video download/to/download/')


class TestRemoveNameVideoSimbols(TestCase):
    """ Test func remove_name_video_simbols. """
    def test_empty_remove_name_video_simbols(self):
        self.assertEqual(downloader.remove_name_video_simbols(''), '')

    def test_clear_text_remove_name_video_simbols(self):
        self.assertEqual(downloader.remove_name_video_simbols('How to download video'), 'How to download video')

    def test_text_remove_name_video_simbols(self):
        self.assertEqual(downloader.remove_name_video_simbols('How! to download video??!'), 'How to download video')

    def test_not_text_remove_name_video_simbols(self):
        self.assertEqual(downloader.remove_name_video_simbols(134), '134')


class TestFindVideo(TestCase):
    """ Test class FindVideo. """

    @patch('yt_dlp.YoutubeDL')
    def test_find_video_emits_signal(self, mock_ytdl):
        mock_ytdl.return_value.extract_info.return_value = {
            "link": "https://www.youtube.com/",
            "quality": "720p"
        }

        video_finder = downloader.FindVideo('https://www.youtube.com/', '720p')
        spy = QSignalSpy(video_finder.video_found_signal)

        video_finder.info_about_video()
        self.assertEqual(len(spy), 1)

    @patch('yt_dlp.YoutubeDL')
    def test_filed_find_video_emits_signal(self, mock_ytdl):
        mock_ytdl.return_value.extract_info.return_value = {
            "link": "https://www.youtube.com/",
            "quality": "720p"
        }

        video_finder = downloader.FindVideo('https://www.youtube.com/', '720p')
        spy = QSignalSpy(video_finder.video_not_found_signal)

        video_finder.info_about_video()
        self.assertEqual(len(spy), 0)


class TestDownloadVideo(TestCase):
    """ Test class DownloadVideo. """

    @patch('yt_dlp.YoutubeDL')
    def test_download_video_emits_signal(self, mock_ytdl):
        mock_ytdl.return_value.extract_info.return_value = {
            "link": "https://www.youtube.com/",
            "quality": "720p",
            "name_video": "Name video",
            "name_channel": "Name channel"
        }

        video_download = downloader.DownloadVideo('https://www.youtube.com/', '720p', 'Name video', 'Name channel')
        spy = QSignalSpy(video_download.completion_signal)

        video_download.starting_download()
        self.assertEqual(len(spy), 1)

    @patch('yt_dlp.YoutubeDL')
    def test_filed_download_video_emits_signal(self, mock_ytdl):
        mock_ytdl.return_value.extract_info.return_value = {
            "link": "https://www.youtube.com/",
            "quality": "720p",
            "name_video": "Name video",
            "name_channel": "Name channel"
        }

        video_download = downloader.DownloadVideo('https://www.youtube.com/', '720p', 'Name video', 'Name channel')
        spy = QSignalSpy(video_download.error_signal)

        video_download.starting_download()
        self.assertEqual(len(spy), 0)


if __name__ == "__main__":
    main()
