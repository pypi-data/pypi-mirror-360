import io, json
from typing import BinaryIO

class SnowflakeCredentials:
    def __init__(self, account_id: str, username: str, password: str) -> None:
        self.account_id = account_id
        self.username = username
        self.password = password

    def as_binary_io(self) -> BinaryIO:
        credentials = {
            "accountId": self.account_id,
            "username": self.username,
            "password": self.password,
        }
        return io.BytesIO(json.dumps(credentials).encode())