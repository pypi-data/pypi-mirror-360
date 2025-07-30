# -*- coding: utf-8 -*-
from pydantic import BaseModel


class User(BaseModel):
    username: str


class Token(BaseModel):
    header_auth_type: str
    decoded: dict
    raw: str

    def __post_init__(self) -> None:
        self.header_auth_type = self.header_auth_type.lower()
