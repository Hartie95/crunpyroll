from typing import Optional, List, Dict
from datetime import datetime
from uuid import uuid4

PUBLIC_TOKEN = "cmpzMGx0eDBkYndrbGl3eGR6ZGY6NFY3cmYyMS1VRlhlWi01WEFkMFhfUVB3cjFndV9pMXM="
USER_AGENT = 'Crunchyroll/ANDROIDTV/3.65.0_22347 (Android 16; en-US; sdk_gphone64_x86_64)'

APP_VERSION = "3.59.0"

DEVICE_NAME = "iPhone"
DEVICE_TYPE = "iPhone 14"
DEVICE_ID = str(uuid4())

WIDEVINE_UUID = "urn:uuid:edef8ba9-79d6-4ace-a3c8-27dcd51d21ed"
PLAYREADY_UUID = "urn:uuid:9a04f079-9840-4286-ab92-e65be0885f95"
SHARED_UUID = "urn:mpeg:dash:mp4protection:2011"

def get_api_headers(headers: Optional[Dict]) -> Dict:
    return {
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "User-Agent": f"{USER_AGENT}",
    } | (headers or {})

def parse_segment(segments, segment, start_number, base_url, template, representation_id):
    repeat = int(segment.get("@r", 0)) + 1
    duration = int(segment.get("@d"))
    time += repeat * duration
    for _ in range(repeat):
        number = start_number + len(segments) - 1
        segment_url = format_segment_url(
            url=base_url + template["@media"],
            obj={
                "Number": str(number),
                "RepresentationID": representation_id
            }
        )
        segments.append(segment_url)

def parse_segments(repr: Dict, template: Dict = None) -> List[str]:
    time = 0
    segments = []
    base_url = repr["BaseURL"]
    representation_id = repr["@id"]
    if template is None:
        start_number = 1
        initialization_url = base_url
    else:
        start_number = int(template["@startNumber"])
        initialization_url = format_segment_url(
            url=base_url + template["@initialization"],
            obj={"RepresentationID": representation_id}
        )
    segments.append(initialization_url)

    if template is not None:
        segment_timeline = template["SegmentTimeline"]["S"]
        if segment_timeline is List:
            for segment in template["SegmentTimeline"]["S"]:
                parse_segment(segments, segment, start_number, base_url, template, representation_id)
        elif segment_timeline is Dict:
            parse_segment(segments, segment_timeline, start_number, base_url, template, representation_id)
    return segments

def parseProtectionBlock(sourceData:dict) -> Optional[dict]:
    if "ContentProtection" in sourceData:
        result = {}
        for drm in sourceData["ContentProtection"]:
            scheme_id_uri = drm["@schemeIdUri"]
            if scheme_id_uri == SHARED_UUID:
                shared_key_id = drm.get("@cenc:default_KID")
        for drm in sourceData["ContentProtection"]:
            scheme_id_uri = drm["@schemeIdUri"]
            if scheme_id_uri == WIDEVINE_UUID:
                result["widevine"] = {}

                pssh_data = drm["cenc:pssh"]
                if isinstance(pssh_data, dict):
                    pssh_data: str = pssh_data.get("#text")

                result["widevine"]["pssh"] = pssh_data
                if "@cenc:default_KID" in drm:
                    result["widevine"]["key_id"] = drm["@cenc:default_KID"]
                elif shared_key_id:
                    result["widevine"]["key_id"] = shared_key_id
            if scheme_id_uri == PLAYREADY_UUID:
                result["playready"] = {}

                pssh_data = drm["mspr:pro"]
                if isinstance(pssh_data, dict):
                    pssh_data: str = pssh_data.get("#text")
                result["playready"]["pssh"] = pssh_data
        return result
    return None

def format_segment_url(url: str, obj: Dict) -> str:
    for key, value in obj.items():
        url = url.replace(f"${key}$", value)
    return url

def get_date() -> datetime: 
    return datetime.utcnow()

def date_to_str(date: datetime) -> Optional[str]: 
    try:
        return "{}-{}-{}T{}:{}:{}Z".format(
            date.year, date.month,
            date.day, date.hour,
            date.minute, date.second
        )
    except Exception:
        return

def str_to_date(string: str) -> Optional[datetime]:
    try:
        return datetime.strptime(
            string,
            "%Y-%m-%dT%H:%M:%SZ"
        )
    except Exception:
        return
