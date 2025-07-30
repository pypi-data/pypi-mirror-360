import os
import re
from functools import wraps
from typing import Any, Dict
from uuid import uuid4
from pydantic import BaseModel, AliasChoices, Field, ConfigDict, model_validator
from adxp_sdk.serves.types import HeaderKeys
from adxp_sdk.serves.playground_login import login_html
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, RedirectResponse
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langserve import add_routes
from starlette.datastructures import MutableHeaders
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv
import os
from pathlib import Path


ROOT_PATH = os.environ.get("ROOT_PATH", "")


def load_environment(path: str | None):
    """Load environment variables from .env file"""
    if path:
        env_path = Path(path)
        load_dotenv(dotenv_path=env_path)

    return os.environ


def formatting_token(auth_header: str) -> str:
    # from agent-gateway
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    # from swagger
    else:
        return auth_header


def is_from_graph_playground(request):
    try:
        referer = request.headers.get("referer", "")

        pattern = r"/playground/?"
        return bool(re.search(pattern, referer))
    except (AttributeError, TypeError):
        return False


class AIPHeaderKeysExtraAllow(BaseModel):
    authorization: str = Field(
        validation_alias=AliasChoices("authorization", "Authorization")
    )
    aip_user: str | None = Field(
        default=None,
        serialization_alias="aip-user",
        validation_alias=AliasChoices("aip-user"),
    )
    aip_transaction_id: str | None = Field(
        default=None,
        serialization_alias="aip-transaction-id",
        validation_alias=AliasChoices("aip-transaction-id"),
    )
    aip_app_serving_id: str | None = Field(
        default=None,
        serialization_alias="aip-app-serving-id",
        validation_alias=AliasChoices("aip-app-serving-id"),
    )
    aip_company: str | None = Field(
        default=None,
        serialization_alias="aip-company",
        validation_alias=AliasChoices("aip-company"),
    )
    aip_department: str | None = Field(
        default=None,
        serialization_alias="aip-department",
        validation_alias=AliasChoices("aip-department"),
    )
    aip_chat_id: str | None = Field(
        default=None,
        serialization_alias="aip-chat-id",
        validation_alias=AliasChoices("aip-chat-id"),
    )
    aip_app_id: str | None = Field(
        default=None,
        serialization_alias="aip-app-id",
        validation_alias=AliasChoices("aip-app-id"),
    )

    """Use This Class like this...
    validated_headers = AIPHeaderKeys.model_validate(dict(original_headers))
    new_headers_dict = validated_headers.model_dump(by_alias=True, exclude_none=True)
    """
    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    def check_required_headers(cls, values):
        if not (values.get("authorization") or values.get("Authorization")):
            raise KeyError("Missing required header: authorization")
        if not (values.get("aip-user") or values.get("aip_user")):
            raise KeyError("Missing required header: aip-user")
        return values


class AIPHeaderKeysExtraIgnore(AIPHeaderKeysExtraAllow):
    model_config = ConfigDict(extra="ignore")
    """Use This Class like this...
    aip_headers: AIPHeaderKeysExtraIgnore = config["configurable"]["aip_headers"]
    aip_headers.model_dump(by_alias=True, exclude_none=True)
    """

    def get_headers_without_authorization(self):
        headers = self.model_dump(by_alias=True, exclude_none=True)
        headers.pop("authorization")
        return headers


class AIPHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip middleware logic for /docs path
        playground_pattern = re.compile(f"^{re.escape(ROOT_PATH)}.*?/playground")
        if (
            (request.url.path == f"{ROOT_PATH}/docs")
            | (request.url.path in ["/favicon.ico"])
            | (request.url.path == f"{ROOT_PATH}/openapi.json")
            | (bool(playground_pattern.match(request.url.path)))
            | (request.url.path.startswith(f"{ROOT_PATH}/login"))
            | (request.url.path.startswith(f"{ROOT_PATH}/sub/"))
        ):
            return await call_next(request)

        new_headers = MutableHeaders()

        if is_from_graph_playground(request):
            playground_headers_entity = AIPHeaderKeysExtraIgnore.model_validate(
                request.cookies
            )
            playground_headers_dict = playground_headers_entity.model_dump(
                by_alias=True, exclude_none=True
            )
            for header, value in playground_headers_dict.items():
                new_headers.append(header, value)

        else:
            old_headers = {
                key.decode("utf-8"): value.decode("utf-8")
                for key, value in request.headers.raw
            }
            try:
                # validate required headers.
                AIPHeaderKeysExtraAllow.model_validate(old_headers)
            except KeyError as e:
                raise HTTPException(status_code=400, detail=e)

            for k, v in old_headers.items():
                if k.lower() == "authorization":
                    # (key) authorization -> Authorization
                    # (value) Bearer skxxxx -> skxxxx
                    v = formatting_token(v)
                    new_headers.append("Authorization", v)
                else:
                    new_headers.append(k, v)

        # header에 transaction id 없으면 생성해서 append
        transaction_id = new_headers.get(
            HeaderKeys.AIP_TRANSACTION_ID.value, str(uuid4())
        )
        if new_headers.get(HeaderKeys.AIP_TRANSACTION_ID.value) is None:
            new_headers.append(HeaderKeys.AIP_TRANSACTION_ID.value, transaction_id)
        request.scope["headers"] = new_headers.raw

        # response header에도 transaction id 추가
        response = await call_next(request)
        response.headers[HeaderKeys.AIP_TRANSACTION_ID.value] = transaction_id
        return response


async def per_req_config_modifier(config: Dict, request: Request) -> Dict:
    """Modify the config for each request."""
    validated_headers = AIPHeaderKeysExtraIgnore.model_validate(request.headers)
    if config.get("configurable") is None:
        config["configurable"] = {}
    config["configurable"].update({"aip_headers": validated_headers})

    # configurable = validated_headers.model_dump(by_alias=True, exclude_none=True)
    # return config
    return RunnableConfig(**config)


def custom_openapi(app):
    if not app.openapi_schema:
        openapi_schema = get_openapi(
            title="LangChain Server",
            description=f"PlatForm Agent App",
            version="0.1.0",
            routes=app.routes,
            servers=[{"url": ROOT_PATH}] if ROOT_PATH else None,
        )
        openapi_schema["info"]["x-logo"] = {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        }

        openapi_schema["components"]["securitySchemes"] = {
            "APIKeyHeader": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
            }
        }

        # Add global security requirement
        openapi_schema["security"] = [{"APIKeyHeader": []}]

    else:
        openapi_schema = app.openapi_schema

    for path in openapi_schema["paths"].values():
        for method in path.values():
            # method.setdefault("parameters", []).extend(
            method["security"] = [{"APIKeyHeader": []}]
            method.setdefault("parameters", []).extend(
                [
                    {
                        "name": HeaderKeys.AIP_USER.value,
                        "in": "header",
                        "description": "User ID",
                        "required": True,
                        "schema": {
                            "type": "string",
                            "default": "ai_agent_eng",
                        },
                    },
                    {
                        "name": HeaderKeys.AIP_APP_SERVING_ID.value,
                        "in": "header",
                        "description": "Serving ID to identify deployed agent app",
                        "required": False,
                        "schema": {
                            "type": "string",
                        },
                    },
                    {
                        "name": HeaderKeys.AIP_TRANSACTION_ID.value,
                        "in": "header",
                        "description": "A unique identifier for each request. Each graph query has its own transaction ID. If the value is null, it will be automatically created and inserted.",
                        "required": False,
                        "schema": {
                            "type": "string",
                        },
                    },
                    {
                        "name": HeaderKeys.AIP_CHAT_ID.value,
                        "in": "header",
                        "description": "Chat ID, which is a collection of conversations between a user and an AI that bundles multiple transactions together.",
                        "required": False,
                        "schema": {
                            "type": "string",
                        },
                    },
                    {
                        "name": HeaderKeys.AIP_COMPANY.value,
                        "in": "header",
                        "description": "Name of company",
                        "required": False,
                        "schema": {
                            "type": "string",
                        },
                    },
                    {
                        "name": HeaderKeys.AIP_DEPARTMENT.value,
                        "in": "header",
                        "description": "Name of department",
                        "required": False,
                        "schema": {
                            "type": "string",
                        },
                    },
                    {
                        "name": HeaderKeys.AIP_SECRET_MODE.value,
                        "in": "header",
                        "description": "Whether store records. Default is False",
                        "required": False,
                        "schema": {"type": "string", "default": False},
                    },
                    {
                        "name": HeaderKeys.AIP_APP_ID.value,
                        "in": "header",
                        "description": "Identifier for Client App.",
                        "required": False,
                        "schema": {"type": "string"},
                    },
                ]
            )

    return openapi_schema


