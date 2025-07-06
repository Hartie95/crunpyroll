from curses.ascii import isdigit

from .obj import Object
from .content import Content
from .images import Images

from ..utils import str_to_date

from datetime import datetime
from typing import List, Dict

class Version(Content):
    """
    Info about an episode.

    Parameters:
        media_id (``str``):
            Unique identifier, todo find use

        content_id (``str``):
            Unique identifier of for the media content used to get the streams

        season_id (``str``):
            Unique identifier of the season of this episode.

        subtitle_locales (List of ``str``):
            List containing language codes of available subtitles.

        audio_locale (``str``):
            Language code of the audio.

        is_original (``bool``):
            True, if this episode is the original dub

        is_premium (``bool``):
            True, if this episode is available to premium users only.

        variant (``str``):
            TODO find out what its used for

        roles (List of ``str``)
            contains "Main" if its the main video, often original. Contains dub for additional dubs
    """
    def __init__(self, data: Dict):
        self.media_id: str = data.get("media_guid")
        self.content_id: str = data.get("guid")
        self.season_id: str = data.get("season_guid")
        self.audio_locale: str = data.get("audio_locale")
        self.is_original: bool = data.get("original")
        self.is_premium: bool = data.get("is_premium_only")
        self.variant: str = data.get("variant")
        self.roles: List[str] = data.get("roles")
