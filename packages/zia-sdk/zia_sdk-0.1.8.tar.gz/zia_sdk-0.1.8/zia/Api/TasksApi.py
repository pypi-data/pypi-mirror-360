import logging
import aiohttp
import requests

class TasksApi:
    def __init__(self, api_key, base_url, logger):
        self.api_key = api_key
        self.logger = logger
        self.base_url = base_url

    async def list_tasks(self, limit=50, offset=0):
        url = f"{self.base_url}/image-recognition/tasks?limit={limit}&offset={offset}"
        headers = {
            "accept": "application/json",
            "X-API-Key": self.api_key,
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
                    return await response.json()  # Return the JSON content of the response
            except aiohttp.ClientError as e:
                self.logger.error(e)
                return None
            
    async def create_task(self, task_data):
        url = f"{self.base_url}/image-recognition/tasks"
        headers = {
            "accept": "application/json",
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, json=task_data) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                self.logger.error(e)
                return None
            
    async def get_task(self, task_uuid):
        url = f"{self.base_url}/image-recognition/tasks/{task_uuid}"
        headers = {
            "accept": "application/json",
            "X-API-Key": self.api_key,
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                self.logger.error(e)
                return None
            
    async def update_task(self, task_uuid, task_data):
        url = f"{self.base_url}/image-recognition/tasks/{task_uuid}"
        headers = {
            "accept": "application/json",
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.put(url, headers=headers, json=task_data) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                self.logger.error(e)
                return None
            

    async def delete_task(self, task_uuid):
        url = f"{self.base_url}/image-recognition/tasks/{task_uuid}"
        headers = {
            "accept": "application/json",
            "X-API-Key": self.api_key,
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.delete(url, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                self.logger.error(e)
                return None