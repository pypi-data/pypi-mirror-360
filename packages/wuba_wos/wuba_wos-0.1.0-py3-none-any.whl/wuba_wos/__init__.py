import requests
from requests.auth import HTTPBasicAuth
from typing import Dict

from loguru import logger


class WOS:
    def __init__(
        self,
        bucket: str,
        app_id: str,
        secret_id: str,
        base_url: str = "http://wosin14.58corp.com",
        token_url: str = "http://token.wos.58dns.org",
    ):
        super().__init__()
        self.bucket = bucket
        self.app_id = app_id
        self.secret_id = secret_id
        self.base_url = base_url
        self.token_url = token_url

    @property
    def upload_url(self):
        return f"{self.base_url}/{self.app_id}/{self.bucket}"

    def get_token(self, file_name: str) -> str:
        auth = HTTPBasicAuth(self.app_id, self.secret_id)
        headers = {
            "host": "token.wos.58dns.org",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"bucket": self.bucket, "filename": file_name}
        res = requests.get(
            url=self.token_url + "/get_token", headers=headers, auth=auth, params=data
        )
        return res.json()["data"]

    def upload(self, filename: str, file_path: str) -> Dict[str, str]:
        token = self.get_token(filename)
        headers = {"Authorization": token}
        with open(file_path, mode="rb") as f:
            files = {"filecontent": (filename, f, "application/octet-stream")}
            data = {"op": "upload"}
            res = requests.post(
                url=self.upload_url + f"/{filename}",
                data=data,
                files=files,
                headers=headers,
            )
            res = res.json()
            if "data" not in res:
                raise Exception(f"upload failed: {res['message']}")
        return res["data"]

    def download(self, filename: str, save_path: str):
        pass

    def delete(self, filename: str):
        token = self.get_token(filename)
        headers = {"Authorization": token}
        res = requests.post(
            url=self.upload_url + f"/{filename}?op=delete&cdn=del",
            headers=headers,
        )
        res = res.json()
        if res["code"] != 0:
            raise Exception(f"delete failed: {res['message']}")
        logger.info(f"delete {filename} success")
