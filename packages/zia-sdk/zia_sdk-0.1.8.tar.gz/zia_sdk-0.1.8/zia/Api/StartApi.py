import logging
import aiohttp
import requests

class StartApi:
    def __init__(self, api_key, base_url, logger):
        self.api_key = api_key
        self.logger = logger
        self.base_url = base_url

    async def images(self, task_uuid, filepath):
        url = f"{self.base_url}/tasks/{task_uuid}/images"
        headers = {
            "accept": "application/json",
            "X-API-Key": self.api_key,
        }

        with open(filepath, 'rb') as file:
            data = aiohttp.FormData()
            data.add_field(
                'images',  # Field name expected by the server
                file,
                filename=filepath.split('/')[-1],  # File name to send
                content_type='image/jpeg'  # Adjust MIME type as needed
            )

            async with aiohttp.ClientSession() as session:
                try:
                    # Make a POST request with the file
                    async with session.post(url, headers=headers, data=data) as response:
                        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
                        return await response.json()  # Return the JSON response
                except aiohttp.ClientError as e:
                    self.logger.error(e)
                    raise e
                
    async def urls(self, task_uuid: str, image_urls: list[str]):
        """
        Uploads a batch of image URLs for a specific task.

        :param task_uuid: UUID of the task you're adding images to.
        :param image_urls: List of public image URLs to upload.
        :return: Parsed JSON response from Neurolabs API.
        """
        url = f"{self.base_url}/image-recognition/tasks/{task_uuid}/urls"
        headers = {
            "accept": "application/json",
            "X-API-Key": self.api_key,
        }

        payload = {
            "urls": image_urls
            }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, headers=headers) as response:            
                    response.raise_for_status()  # Raises on HTTP 4xx or 5xx
                    return await response.json()
            except aiohttp.ClientError as e:
                self.logger.error(f"HTTP request failed: {e}")
                raise
            except Exception as e:
                self.logger.exception("Unexpected error during image URL upload")
                raise