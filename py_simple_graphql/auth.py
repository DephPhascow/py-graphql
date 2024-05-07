import json
import os
from typing import Coroutine, Union
from .utils import gen_mutate, gen_fragment
from dataclasses import dataclass
from .graphql import GraphQL
from data.db import UserModel
from datetime import datetime
from datetime import timezone
import asyncio

def fragment_token():
  return gen_fragment(
    name="tokenFragment",
    type_name="ObtainJSONWebTokenType",
    request="""
        token {
            token
            payload {
            exp
            }
        }
        errors
        success
        refreshToken {
            token
            expiresAt
        }    
    """,
  )
  
def auth_token():
  return gen_mutate(
    name="tokenAuth",
    request="""
        ...tokenFragment 
    """,
    var={
        "tgId": "String!",
        "password": "String!",
    }
  )
  
def refresh_token():
  return gen_mutate(
    name="refreshToken",
    request="""
        ...tokenFragment 
    """,
    var={
        "refreshToken": "String!",
        "revokeRefreshToken": "Boolean!",
    }
  )
  
@dataclass
class Token:
    success: bool
    error: str
    token: str
    token_exp: datetime
    refresh_token: str
    refresh_token_exp: datetime
    def __post_init__(self):
        if isinstance(self.token_exp, str):
            self.token_exp = datetime.fromisoformat(self.token_exp)
        if isinstance(self.refresh_token_exp, str):
            self.refresh_token_exp = datetime.fromisoformat(self.refresh_token_exp)
    def to_json(self):
        return {
            "success": self.success,
            "error": self.error,
            "token": self.token,
            "token_exp": self.token_exp.isoformat(),
            "refresh_token": self.refresh_token,
            "refresh_token_exp": self.refresh_token_exp.isoformat()
        }

@dataclass
class Auth:
    login: Union[str, int]
    password: str
    gql: GraphQL
    tz: timezone = timezone.utc
    msg_no_access: str = "Нет доступа"
    token: Token = None
    file_name: str = "ex.json"
    on_save: Coroutine = None
        
    async def request_tokens(self,):
        exec = self.gql.add_query("auth_token", auth_token())
        exec.add_fragment(fragment_token())
        self.token = await exec.execute(variables={
                "tgId": self.login,
                "password": self.password,
            },
            q_word="data.tokenAuth.{success: success, error: error, token: token.token, token_exp: token.payload.exp, refresh_token: refreshToken.token, refresh_token_exp: refreshToken.expiresAt}",
            to_type=Token,
            ignore_token = True,
            ignore_middlewares = ['auth']
        )[0]
        
    async def middleware(self, ):
        utc = timezone.utc
        now = datetime.now(utc)
        self.token_exp = self.token.token_exp.replace(tzinfo=utc)
        if now > self.token.token_exp:
            if now > self.token.refresh_token_exp:
                await self.request_tokens()
            else:
                delta_days = self.token.refresh_token_exp - now
                revoke = delta_days.days < 1
                exec = self.gql.add_query("refresh_token", refresh_token())
                exec.add_fragment(fragment_token())
                self.token = (await exec.execute(variables={
                    "refreshToken": self.token.refresh_token,
                    "revokeRefreshToken": revoke
                },
                q_word="data.refreshToken.{success: success, error: error, token: token.token, token_exp: token.payload.exp, refresh_token: refreshToken.token, refresh_token_exp: refreshToken.expiresAt}",
                to_type=Token,
                ignore_token = True,
                ignore_middlewares = ['auth']                
                ))[0]
            await self.on_save(self.token, self.login)
        
    def save_json(self, file_name: str):
        self.file_name = file_name
        with open(file_name, "w") as file:
            file.write(json.dumps(self.token.to_json()))
            
    def load_json(self, file_name: str):
        self.file_name = file_name
        with open(file_name, "r") as file:
            self.token = Token(**json.loads(file.read()))
    def load(self, token: Token):
        self.token = token