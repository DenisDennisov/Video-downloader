"""
The function is not called directly! It is called from workers a subprocess and from tests.
"""


def extract_info_about_video(url: str, user_agent: str) -> list:
    """ A function for searching video information using the yt-dlp library link. """
    return ['-m', 'yt_dlp',
     '--dump-json',
     '--quiet',
     '--no-warnings',
     '--add-header', f'User-Agent: {user_agent}',
     url]
