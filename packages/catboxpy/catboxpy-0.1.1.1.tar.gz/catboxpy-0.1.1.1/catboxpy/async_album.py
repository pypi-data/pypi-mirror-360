import httpx

CATBOX_API = "https://catbox.moe/user/api.php"

class AsyncAlbumManager:
    def __init__(self, userhash: str | None = None):
        self.userhash = userhash

    async def _post(self, data: dict) -> str:
        if self.userhash:
            data["userhash"] = self.userhash
        async with httpx.AsyncClient() as client:
            response = await client.post(CATBOX_API, data=data)
        if response.status_code == 200:
            return response.text.strip()
        else:
            raise Exception(f"Request failed: {response.status_code} {response.text}")
        
    async def _check_userhash(self):
        if not self.userhash:
            raise ValueError("This operation requires a userhash (logged in user)")
        
    async def create(self, title: str, desc: str, files: list[str]) -> str:

        return await self._post({
            "reqtype": "createalbum",
            "title": title,
            "desc": desc,
            "files": " ".join(files),
        })

    async def edit(self, short: str, title: str, desc: str, files: list[str]) -> str:
        await self._check_userhash()
        return await self._post({
            "reqtype": "editalbum",
            "short": short,
            "title": title,
            "desc": desc,
            "files": " ".join(files),
        })

    async def add_files(self, short: str, files: list[str]) -> str:
        await self._check_userhash()
        return await self._post({
            "reqtype": "addtoalbum",
            "short": short,
            "files": " ".join(files),
        })

    async def remove_files(self, short: str, files: list[str]) -> str:
        await self._check_userhash()
        return await self._post({
            "reqtype": "removefromalbum",
            "short": short,
            "files": " ".join(files),
        })

    async def delete(self, short: str) -> str:
        await self._check_userhash()
        return await self._post({
            "reqtype": "deletealbum",
            "short": short,
        })