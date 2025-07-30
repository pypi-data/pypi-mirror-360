#!/usr/bin/env python3
"""
配置生成模块
"""

from typing import Dict, Any

def generate_mock_config(config_type: str) -> Dict[str, Any]:
    """
    根据配置类型生成模拟配置文件
    
    Args:
        config_type: 配置类型 (form, table, chart)
        
    Returns:
        配置数据字典
    """
    configs = {
        "form": {
            "type": "form",
            "title": "表单配置",
            "fields": [
                {
                    "name": "name",
                    "label": "姓名",
                    "type": "input",
                    "required": True,
                    "rules": [{"required": True, "message": "请输入姓名"}]
                },
                {
                    "name": "email",
                    "label": "邮箱",
                    "type": "input",
                    "inputType": "email",
                    "required": True,
                    "rules": [
                        {"required": True, "message": "请输入邮箱"},
                        {"type": "email", "message": "请输入正确的邮箱格式"}
                    ]
                }
            ],
            "submitButton": {
                "text": "提交",
                "loading": False
            }
        },
        "table": {
            "type": "table",
            "title": "表格配置",
            "columns": [
                {
                    "key": "id",
                    "title": "ID",
                    "width": 80,
                    "align": "center"
                },
                {
                    "key": "name",
                    "title": "名称",
                    "width": 150
                },
                {
                    "key": "status",
                    "title": "状态",
                    "width": 100,
                    "render": "tag"
                },
                {
                    "key": "actions",
                    "title": "操作",
                    "width": 120,
                    "render": "actions",
                    "actions": ["edit", "delete"]
                }
            ],
            "pagination": {
                "pageSize": 10,
                "showSizeChanger": True,
                "showQuickJumper": True
            }
        },
        "chart": {
            "type": "chart",
            "title": "图表配置",
            "chartType": "line",
            "data": {
                "xAxis": "date",
                "yAxis": "value",
                "series": [
                    {
                        "name": "销售额",
                        "color": "#1890ff"
                    }
                ]
            },
            "options": {
                "responsive": True,
                "legend": {
                    "display": True,
                    "position": "top"
                },
                "scales": {
                    "x": {
                        "display": True,
                        "title": "日期"
                    },
                    "y": {
                        "display": True,
                        "title": "数值"
                    }
                }
            }
        }
    }
    
    return configs.get(config_type, {"type": config_type, "config": "未知配置类型"}) 