def get_login_html_content(hasError: bool = False):
    error_message = "<p>Invalid API Key</p>" if hasError else ""
    return login_html.format(root_path=ROOT_PATH, error_message=error_message)


def init_app() -> FastAPI:
    print("Initializing App")

    app = FastAPI(root_path=ROOT_PATH)

    # Set all CORS enabled origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    app.add_middleware(AIPHeaderMiddleware)
    return app


def add_login(app: FastAPI) -> FastAPI:
    app.openapi_schema = custom_openapi(app=app)

    @app.get("/login", response_class=HTMLResponse)
    def login_form():
        return HTMLResponse(content=get_login_html_content())

    @app.post("/login")
    def login(
        api_key: str = Form(),
        aip_user: str = Form(),
        aip_app_serving_id: str | None = Form(default=None),
        prefix: str | None = Form(default=""),
    ):
        if api_key:
            prefix = prefix if prefix else ""
            response = RedirectResponse(
                url=f"{ROOT_PATH}{prefix}/playground", status_code=303
            )
            kv_list = [
                ("api_key", "authorization"),
                ("aip_user", "aip-user"),
                ("aip_app_serving_id", "aip-app-serving-id"),
            ]
            for k, v in kv_list:
                if locals().get(k):
                    response.set_cookie(
                        key=v,
                        value=locals()[k],
                        httponly=True,
                        secure=True,
                        samesite="strict",
                    )
            return response
        return HTMLResponse(content=get_login_html_content(hasError=True))

    return app


def add_routes_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Code to be executed before add_routes
        print("Executing pre-add_routes logic")

        app = FastAPI(root_path=ROOT_PATH)

        # Set all CORS enabled origins
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"],
        )
        app.add_middleware(AIPHeaderMiddleware)
        # Call the original function (which includes add_routes)
        kwargs.pop("app", None)
        setup_routes = func(app, *args, **kwargs)
        app = setup_routes()

        # Code to be executed after add_routes
        print("Executing post-add_routes logic")
        app.openapi_schema = custom_openapi(app=app)

        @app.get("/login", response_class=HTMLResponse)
        def login_form():
            return HTMLResponse(content=get_login_html_content())

        @app.post("/login")
        def login(
            api_key: str = Form(...),
            aip_user: str = Form(...),
            aip_app_serving_id: str = Form(...),
            prefix: str = Form(...),
        ):
            if api_key:
                response = RedirectResponse(
                    url=f"{ROOT_PATH}{prefix}/playground", status_code=303
                )
                kv_list = [
                    ("api_key", "authorization"),
                    ("aip_user", "AIP_USER"),
                    ("aip_app_serving_id", "AIP_APP_SERVING_ID"),
                ]
                for k, v in kv_list:
                    response.set_cookie(
                        key=v,
                        value=locals()[k],
                        httponly=True,
                        secure=True,
                        samesite="strict",
                    )
                return response
            return HTMLResponse(content=get_login_html_content(hasError=True))

        return app

    return wrapper
