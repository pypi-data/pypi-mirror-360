__mf_common__ = ['prop','name']

meta_field_key_defaults = {
    'data.Meta': {
        'default': ('pick', ['entity','name']),
    },
    'data.MetaView': {
        'list': ('pick', ['meta_id','code','view_name']),
    },
    'data.MetaField': {
        'add': ('pick',['prop','domain','name']),
        'tool': ('pick',[*__mf_common__,'domain','tool','refer','format']),
        'rest': ('pick',[*__mf_common__,'not_null','allow_edit','allow_sort','allow_search','allow_download','allow_upload','allow_update']),
        'table': ('pick',[*__mf_common__,'unit','column_width','fixed','align','edit_on_table','hide_on_table','header_color','cell_color']),
        'form': ('pick',[*__mf_common__,'hide_on_form','hide_on_form_insert','hide_on_form_edit','hide_on_form_branch','hide_on_form_leaf','span']),
    }
}