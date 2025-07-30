
meta_field_value_defaults = {
    'data.MetaFieldDomain':{
        "__init__":{
            "default_id":{
                "tool":"tree"
            },
            "search_id":{
                "tool":"tree"
            },
            "tools":{
                "tool":"tree",
                "refer": {
                    "display":"code"
                }
            },
            "align":{
                "tool":"set",
                "format":{
                    "set": {
                        'left':'左对齐',
                        'right':'右对齐',
                        'center':'剧中对齐',
                    }
                }
            }
        }
    },
    'data.MetaField':{
        "__init__":{
            "column_width":{
                'unit':'px'
            },
            "fixed":{
                "tool":"set",
                "format":{
                    "set": {
                        'left':'左侧固定',
                        'right':'右侧固定',
                    }
                }
            },
            "align":{
                "tool":"set",
                "format":{
                    "set": {
                        'left':'左对齐',
                        'right':'右对齐',
                        'center':'剧中对齐',
                    }
                }
            },
            "prop":{
                'allow_edit': False,
                'column_width': 120
            },
            "domain":{
                'allow_edit': False,
                'column_width': 120,
            },
            "tool":{
                'column_width': 100,
                'tool': 'tree',
                'refer': {
                    'entity':'data.MetaFieldTool',
                    'includes': {'metafielddomain__name':'${domain}'},
                    'value': 'code','display':'code'
                }

            },
            "span":{
                'column_width': 100,
                "format": { "min": 0, "max": 24, "step": 1, "precision": 0, "step_strictly": True }
            },
            "refer":{
                'allow_edit': False,
                'column_width': 80
            },
            "format":{
                'allow_edit': False,
                'column_width': 80
            },
        }
    }
}