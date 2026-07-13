from .obj import Object
from .drm import ContentProtection
from crunpyroll.types import SubtitlesStream
from ..utils import (
    parse_segments,
    parseProtectionBlock
)

from typing import List, Dict

import xmltodict


class Manifest(Object):
    """
    Info about a manifest.

    Parameters:
        video_streams (List of :obj:`~crunpyroll.types.ManifestVideoStream`):
            List of every video stream available.

        audio_streams (List of :obj:`~crunpyroll.types.ManifestAudioStream`):
            List of every audio stream available.

        subs_streams (List of :obj:`~crunpyroll.types.SubtitlesStream`):
            List of every subtitle stream available

        content_protection (:obj:`~crunpyroll.types.ContentProtection`):
            Info about Content Protection (DRM).

        plain (``str``):
            Plain version of the manifest (XML).
            Useful for external downloader tools.
    """

    def __init__(self, data: Dict):
        self.video_streams: List["ManifestVideoStream"] = data.get("video_streams")
        self.audio_streams: List["ManifestAudioStream"] = data.get("audio_streams")
        self.sub_streams: List["SubtitlesStream"] = data.get("subs_streams")
        self.content_protection: "ContentProtection" = ContentProtection(data.get("content_protection"))
        self.plain: str = data.get("plain")

    @classmethod
    def parse(cls, obj: str):
        data = {}
        data["plain"] = obj
        data["video_streams"] = []
        data["audio_streams"] = []
        data["subs_streams"] = []
        data["content_protection"] = {}
        manifest = xmltodict.parse(obj)
        for aset in manifest["MPD"]["Period"]["AdaptationSet"]:
            template = None
            ## some streams, like "GR09CXQMJ" don't have a Segment template, so we need to handle it as optional
            if "SegmentTemplate" in aset:
                template = aset["SegmentTemplate"]

            global_protection = parseProtectionBlock(aset)
            if global_protection is not None:
                data["content_protection"] = global_protection

            mimeType = aset.get("@mimeType") or aset.get("@mime_Type") or aset.get("@mime_type")

            # in some cases it might not be a dict, but a single element
            representations = aset["Representation"]
            for repr in representations if isinstance(representations, list) else [representations]:
                if mimeType.startswith("text/vtt"):
                    repr = aset["Representation"]
                    stream = SubtitlesStream(dict(format='vtt', language=aset["@lang"], url=repr["BaseURL"]))
                    data["subs_streams"].append(stream)
                elif mimeType.startswith("audio/"):
                    stream = ManifestAudioStream.parse(repr, template)
                    data["audio_streams"].append(stream)
                elif mimeType.startswith("video/"):
                    stream = ManifestVideoStream.parse(repr, template)
                    data["video_streams"].append(stream)
                    data["audio_streams"].append(stream)

                # some streams, like "GR09CXQMJ", have one per representation, not a more global protection area
                # todo? maybe support per stream protections
                repr_protection = parseProtectionBlock(repr)
                if repr_protection is not None:
                    data["content_protection"] = repr_protection

        return cls(data)


class ManifestVideoStream(Object):
    """
    Info about a manifest video stream.

    Parameters:
        codecs (``str``):
            Codecs of the video stream.

        width (``int``):
            Width of the video stream.

        height (``int``):
            Height of the video stream.
        
        bitrate (``int``):
            Bitrate of the video stream.

        segments (List of ``str``):
            Each segment URL of the video stream.
    """

    def __init__(self, data: Dict):
        self.codecs: str = data.get("codecs")
        self.width: int = data.get("width")
        self.height: int = data.get("height")
        self.bitrate: int = data.get("bitrate")
        self.segments: List[str] = data.get("segments")

    @classmethod
    def parse(cls, obj: Dict, template: Dict = None):
        data = {}
        data["codecs"] = obj["@codecs"]
        data["width"] = int(obj["@width"])
        data["height"] = int(obj["@height"])
        data["bitrate"] = int(obj["@bandwidth"])
        data["segments"] = parse_segments(obj, template)
        return cls(data)


class ManifestAudioStream(Object):
    """
    Info about a manifest audio stream.

    Parameters:
        codecs (``str``):
            Codecs of the audio stream.
        
        bitrate (``int``):
            Bitrate of the audio stream.

        segments (List of ``str``):
            Each segment URL of the audio stream.
    """

    def __init__(self, data: Dict):
        self.codecs: str = data.get("codecs")
        self.bitrate: int = data.get("bitrate")
        self.segments: List[str] = data.get("segments")

    @classmethod
    def parse(cls, obj: Dict, template: Dict):
        data = {}
        data["codecs"] = obj["@codecs"]
        data["bitrate"] = int(obj["@bandwidth"])
        data["segments"] = parse_segments(obj, template)
        return cls(data)
