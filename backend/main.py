from typing import Callable, List

import uvicorn
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel

from kube_objects import ConfigMap, Deployment, Service


class Func(BaseModel):
    name: str
    code: str


app = FastAPI()


@app.get('/funcs')
async def get_funcs() -> List[Func]:
    return [
        Func(**{'name': configmap.body.metadata.name, 'code': configmap.body.data.code})
        for configmap in ConfigMap().get_all()
        if 'code' in configmap.body.data
    ]


@app.put('/funcs/<name>')
async def put_func(name: str, func: Func) -> Response:
    ConfigMap(name, {'code': func.code}).put()
    Deployment().delete(name)
    Deployment(name).put()
    Service(name).put()
    return Response(status=200)


@app.delete('/funcs/<name>')
async def delete_func(name: str) -> Response:
    Service().delete(name)
    Deployment().delete(name)
    ConfigMap().delete(name)
    return Response(status=200)


@app.middleware('http')
async def post_process(
    request: Request, call_next: Callable[[Request], Response]
) -> Response:
    response = await call_next(request)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, PUT, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Access-Control-Allow-Origin'
    return response


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
