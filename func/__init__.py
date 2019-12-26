import datetime
import logging
import azure.functions as func
import json
import pathlib
import threading
import time
import array
import requests

from .model.stock_history import (Stock, History)
from .crawler import Crawler
from typing import List
from dateutil.relativedelta import relativedelta
from configuration_manager.reader import reader

SETTINGS_FILE_PATH = pathlib.Path(
    __file__).parent.parent.__str__() + "//local.settings.json"

def main(func: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    try:
        logging.info("Timer job 'sosi_func0006_sotck_dividend_history' has begun")

        config_obj: reader = reader(SETTINGS_FILE_PATH, 'Values')
        post_service_url: str = config_obj.get_value("post_service_url")
        formatted_start_date: int = 0
        formatted_end_date: int = 0
        target_url: str = config_obj.get_value("target_url")
        stock_code_list_service_url: str = config_obj.get_value("stock_code_list_service_url")
        days_to_look_back: str = config_obj.get_value("days_to_look_back", "0")
        response: requests.Response = None
        stk_codes: array.array = {}
        date_parse_pattern: str = "%d/%m/%Y"
        
        # Crawling
        start_date: datetime.date = datetime.date.today() - relativedelta(days=int(days_to_look_back))
        formatted_start_date = int(time.mktime(start_date.timetuple()))
        formatted_end_date = int(time.mktime(datetime.date.today().timetuple()))

        logging.info("From {} to {}".format(start_date.strftime(date_parse_pattern), datetime.date.today().strftime(date_parse_pattern)))

        # Getting stock code list
        response = requests.request("GET", stock_code_list_service_url)
        stk_codes = json.loads(response.text)
        thread_lst: List[threading.Thread] = []
        
        for code in stk_codes:
            logging.info(code['stock'])
            
            # process_crawling(code['stock'], target_url, post_service_url, formatted_start_date, formatted_end_date)

            t_aux: threading.Thread = threading.Thread(target=process_crawling, args=(code['stock'], target_url, post_service_url, formatted_start_date, formatted_end_date))            
            thread_lst.append(t_aux)
        
            t_aux.start()
            pass
            
        # Wait 'till all threads are done
        for thread in thread_lst:
            if thread and thread.is_alive():
                thread.join()

        logging.info("Timer job is done. Waiting for the next execution time")

        pass
    except Exception as ex:
        error_log = '{} -> {}'
        logging.exception(error_log.format(utc_timestamp, str(ex)))
        pass
    pass

def invoke_url(url, json):
    headers = {
        'content-type': "application/json",
        'cache-control': "no-cache",
        'content-length': str(len(str(json).encode('utf-8')))
    }

    requests.request("POST", url, data=json, headers=headers)
    pass

def process_crawling(stock_code: str, target_url: str, post_service_url: str, formatted_start_date: int, formatted_end_date: int):
    try:
        crawler_obj: Crawler = Crawler(target_url, formatted_start_date, formatted_end_date)
        stock_hist: Stock = crawler_obj.get_history(stock_code)

        if stock_hist:
            if not stock_hist.history:
                stock_hist.history = []  
                logging.warning("{} - HISTORY EMPTY!".format(stock_code))  

            json_obj = json.dumps(stock_hist.__dict__, default=lambda o: o.__dict__)

            threading.Thread(target=invoke_url, args=(post_service_url, json_obj)).start()                
            pass
    except Exception as e:
        logging.error(e)
        pass
    pass