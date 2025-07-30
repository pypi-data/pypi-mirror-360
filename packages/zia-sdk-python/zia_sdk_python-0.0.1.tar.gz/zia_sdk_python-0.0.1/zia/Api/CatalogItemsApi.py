import logging

import aiohttp
import asyncio


class CatalogItemsApi:
    def __init__(self, api_key, base_url, logger):
        self.api_key = api_key
        self.logger = logger
        self.base_url = base_url
        
        
    async def get_catalog_items(self, limit=50, offset=0):
        url = f"{self.base_url}/catalog-items?limit={limit}&offset={offset}"
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
                self.logger.error(f"Error fetching v2 catalog items: {e}")
                return None
            
            
    async def get_catalog_item_by_uuid(self, item_uuid):
        url = f"{self.base_url}/catalog-items/{item_uuid}"
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
                self.logger.error(f"Error fetching catalog item {item_uuid}: {e}")
                return None
            
    async def create_catalog_item(self, item_data):
        url = f"{self.base_url}/catalog-items"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, json=item_data) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                self.logger.error(f"Error creating catalog item: {e}")
                return None
            
            
    async def upload_catalog_item_reference_images(self, item_uuid, images):
        """
        Upload reference images for a catalog item.

        Args:
            item_uuid (str): The UUID of the catalog item.
            images (list): List of file paths or file-like objects to upload.

        Returns:
            dict or None: The response JSON or None if an error occurred.
        """
        url = f"{self.base_url}/catalog-items/{item_uuid}/reference-images"
        headers = {
            "accept": "application/json",
            "X-API-Key": self.api_key,
        }

        data = aiohttp.FormData()
        for img in images:
            if isinstance(img, str):
                data.add_field('images', open(img, 'rb'), filename=img.split('/')[-1])
            else:
                data.add_field('images', img, filename=getattr(img, 'name', 'image.jpg'))

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, data=data) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                self.logger.error(f"Error uploading reference images for item {item_uuid}: {e}")
                return None
            
    
        async def create_one_faced_asset_request(self, item_uuid, asset_data):
            """
            Create a one-faced asset request for a catalog item.

            Args:
                item_uuid (str): The UUID of the catalog item.
                asset_data (dict): The asset request payload.

            Returns:
                dict or None: The response JSON or None if an error occurred.
            """
            url = f"{self.base_url}/catalog-items/{item_uuid}/asset-requests/one-faced-asset"
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
            }

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(url, headers=headers, json=asset_data) as response:
                        response.raise_for_status()
                        return await response.json()
                except aiohttp.ClientError as e:
                    self.logger.error(f"Error creating one-faced asset request for item {item_uuid}: {e}")
                    return None
            
    

    async def get_catalog_items_old(self, limit=50, offset=0):

        url = f"{self.base_url}/catalog-items?limit={limit}&offset={offset}"
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
            
            print("done")


