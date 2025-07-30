import requests
import logging
from zia.Api.CatalogItemsApi import CatalogItemsApi
from zia.Api.ResultsApi import ResultsApi
from zia.Api.StartApi import StartApi
from zia.Api.TasksApi import TasksApi

class ApiClient:
    def __init__(self, api_key: str, base_url:str, logger:logging.Logger):
        """_summary_

        Args:
            api_key (str): API key for authentication
            base_url (str): Base URL for the API. Defaults to staging if not provided.
            logger (logger): Logger instance for logging messages. If not provided, a default logger will be used.
        """
        
        if base_url is None:
            base_url = "https://staging.api.neurolabs.ai/v2"
        elif base_url == "staging":
            base_url = "https://staging.api.neurolabs.ai/v2"
        elif base_url == "prod":
            base_url = "https://api.neurolabs.ai/v2"
            
            
        self.api_key = api_key
        self.base_url = base_url
        if logger is None:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        self.logger = logger

    def create_catalog_items_api(self):
        return CatalogItemsApi(self.api_key, self.base_url, self.logger)
    
    def create_image_recognition_results_api(self):
        return ResultsApi(self.api_key, self.base_url, self.logger)
    
    def create_tasks_api(self):
        return TasksApi(self.api_key, self.base_url, self.logger)

    def start_image_recognition_api(self):
        return StartApi(self.api_key, self.base_url, self.logger)

