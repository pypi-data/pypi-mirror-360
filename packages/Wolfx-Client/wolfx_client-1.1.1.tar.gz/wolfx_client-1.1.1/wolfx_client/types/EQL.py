from typing import Union

class Earthquake:
    _type = "jma_eqlist"
    title: str
    """地震情報の種類"""
    eventID: str
    """イベントID"""
    time: str
    """発生時刻"""
    time_full: str
    """発生時刻（詳細）"""
    location: str
    """発生場所"""
    magnitude: Union[str, float]
    """マグニチュード"""
    shindo: Union[str, int]
    """最大震度"""
    depth: str
    """深さ"""
    latitude: Union[str, float]
    """緯度"""
    longitude: Union[str, float]
    """経度"""
    info: str
    """津波情報"""
    
    def __init__(self, data: dict):
        self.title = data["Title"]
        self.eventID = data["EventID"]
        self.time = data["time"]
        self.time_full = data["time_full"]
        self.location = data["location"]
        self.magnitude = data["magnitude"]
        self.shindo = data["shindo"]
        self.depth = data["depth"]
        self.latitude = data["latitude"]
        self.longitude = data["longitude"]
        self.info = data["info"]

class EarthquakeData:
    _type = "jma_eqlist"
    """IDは常にjma_eqlistです。"""
    data: dict[str, Earthquake]
    """地震情報（NoXをキーとする辞書）"""
    md5: str
    """MD5ハッシュ"""

    def __init__(self, data: dict):
        self.md5 = data["md5"]
        self.data = {}
        
        # md5以外のキーはすべて地震データ
        for key, value in data.items():
            if key != "md5":
                self.data[key] = Earthquake(value)
        