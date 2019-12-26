from typing import List

class History:
    earning: float
    date: str
    description: str

    def __init__(self, _date:str,  _earning: float, _desc: str):
        self.date = _date
        self.earning = _earning
        self.description = _desc
        pass
    pass

class Stock:
    code: str
    processing_date: str
    start_date: str
    end_date: str
    history: List[History] = []

    def __init__(self, _code: str, _proc_date: str, _start_date: str, _end_date: str, _hist: List[History]):
        self.code = _code
        self.processing_date = _proc_date
        self.start_date = _start_date
        self.end_date = _end_date
        self.history = _hist
        pass
    pass
