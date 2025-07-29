class Heartbeat:
    _type = "heartbeat"
    ver: int
    _id: str
    timestamp: int

    def __init__(self, data):
        self.ver = data.get("ver")
        self._id = data.get("id")
        self.timestamp = data.get("timestamp")