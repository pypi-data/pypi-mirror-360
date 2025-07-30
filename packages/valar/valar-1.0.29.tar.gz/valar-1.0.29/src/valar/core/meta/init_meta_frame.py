import copy

from .defaults.frame_defaults import meta_field_tool, meta_field_domain

from ...data.models import MetaFieldDomain, MetaFieldTool


def init_meta_frame():
    from ..dao.dao_orm import OrmDao
    tool_dao = OrmDao('data.MetaFieldTool')
    domain_dao = OrmDao('data.MetaFieldDomain')
    mapping = {}
    tool_dao.objects.all().delete()
    for item in meta_field_tool:
        item = copy.deepcopy(item)
        _id, code = item['id'], item['code']
        item.update({"saved": True})
        if item['isLeaf']:
            mapping[code] = _id
        tool_dao.save_one(item, True)
    domain_dao.objects.all().delete()
    for row in meta_field_domain:
        row = copy.deepcopy(row)
        default_id, tools = row['default_id'], row['tools']
        _row = copy.deepcopy(row)
        _row.update({
            'default_id': mapping[default_id],
            'tools': [mapping[tool] for tool in tools],
            "saved": True
        })
        domain_dao.save_one(_row)
    return MetaFieldDomain.objects.all()