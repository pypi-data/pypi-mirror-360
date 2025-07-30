import logging
import aiohttp
import requests


class ResultsApi:
    def __init__(self, api_key, base_url, logger):
        self.api_key = api_key
        self.logger = logger
        self.base_url = base_url

    async def get_results(self, task_uuid, limit=50, offset=0):
        url = f"{self.base_url}/image-recognition/tasks/{task_uuid}/results?limit={limit}&offset={offset}"
        headers = {
            "accept": "application/json",
            "X-API-Key": self.api_key,
        }
        logging.debug(f"Fetching results from {url} with limit={limit} and offset={offset}")
        async with aiohttp.ClientSession() as session:

            try:
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
                    return await response.json()  # the JSON content of the response
            except aiohttp.ClientError as e:
                self.logger.error(e)
                return None

    async def get_result_for_specific_image_task(self, task_uuid, image_id, limit=50, offset=0, as_async = True):
        url = f"{self.base_url}/image-recognition/tasks/{task_uuid}/results/{image_id}"
        headers = {
            "accept": "application/json",
            "X-API-Key": self.api_key,
        }
        
        if as_async:
            async with aiohttp.ClientSession() as session:

                try:
                    async with session.get(url, headers=headers) as response:
                        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
                        return await response.json()  # the JSON content of the response
                except aiohttp.ClientError as e:
                    self.logger.error(e)
                    return None
        else:
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
                return response.json()       # the JSON content of the response
            except requests.RequestException as e:
                self.logger.error(e)
                return None
