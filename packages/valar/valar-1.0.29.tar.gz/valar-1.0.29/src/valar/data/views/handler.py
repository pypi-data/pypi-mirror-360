from ...channels.sender import ValarSocketSender
from ...core.counter import Counter
from ...core.dao.dao_base import Dao
from ...core.dao.dao_mon import MonDao
from ...core.dao.dao_orm import OrmDao




def save_many_handler(sender: ValarSocketSender):
    data = sender.data
    entity, array, db = data.get("entity"), data.get("array",[]), data.get("db")
    dao = Dao(entity, db)
    counter = Counter(array)
    for item in array:
        item['saved'] = True
        dao.save_one(item)
        payload = counter.tick()
        sender.to_clients(payload, sender.client, wait=True)



def delete_many_handler(sender: ValarSocketSender):
    data = sender.data
    entity, conditions, db = data.get("entity"), data.get("conditions", []), data.get("db")
    if db == 'orm':
        dao = OrmDao(entity)
        query_set, _ = dao.find(conditions)
        paths = dao.model.get_file_paths(query_set)
        query_set.delete()
        counter = Counter(len(paths))
        # for path in paths:
            # dao.model.minio.remove_path(path)
        payload = counter.tick()
        sender.to_clients(payload, sender.client, wait=True)
    else:
        dao = MonDao(entity)
        dao.delete(conditions)



