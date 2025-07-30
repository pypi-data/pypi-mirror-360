
meta_field_tool = [
    {'id': 2, 'sort': 32, 'pid': 7, 'isLeaf': True, 'name': '输入框', 'code': 'text'},
    {'id': 3, 'sort': 17, 'pid': 0, 'isLeaf': False, 'name': 'SPEC', 'code': '特殊工具集'},
    {'id': 5, 'sort': 22, 'pid': 0, 'isLeaf': False, 'name': 'DATE', 'code': '日期时间工具集'},
    {'id': 6, 'sort': 21, 'pid': 8, 'isLeaf': True, 'name': '数字输入', 'code': 'number'},
    {'id': 7, 'sort': 36, 'pid': 0, 'isLeaf': False, 'name': 'TEXT', 'code': '文本工具集'},
    {'id': 8, 'sort': 26, 'pid': 0, 'isLeaf': False, 'name': 'NUMB', 'code': '数字工具集'},
    {'id': 9, 'sort': 10, 'pid': 0, 'isLeaf': False, 'name': 'FILE', 'code': '文件工具集'},
    {'id': 10, 'sort': 27, 'pid': 0, 'isLeaf': False, 'name': 'BOOL', 'code': '逻辑工具集'},
    {'id': 11, 'sort': 31, 'pid': 0, 'isLeaf': False, 'name': 'LIST', 'code': '列表工具集'},
    {'id': 12, 'sort': 8, 'pid': 3, 'isLeaf': True, 'name': '对象', 'code': 'object'},
    {'id': 13, 'sort': 5, 'pid': 9, 'isLeaf': True, 'name': '图片上传', 'code': 'image'},
    {'id': 14, 'sort': 2, 'pid': 9, 'isLeaf': True, 'name': '文件上传', 'code': 'file'},
    {'id': 15, 'sort': 13, 'pid': 9, 'isLeaf': True, 'name': '富文本', 'code': 'rich'},
    {'id': 17, 'sort': 11, 'pid': 10, 'isLeaf': True, 'name': '开关', 'code': 'switch'},
    {'id': 18, 'sort': 7, 'pid': 3, 'isLeaf': True, 'name': '元数据', 'code': 'meta'},
    {'id': 19, 'sort': 9, 'pid': 7, 'isLeaf': True, 'name': '颜色选择', 'code': 'color'},
    {'id': 20, 'sort': 14, 'pid': 11, 'isLeaf': True, 'name': '穿梭框', 'code': 'transfer'},
    {'id': 21, 'sort': 16, 'pid': 7, 'isLeaf': True, 'name': '自动填充', 'code': 'auto'},
    {'id': 22, 'sort': 35, 'pid': 5, 'isLeaf': True, 'name': '日期选择', 'code': 'date'},
    {'id': 23, 'sort': 12, 'pid': 10, 'isLeaf': True, 'name': '逻辑选择', 'code': 'boolean'},
    {'id': 24, 'sort': 24, 'pid': 11, 'isLeaf': True, 'name': '列表选择', 'code': 'select'},
    {'id': 25, 'sort': 15, 'pid': 11, 'isLeaf': True, 'name': '树形选择', 'code': 'tree'},
    {'id': 26, 'sort': 23, 'pid': 11, 'isLeaf': True, 'name': '及联选择', 'code': 'cascade'},
    {'id': 28, 'sort': 25, 'pid': 7, 'isLeaf': True, 'name': '图标', 'code': 'icon'},
    {'id': 31, 'sort': 6, 'pid': 0, 'isLeaf': True, 'name': '无', 'code': 'none'},
    {'id': 32, 'sort': 30, 'pid': 7, 'isLeaf': True, 'name': '文本框', 'code': 'textarea'},
    {'id': 33, 'sort': 18, 'pid': 36, 'isLeaf': True, 'name': '时间区间', 'code': 'timerange'},
    {'id': 35, 'sort': 33, 'pid': 5, 'isLeaf': True, 'name': '时间选择', 'code': 'time'},
    {'id': 36, 'sort': 20, 'pid': 0, 'isLeaf': False, 'name': 'RANGE', 'code': '区间工具集'},
    {'id': 37, 'sort': 38, 'pid': 36, 'isLeaf': True, 'name': '日期区间', 'code': 'daterange'},
    {'id': 39, 'sort': 3, 'pid': 36, 'isLeaf': True, 'name': '多日期', 'code': 'dates'},
    {'id': 54, 'sort': 54, 'pid': 7, 'isLeaf': True, 'name': '集合', 'code': 'set'}
]

meta_field_domain = [
    {
        'name': 'CharField',
        'default_id': 'text', 'align': 'left',
        'tools': [
            'text', 'number', 'meta', 'color', 'auto', 'date', 'time','select', 'tree', 'cascade', 'icon',
            'textarea', 'timerange', 'daterange', 'dates', 'set'
        ]
     },
    {
        'name': 'TextField',
        'default_id': 'textarea', 'align': 'left',
        'tools': ['text', 'textarea', 'rich']
    },
    {
        'name': 'BooleanField',
        'default_id': 'switch', 'align': 'center',
        'tools': ['switch', 'boolean']
    },
    {
        'name': 'IntegerField',
        'default_id': 'number', 'align': 'right',
        'tools': ['number']
    },
    {
        'name': 'FloatField',
        'default_id': 'number', 'align': 'right',
        'tools': ['number']
    },
    {
        'name': 'ForeignKey',
        'default_id': 'select', 'align': 'left',
        'tools': ['select', 'tree', 'cascade']
    },
    {
        'name': 'ManyToOneRel',
        'default_id': 'select', 'align': 'center',
        'tools': ['transfer', 'select', 'tree', 'cascade']
    },
    {
        'name': 'ManyToManyField',
        'default_id': 'select', 'align': 'center',
        'tools': [ 'transfer', 'select', 'tree', 'cascade']
    },
    {
        'name': 'ManyToManyRel',
        'default_id': 'select', 'align': 'center',
        'tools': ['transfer', 'select', 'tree', 'cascade']
    },
    {
        'name': 'OneToOneRel',
        'default_id': 'none', 'align': 'left',
        'tools': []
    },
    {
        'name': 'OneToOneField',
        'default_id': 'none', 'align': 'left',
        'tools': []
    },
    {
        'name': 'DateField',
        'default_id': 'date', 'align': 'center',
        'tools': ['date']
    },
    {
        'name': 'TimeField',
        'default_id': 'time', 'align': 'center',
        'tools': ['time']
    },
    {
        'name': 'DateTimeField',
        'default_id': 'date', 'align': 'center',
        'tools': ['date']
    },
    {
        'name': 'JSONField',
        'default_id': 'object', 'align': 'center',
        'tools': ['object']
    },
    {
        'name': 'FileField',
        'default_id': 'file', 'align': 'center',
        'tools': ['image', 'file']
    },
    {
        'name': 'BigAutoField',
        'default_id': 'none', 'align': 'right',
        'tools': []
    },
    {
        'name': 'UUIDField',
        'default_id': 'none', 'align': 'left',
        'tools': []
    },
    {
        'name': 'Custom',
        'default_id': 'none', 'align': 'left',
        'tools': []
    },
]
