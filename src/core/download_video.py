"""
The function is not called directly! It is called from workers a subprocess and from tests.
"""


def download_process_video(url: str, quality: str, user_agent: str, output_path: str) -> list:
    """ A function for downloading video information using the yt-dlp library link. """
    return ['-m', 'yt_dlp',
    '--output', output_path,
    '--format', f'bestvideo[ext=mp4][height<={quality}]+bestaudio[ext=m4a]/best[ext=mp4]',
    '--merge-output-format', 'mp4',
    '--no-warnings',
    '--newline',
    '--add-header', f'User-Agent: {user_agent}',
    url]
