import httpx
import os
from .async_album import AsyncAlbumManager

CATBOX_API = 'https://catbox.moe/user/api.php'


class AsyncCatboxClient:

    def __init__(self, userhash: str | None = None):

        self.userhash = userhash
        self.album = AsyncAlbumManager(userhash=self.userhash) 
        

    async def upload(self,file_or_url: str) ->str:
        '''Upload an File to Catbox
            by uploading a file or by using an Url.'''
        
        if file_or_url.startswith('https://') or file_or_url.startswith('http://'):
            return await self._upload_url(file_or_url)
        
        else:
            return await self._upload_file(file_or_url)
    
    async def _upload_file(self, file_path: str) -> str:
        data = {'reqtype': 'fileupload'}
        if self.userhash:
            data['userhash'] = self.userhash

        async with httpx.AsyncClient() as client:
            with open(file_path, 'rb') as f:
                files = {'fileToUpload': (os.path.basename(file_path), f, 'application/octet-stream')}
                response = await client.post(CATBOX_API, data=data, files=files)

        if response.status_code == 200:
            return response.text.strip()
        else:
            raise Exception(f"File upload failed: {response.status_code} {response.text}")
        


    async def _upload_url(self, url: str) -> str:
        data = {
            'reqtype': 'urlupload',
            'url': url
        }
        if self.userhash:
            data['userhash'] = self.userhash

        async with httpx.AsyncClient() as client:
            response = await client.post(CATBOX_API, data=data)

        if response.status_code == 200:
            return response.text.strip()
        else:
            raise Exception(f"URL upload failed: {response.status_code} {response.text}")

        

    async def delete_file(self, filename: str | list[str]) -> str:
        if not self.userhash:
            raise ValueError("Userhash is required to delete files")

        if isinstance(filename, list):
            files_str = " ".join(filename)
        else:
            files_str = filename

        data = {
            "reqtype": "deletefiles",
            "userhash": self.userhash,
            "files": files_str
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(CATBOX_API, data=data)
        if response.status_code == 200:
            return response.text.strip()
        else:
            raise Exception(f"URL upload failed: {response.status_code} {response.text}")

