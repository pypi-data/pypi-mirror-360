import requests

CATBOX_API = 'https://catbox.moe/user/api.php'

class AlbumManager:
    def __init__(self, userhash: str | None = None):
        self.userhash = userhash


    def _post(self, data: dict) ->str:
        if self.userhash:
            data["userhash"] = self.userhash
        response = requests.post(CATBOX_API, data = data)
        if response.status_code == 200:
            return response.text.strip()
        
        else:
            raise Exception(f'Request Failed: {response.status_code} {response.text}')
        
    def create(self,title: str, desc:str, files : list[str]) ->str:
        '''
        Create a new album
        Params: 
        Album Title,
        Album Description,
        List of catbox file urls'''

        return self._post({
            'reqtype' :'createalbum',
            'title' : title,
            'desc' : desc,
            'files' : " ".join(files),

        })
    def _check_userhash(self):
        if not self.userhash:
            raise ValueError("This operation requires a userhash (logged in user)")
    def edit(self,short: str, title: str, desc: str, files: list[str]) ->str:
        '''
        Editing an Album
        Params:
        Short: 6 alphanumeric characters in the url thats generated,
        title: Album Title,
        desc: Album description,
        Files: List of file urls
        '''
        self._check_userhash()
        return self._post({
            'reqtype' :'createalbum',
            'short' : short,
            'title' : title,
            'desc' : desc,
            'files' : " ".join(files),

        })
    
    def add_files(self, short: str, files: list[str]) -> str:
        """
        Add files to an existing album.

        short: Album ID
        files: Files to add
        """
        self._check_userhash()
        return self._post({
            "reqtype": "addtoalbum",
            "short": short,
            "files": " ".join(files),
        })

    def remove_files(self, short: str, files: list[str]) -> str:
        """
        removes files from an album.

        short: Album ID
        files: Files to remove

        """
        self._check_userhash()
        return self._post({
            "reqtype": "removefromalbum",
            "short": short,
            "files": " ".join(files),
        })

    def delete(self, short: str) -> str:
        """
        deletes an album.

        short: Album ID
        """
        self._check_userhash()
        return self._post({
            "reqtype": "deletealbum",
            "short": short,
        })
    
class AnonymousAlbumProxy:
    def __getattr__(self, name):
        raise RuntimeError("User Hash is required. Anonymous clients cannot manage albums.")
