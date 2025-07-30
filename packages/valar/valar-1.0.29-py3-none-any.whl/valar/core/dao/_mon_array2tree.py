def array2tree(data, mapping):
    mapping = mapping or {}
    lookup = {}
    for array in data:
        for i in range(len(array)):
            key = '/'.join(array[0:i+1])
            item = mapping.get(key, {})
            value = item.get('value', array[i])
            label = item.get('label', value)
            display = item.get('display')
            item = lookup.get(key, {'value': value,'label':label,'display':display})
            if i < len(array) -1:
                item['children'] = item.get('children', [])
            lookup[key] = item
            if i > 0:
                parent =   '/'.join(array[0:i])
                lookup[parent]['children'].append(lookup[key])
    return [lookup[root] for root in [*set([array[0] for array in data])]]