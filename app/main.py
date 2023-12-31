import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from starlette.requests import Request
from elasticsearch import AsyncElasticsearch
from logging import getLogger, StreamHandler

from app.models import CreateUserRequest

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel("INFO")

MAPPING_FOR_INDEX = {
            "properties": {
                "name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "surname": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "date_of_birth": {
                    "type": "date"
                },
                "interests": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                }
            }
        }


async def ping() -> dict:
    return {"success": True}


async def create_index(request: Request) -> dict:
    elastic_client: AsyncElasticsearch = request.app.state.elastic_client
    await elastic_client.indices.create(index="users", mappings=MAPPING_FOR_INDEX)
    return {"success": True}


async def delete_index(request: Request) -> dict:
    elastic_client: AsyncElasticsearch = request.app.state.elastic_client
    await elastic_client.indices.delete(index="users")
    return {"success": True}


async def create_user(request: Request, body: CreateUserRequest) -> dict:
    elastic_client: AsyncElasticsearch = request.app.state.elastic_client
    res = await elastic_client.index(index="users", document=body.dict())
    logger.info(res)
    return {"success": True, "result": res}


async def get_all_users(request: Request):
    elastic_client: AsyncElasticsearch = request.app.state.elastic_client
    res = await elastic_client.search(index="users", query={"match_all": {}})
    return {"success": True, "result": res}


routes = [
    APIRoute(path="/ping", endpoint=ping, methods=["GET"]),
    APIRoute(path="/create_index", endpoint=create_index, methods=["GET"]),
    APIRoute(path="/delete_index", endpoint=delete_index, methods=["GET"]),
    APIRoute(path="/create_user", endpoint=create_user, methods=["POST"]),
    APIRoute(path="/get_all_users", endpoint=get_all_users, methods=["GET"])
]

elastic_client = AsyncElasticsearch()
app = FastAPI()
app.state.elastic_client = elastic_client
app.include_router(APIRouter(routes=routes))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)