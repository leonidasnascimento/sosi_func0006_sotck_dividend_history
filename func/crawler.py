import urllib3
import requests
import locale

from datetime import datetime
from .model.stock_history import (Stock, History) 
from bs4 import (BeautifulSoup, Tag)
from typing import List

class Crawler:
    #Properties
    target_url: str
    unformatted_target_url: str
    start_timestamp: int
    end_timestamp: int
    
    # Constants
    default_locale: str = "en_US.UTF-8"
    full_date_parse_str: str = "%d/%m/%Y %H:%M:%S"
    short_date_parse_str: str = "%d/%m/%Y"
    
    def __init__(self, _target_url: str, _start_timestamp: int, _end_timestamp: int):
        self.unformatted_target_url = _target_url
        self.start_timestamp = _start_timestamp
        self.end_timestamp = _end_timestamp
        pass

    def get_history(self, _stock_code: str) -> Stock:
        self.target_url = self.unformatted_target_url.format(_stock_code, self.start_timestamp, self.end_timestamp)

        proc_date_time: str = datetime.now().strftime(self.full_date_parse_str)
        start_date_aux: str = datetime.fromtimestamp(self.start_timestamp).strftime(self.short_date_parse_str)
        end_date_aux: str = datetime.fromtimestamp(self.end_timestamp).strftime(self.short_date_parse_str)
        stock_obj: Stock = Stock(_stock_code, proc_date_time, start_date_aux, end_date_aux, [])
        
        headers = {
            'upgrade-insecure-requests': "1",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            'cache-control': "no-cache",
            'postman-token': "146ba02b-dc25-fb1a-9fbc-a8df1248db26"
        }

        res = requests.get(self.target_url, headers=headers)
        soup = BeautifulSoup(res.content)

        historical_prices: Tag = soup.find("table", attrs={"data-test":"historical-prices"})
        if not historical_prices:
            return stock_obj
         
        prices: List[Tag] = historical_prices.select("tbody>tr")
        if not prices:
            return stock_obj

        for price in prices:
            price_col: List[Tag] = price.find_all("td")
            if not price_col:
                return

            # Right way of formatting date is right bellow. We decided to use a work around to speed thing up.
            # locale.setlocale(locale.LC_ALL, self.default_locale)
            # datetime.strptime(price_col[0].text, "%d de %b de %Y").strftime(slef.short_date_parse_str)
            
            # Date formating work around
            date: str = self.format_brl_date_str(price_col[0].text)

            # Earnings
            earnAux: Tag = price_col[1].find("strong")
            earnig: float = float(self.format_str_number(earnAux.text)) if earnAux else 0.00
            
            # Description
            descTag: Tag = price_col[1].find("span")
            description: str = descTag.text if descTag else ""     
                        
            hist: History = History(date, earnig, description)
            stock_obj.history.append(hist)
            pass
        
        print(stock_obj.__dict__)
        return stock_obj

    def format_brl_date_str(self, str_value: str) -> str:
        if str_value is None:
            return ""

        if str_value == "":
            return ""
        
        arr_date: list = str_value.split(" de ")
        month_num: int = 0 

        if len(arr_date) < 3:
            return ""

        if str(arr_date[1]).lower() == "jan":
            month_num = 1
        elif str(arr_date[1]).lower() == "fev":
            month_num = 2
        elif str(arr_date[1]).lower() == "mar":
            month_num = 3
        elif str(arr_date[1]).lower() == "abr":
            month_num = 4
        elif str(arr_date[1]).lower() == "mai":
            month_num = 5
        elif str(arr_date[1]).lower() == "jun":
            month_num = 6
        elif str(arr_date[1]).lower() == "jul":
            month_num = 7
        elif str(arr_date[1]).lower() == "ago":
            month_num = 8
        elif str(arr_date[1]).lower() == "set":
            month_num = 9
        elif str(arr_date[1]).lower() == "out":
            month_num = 10
        elif str(arr_date[1]).lower() == "nov":
            month_num = 11
        elif str(arr_date[1]).lower() == "dez":
            month_num = 12

        return_date = datetime(int(arr_date[2]), month_num, int(arr_date[0]))
        return return_date.strftime(self.short_date_parse_str)

    def format_str_number(self, str_value: str) -> str:
        if str_value is None:
            return ""
        
        if str_value.find('-') > -1: 
            str_value = str_value.replace('-', '')
        
        if str_value == '':
            return "0"

        return str_value
    pass