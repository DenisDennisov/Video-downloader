class LinkVideoInfo:
    """ Class storing state information about video for processing video controller. """
    def __init__(self):
        self.url: None | str = None
        self.quality: None | str = None
        self.name_video: None | str = None
        self.name_channel: None | str = None
        self.description_video: None | str = None
        self.preview_video: None | str = None

    def clear_video_info(self):
        """ Clear information about find video. """
        self.url = None
        self.quality = None
        self.name_video = None
        self.name_channel = None
        self.description_video = None
        self.preview_video = None
