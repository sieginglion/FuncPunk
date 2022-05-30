from typing import List

import uvicorn
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from kube_objects import ConfigMap, Deployment, Service


app = FastAPI()


class Func(BaseModel):
    name: str
    code: str


@app.get('/funcs')
async def get_funcs() -> List[Func]:
    return [
        Func(**{'name': configmap.body.metadata.name, 'code': configmap.body.data.code})
        for configmap in ConfigMap().get_all()
        if 'code' in configmap.body.data
    ]


@app.put('/funcs/{name}')
async def put_func(name: str, func: Func) -> Response:
    ConfigMap(name, {'code': func.code}).put()
    Deployment().delete(name)
    Deployment(name).put()
    Service(name).put()
    return Response(status_code=200)


@app.delete('/funcs/{name}')
async def delete_func(name: str) -> Response:
    Service().delete(name)
    Deployment().delete(name)
    ConfigMap().delete(name)
    return Response(status_code=200)


app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'])

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
