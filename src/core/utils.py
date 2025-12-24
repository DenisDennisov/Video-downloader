import os
from pathlib import Path

import requests
from urllib.parse import urlparse

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())


class SymbolVideoNameCleaner:
    """ Class for removing characters from video. """
    def __init__(self, symbols_to_remove: str = '!@#$%^&*()/|=+-_:;?><}{[]№".,'):
        self.symbols = symbols_to_remove

    def clean_video(self, words: str) -> str:
        """ Removing characters. """
        if not isinstance(words, str):
            return str(words)
        table = str.maketrans('', '', self.symbols)
        return words.translate(table).strip()


class DefaultUserAgentProvider:
    """ Class user agent receiving. """
    def __init__(self, user_agent: str = os.getenv('USER_AGENT')):
        self._user_agent = user_agent

    def get_user_agent(self) -> str:
        """ Get user agent. """
        return self._user_agent


class CheckerInternetPC:
    """Class checking internet on PC. """
    def __init__(self, valid_url: str = 'https://google.com/'):
        self._valid_url = valid_url

    def check_internet(self) -> bool:
        """ Check internet on the pc. """
        try:
            res_internet = requests.get(self._valid_url, timeout=20)
            if res_internet.status_code == 200:
                return True
        except (requests.RequestException, OSError):
            return False


class CheckerValidLink:
    """ Class for removing characters from video. """
    def __init__(self, file_resources="video_resources.txt"):
        self._file_resources = file_resources
        self._ROOT_DIRECTORY = self._get_file_resources_dir()
        self._path_to_video_resources = next(self._ROOT_DIRECTORY.rglob(f"{self._file_resources}"), None)
        self.allowed_hosts: list = []

        self._load_file_allowed_links()

    @staticmethod
    def _get_file_resources_dir() -> Path:
        """ Get root directory file resources. """
        return next(
            p for p in Path(__file__).resolve().parents if (p / '.git').exists() or (p / 'pyproject.toml').exists())

    def _load_file_allowed_links(self):
        """ Loading files with video allowed resources yt-dlp. """

        with open(f'{self._path_to_video_resources}', 'r', encoding='utf-8') as file:
            text = file.read().split()
        for sentence in text:
            sentence = sentence.strip()
            if sentence:
                self.allowed_hosts.append(sentence)

    def valid_link(self, link: str) -> bool:
        """ Check valid link to download video. """
        try:
            parsed = urlparse(link).netloc.replace('www.', '')
            if parsed in self.allowed_hosts:
                return True
            return False
        except Exception as e:
            return False
