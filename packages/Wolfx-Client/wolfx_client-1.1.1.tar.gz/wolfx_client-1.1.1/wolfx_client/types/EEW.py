from typing import Union, Literal

class EEWIssue:
    """緊急地震速報の発表元と発生状況"""
    Source: str
    """緊急地震速報の発表元"""
    Status: str
    """緊急地震速報の発生状況"""
    
    def __init__(self, data: dict):
        self.Source = data["Source"]
        self.Status = data["Status"]    

class EEWAccuracy:
    """震央の精度等の情報"""
    Epicenter: str
    """震央の精度"""
    Depth: str
    """震源の深さの精度"""
    Magnitude: str
    """マグニチュードの精度"""
    
    def __init__(self, **data):
        self.Epicenter = data["Epicenter"]
        self.Depth = data["Depth"]
        self.Magnitude = data["Magnitude"]

class EEWMaxIntChange:
    String: str
    """最大震度の変更に関する説明"""
    Reason: str
    """最大震度の変更理由"""
    
    def __init__(self, **data):
        self.String = data["String"]
        self.Reason = data["Reason"]   
    
class EEWWarnArea:
    Chiiki: str
    """警報区分"""
    Shindo1: str
    """最大震度"""
    Shindo2: str
    """考えられる最小震度"""
    Time: str
    """発表時刻"""
    Type: Literal["警報", "予報"]
    """警報種別"""
    Arrive: bool
    """到達したかどうか"""
    
    def __init__(self, **data):
        self.Chiiki = data["Chiiki"]
        self.Shindo1 = data["Shindo1"]
        self.Shindo2 = data["Shindo2"]
        self.Time = data["Time"]
        self.Type = data["Type"]
        self.Arrive = data["Arrive"]

class EEW:
    """
    気象庁が発表する緊急地震速報をリアルタイムで取得。
    """
    _type = "jma_eew"
    """タイプは常にjma_eewです。"""
    title: str
    """緊急地震速報タイトル"""
    CodeType: str
    """緊急地震速報の説明"""
    Issue: EEWIssue
    """地震情報の発信情報"""
    EventID: int
    """地震情報のイベントID"""
    Serial: int
    """報数"""
    AnnouncedTime: str
    """発表時刻"""
    OriginTime: str
    """地震発生時刻"""
    Hypocenter: str
    """震源地"""
    Latitude: float
    """緯度"""
    Longitude: float
    """経度"""
    Magnitude: float
    """マグニチュード"""
    Depth: Union[float, int]
    """深さ"""
    MaxIntensity: Union[str, int]
    """最大震度"""
    Accuracy: EEWAccuracy
    """震央の精度等の情報"""
    
    MaxIntChange: EEWMaxIntChange
    """最大震度の変更に関する情報"""

    warnArea: list[EEWWarnArea] | None
    """警報エリア"""
    
    isSea: bool
    """海域での地震かどうか"""

    isTraining: bool
    """訓練かどうか"""
    isAssumption: bool
    """仮定震源かどうか (PLUM/レベル/IPF法)"""

    isWarn: bool
    """警報かどうか"""

    isFinal: bool
    """最終情報かどうか"""
    
    isCancel: bool
    """キャンセル報かどうか"""

    OriginalText: str
    """気象庁からの原文"""

    def __init__(self, data: dict):
        self.Title = data["Title"]
        self.CodeType = data["CodeType"]
        self.Issue = EEWIssue(data["Issue"])
        self.EventID = data["EventID"]
        self.Serial = data["Serial"]
        self.AnnouncedTime = data["AnnouncedTime"]
        self.OriginTime = data["OriginTime"]
        self.Hypocenter = data["Hypocenter"]
        self.Latitude = data["Latitude"]
        self.Longitude = data["Longitude"]
        self.Magunitude = data["Magunitude"]
        self.Depth = data["Depth"]
        self.MaxIntensity = data["MaxIntensity"]
        self.Accuracy = EEWAccuracy(**data["Accuracy"])
        self.MaxIntChange = EEWMaxIntChange(**data["MaxIntChange"])
        self.WarnArea = [EEWWarnArea(**area) for area in data["WarnArea"]] if data["WarnArea"] else None
        self.isSea = data["isSea"]
        self.isTraining = data["isTraining"]
        self.isAssumption = data["isAssumption"]
        self.isWarn = data["isWarn"]
        self.isFinal = data["isFinal"]
        self.isCancel = data["isCancel"]
        self.OriginalText = data["OriginalText"]