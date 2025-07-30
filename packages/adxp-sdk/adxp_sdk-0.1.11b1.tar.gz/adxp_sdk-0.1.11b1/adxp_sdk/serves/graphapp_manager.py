import importlib.util
from autologging import logged
from typing import Dict, Any, Iterator, AsyncIterator, Optional, List
from autologging import logged
from langserve import add_routes
from langgraph.graph.state import CompiledStateGraph
from adxp_sdk.serves.utils import (
    per_req_config_modifier,
    init_app,
    add_login,
)
from adxp_sdk.serves.schema import GraphPath
from fastapi import FastAPI
from typing import Literal


def set_up_graph_routes(
    app: FastAPI,
    graph_path: str,
    graph_name: str = "",
    stream_mode: (
        Literal["values", "updates", "custom", "messages", "debug"] | None
    ) = None,
):
    """add graph routes to the app"""
    try:
        module_file, object_name = graph_path.split(":")
    except ValueError:
        raise ValueError(
            "graph_path 형식이 올바르지 않습니다. 예시: '/path/to/module.py:object_name'"
        )
    module_file = module_file.strip()
    object_name = object_name.strip()
    # importlib를 사용하여 모듈을 동적으로 로드합니다.
    spec = importlib.util.spec_from_file_location("dynamic_module", module_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"모듈 {module_file}을(를) 찾을 수 없습니다.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # 지정한 이름의 객체를 모듈에서 가져옵니다.
    try:
        graph: CompiledStateGraph = getattr(module, object_name)
    except AttributeError:
        raise AttributeError(
            f"모듈 {module_file}에 {object_name}이(가) 존재하지 않습니다."
        )
    if graph_name != "":
        graph_name = f"/{graph_name}"
    if stream_mode:
        graph.stream_mode = stream_mode
    add_routes(
        app,
        graph,
        path=graph_name,
        per_req_config_modifier=per_req_config_modifier,
    )
    return app


@logged
def create_graph_app(
    graph_path: str,
    stream_mode: (
        Literal["values", "updates", "custom", "messages", "debug"] | None
    ) = None,
) -> FastAPI:
    """create a FastAPI app with graph routes"""
    app = init_app()
    app = set_up_graph_routes(app=app, graph_path=graph_path, stream_mode=stream_mode)
    app = add_login(app=app)
    return app


@logged
def create_multiple_graphs_app(
    graph_paths: List[GraphPath | dict],
    stream_mode: (
        Literal["values", "updates", "custom", "messages", "debug"] | None
    ) = None,
) -> FastAPI:
    """create a FastAPI app with multiple graph routes"""
    app = init_app()
    for graph_path in graph_paths:
        if not isinstance(graph_path, GraphPath):
            graph_path = GraphPath.model_validate(graph_path)
        app = set_up_graph_routes(
            app=app,
            graph_path=graph_path.object_path,
            graph_name=graph_path.name,
            stream_mode=stream_mode,
        )
    app = add_login(app=app)
    return app
