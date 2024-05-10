from typing import Coroutine, Union
from py_simple_graphql.enums import QueryType
from py_simple_graphql.utils import gen_mutate, gen_fragment
from dataclasses import dataclass, field
from py_simple_graphql.graphql import GraphQL
from datetime import datetime
from datetime import timezone
from py_simple_graphql.middleware import Middleware

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
    },
    q_words="data.tokenAuth.{success: success, error: error, token: token.token, token_exp: token.payload.exp, refresh_token: refreshToken.token, refresh_token_exp: refreshToken.expiresAt}",
    to_type=Token,    
    require_fragments=["tokenFragment"]
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
    },
    q_word="data.refreshToken.{success: success, error: error, token: token.token, token_exp: token.payload.exp, refresh_token: refreshToken.token, refresh_token_exp: refreshToken.expiresAt}",
    to_type=Token,
    require_fragments=["tokenFragment"]
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
class AuthMiddleware(Middleware):
    gql: GraphQL
    login: Union[str, int]  = None
    password: str = None
    tz: timezone = timezone.utc
    token: Token = None
    on_save: Coroutine = None
    
    async def on_startup(self):
        self.gql.logger.log(f"Middleware {self.name} starting ...")
        self.gql.add_fragment(fragment_token())
        self.gql.logger.log(f"Middleware {self.name} started ...")
        
    async def set_data(self, login: str, password: str):
        self.login = login
        self.password = password
        self.gql.logger.log(f"Middleware {self.name} set login data: {self.login=}; {self.password=}")
        
    async def on_before_request(self, type: QueryType):
        self.gql.logger.log(f"Middleware {self.name}: Before request, type {type}, token data: {self.token}")
        if not self.token:
            self.gql.logger.log(f"Middleware {self.name}: Request new token data")
            await self.request_tokens()
            self.gql.logger.log(f"Middleware {self.name}: New token data: {self.token}")
            return 
        self.gql.logger.log(f"Middleware {self.name}: Processing")
        await self.process()
        self.gql.logger.log(f"Middleware {self.name}: Save")
        
    async def get_header(self):
        headers = {
            "Authorization": f"JWT {self.token.token}"
        }
        self.gql.logger.log(f"Middleware {self.name}: gen header: {headers}")
        return headers
        
    async def request_tokens(self,):
        self.gql.logger.log(f"Middleware {self.name}: Begin request new token data")
        exec = self.gql.add_query("auth_token", auth_token())
        res = await exec.execute(variables={
                "tgId": self.login,
                "password": self.password,
            },
            ignore_middlewares = ['auth']
        )
        self.token = res["tokenAuth"]
        self.gql.logger.log(f"Middleware {self.name}: End request new token data")
        
    async def process(self, ):
        now = datetime.now(self.tz)
        self.token.token_exp = self.token.token_exp.replace(tzinfo=self.tz)
        if now > self.token.token_exp:
            if now > self.token.refresh_token_exp:
                await self.request_tokens()
            else:
                delta_days = self.token.refresh_token_exp - now
                revoke = delta_days.days < 1
                exec = self.gql.add_query("refresh_token", refresh_token())
                self.token = (await exec.execute(variables={
                    "refreshToken": self.token.refresh_token,
                    "revokeRefreshToken": revoke
                },
                ignore_middlewares = ['auth']                
                ))[0]
            await self.on_save(self.token, self.login)
            
    def load(self, token: Token):
        self.token = token