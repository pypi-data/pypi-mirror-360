
def __translate_finder__(conditions):
    return {}


class MonQuery:

    def __init__(self, conditions: list, orders = None):
        self.orders = orders or {'sort': -1}
        conditions = conditions if len(conditions) else [{'includes':{},'excludes':{}}]
        self.finder = __translate_finder__(conditions)

