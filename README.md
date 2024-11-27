# Video downloader v1.0.0
___
Application with interface for downloading videos from various resources, developed using the yt-dlp and PyQt5.
This application allows users to download videos from various sources in various formats and qualities using a graphical user interface (GUI). The yt-dlp library is used to download videos, and PyQt5 provides a user-friendly interface.
#### The application is created as a portfolio.

![Screenshot](https://github.com/DenisDennisov/Video-downloader/tree/main/images/video downloader.png)

## Requirements
___
- Python 3.8+
- [PyQt5](https://pypi.org/project/PyQt5/)
- [pyqt5-tools](https://pypi.org/project/pyqt5-tools/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [requests](https://pypi.org/project/requests/)
- [dotenv](https://github.com/theskumar/python-dotenv/)
- [colorama](https://pypi.org/project/colorama/)

## How to install
___
### 1. Clone repository

```bash
git clone https://github.com/DenisDennisov/Video-downloader.git
cd .../Video-downloader 
```

### 2. Install venv
```bash
python -m venv venv
```
### 3. Activate venv
```bash
venv\Scripts\activate
```
### 4. Install requirements.txt
```bash
pip install -r requirements.txt
```
### 5. Put your User Agent in .env file
```bash
USER_AGENT=YOUR_USER_AGENT
```
### 6. Launch app.py
```bash
python app.py
```
## How to use
___
* In the field: "Add link video..." insert video link and click the button: "Find video".     


* Wait for information about the found video. If you want to clear the information and add a new link, click the trash button and repeat the steps from point 1.


* Select the quality of the video you want to download.


* Click the button: "Download" and wait until the download is complete.  

#### The program will automatically create a directory of folders with the name of the channel and video in the project folder. If the video already exists, it will not be downloaded.

p.s. The project may have some bugs that will be improved over time.

## Resources from which you can download videos
___
#### File sharing services (video only):
- Dropbox, GoogleDrive, GoogleDrive:Folder, Yandex.Disk. 
#### Video hosting:
- 1tv, facebook, Video@Mail.Ru, Rutube, TikTok, Twitter, Vimeo, VK, Youtube, ZenYandex. 
#### Music: 
- Music@Mail.Ru, Yandex.Music.
#### [Source (click)](https://www.altlinux.org/Soft/yt-dlp)
#### p.s. There are problems with downloading YouTube videos from Russia.

## Additionally
Files with extensions ".ui" and ".qrc" have already been converted to ".py" format in the src folder.

## License
___
This project is licensed under the Apache-2.0 License - see the [LICENSE](https://github.com/DenisDennisov/Video-downloader?tab=Apache-2.0-1-ov-file#readme) file for details.
