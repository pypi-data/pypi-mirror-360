from django.db.models import Q
from functools import reduce



def __fun__(x, y): return x | y
def __translate_orders__(orders):
    array = []
    for key in orders:
        value = orders.get(key)
        prefix = '-' if value == -1 else ''
        array.append(f'{prefix}{key}')
    return array
def __translate_condition__(conditions, _type):
    


    return reduce(__fun__,  [Q(**cond[_type]) for cond in conditions])


class OrmQuery:

    def __init__(self, conditions: list , orders = None):
        conditions = conditions or []
        self.orders =  __translate_orders__(orders or {'sort': -1})
        conditions = conditions if len(conditions) else [{'includes':{},'excludes':{}}]
        self.includes = __translate_condition__(conditions,'includes')
        self.excludes = __translate_condition__(conditions, 'excludes')

    @staticmethod
    def is_empty(conditions):
        if conditions and len(conditions):
            temp = {}
            for cond in conditions:
                temp.update(cond)
            return len(temp.keys()) == 0
        else:
            return True






