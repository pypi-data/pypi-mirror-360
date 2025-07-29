import redis
from typing import Union
from fastapi import FastAPI, Request
r = redis.Redis.from_url(url="redis://:1234qwer666@150.158.144.155:6390/0", decode_responses=True)
app = FastAPI()


def test():
    myredis = redis.Redis.from_url(url="redis://:1234qwer666@150.158.144.155:6390/0", decode_responses=True)
    # myredis = redis.Redis(host='150.158.144.155', port=6390, decode_responses=True,
    #                 username="", password="1234qwer666", db=0)
    # ipdb.set_trace()
    myredis.set('foo', 'bar')
    myredis.set('xxxlock', 'client_id', nx=True, ex=600)
    print(myredis.get('foo'))
    print(myredis.get('foo'))
    print(myredis.get('foo'))


@app.get("/set/{key}/{value}", tags=["redis"])
def get_customer(key: str, value: str):
    r.set(key, value)
    return {"redis": "set", key: value}


@app.get("/get/{key}", tags=["redis"])
def get_customer(key: str):
    value = r.get(key)
    return {"redis": "get",  key: value}


@app.get("/ratelimit/{key}", tags=["redis"])
def ratelimit(key: str, ):
    r.set(key, 0, ex=10, nx=True)
    v = r.incr(key)
    ttl = r.ttl(key)
    return {"redis": "setnx", "key": key, "counter": v, "ttl": ttl}



### todo:
# 将redis的其他数据结构实现为 fastapi 的一个endpoint(接口)


#  运行程序:
#  uvicorn.exe redisdemo:app