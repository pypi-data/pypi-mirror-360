import json

from .handler import save_many_handler,delete_many_handler
from ...channels.executer import execute_channel
from ...channels.sender import ValarSocketSender
from ...core.dao.dao_base import Dao
from ...core.meta.meta_orm import OrmMeta
from ...core.response import ValarResponse

async def save_many(request):
    sender = ValarSocketSender(request)
    await execute_channel(save_many_handler, sender)
    return ValarResponse(True)

async def delete_many(request):
    sender = ValarSocketSender(request)
    await execute_channel(delete_many_handler, sender)
    return ValarResponse(True)

def save_one (request,db, entity):
    item = json.loads(request.body)
    dao = Dao(entity, db)
    bean = dao.save_one(item)
    item = dao.transform(bean)
    return ValarResponse(item)

def delete_one(request, db, entity):
    body = json.loads(request.body)
    _id = body['id']
    dao = Dao(entity, db)
    flag = dao.delete_one(_id)
    return ValarResponse(flag)

def find_one(request, db, entity):
    body = json.loads(request.body)
    _id = body['id']
    dao = Dao(entity, db)
    bean = dao.find_one(_id)
    item = dao.transform(bean)
    return ValarResponse(item)

def find (request,db, entity):
    conditions = json.loads(request.body)
    dao = Dao(entity, db)
    results, _ = dao.find(conditions)
    results = dao.transform(results)
    return ValarResponse(results)

def update(request, db, entity):
    body = json.loads(request.body)
    conditions = body.get('conditions',[])
    template =body.get('template')
    dao = Dao(entity, db)
    flag = dao.update(template, conditions)
    return ValarResponse(flag)

def table(request, db, entity):
    body = json.loads(request.body)
    conditions = body.get('conditions', [])
    orders = body.get('orders')
    size = body.get('size')
    page = body.get('page')
    dao = Dao(entity, db)
    results, total = dao.find(conditions, orders, size, page)
    results = dao.transform(results)
    return ValarResponse({
        "results":results,
        "total": total
    })

def tree(request, db, entity):
    body = json.loads(request.body)
    conditions = body.get('conditions', [])

    root = body.get('root')
    dao = Dao(entity, db)
    query_set = dao.tree(root, conditions)
    results = dao.transform(query_set)
    return ValarResponse({
        "results": results,
        "root": root
    })


def meta_view(request, db, entity):
    body = json.loads(request.body)
    code = body.get('code')
    _view = OrmMeta(entity, code).get_view()
    return ValarResponse(_view)