#!/usr/bin/env python3
"""
Swagger相关辅助函数模块
"""

from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import Context

def process_swagger_data(swagger_data: Dict, filter_paths: List[str] = None, ctx: Context = None) -> Dict[str, Any]:
    """
    处理Swagger数据，提取关键信息和过滤路径
    
    Args:
        swagger_data: Swagger API 文档数据
        filter_paths: 要过滤的路径列表
        ctx: MCP上下文对象
    """
    # 提取关键信息
    info = {
        "title": swagger_data.get("info", {}).get("title", "API"),
        "version": swagger_data.get("info", {}).get("version", "1.0.0"),
        "base_path": swagger_data.get("basePath", ""),
        "host": swagger_data.get("host", ""),
        "schemes": swagger_data.get("schemes", ["http"]),
        "paths_count": len(swagger_data.get("paths", {})),
        "definitions_count": len(swagger_data.get("definitions", {}))
    }
    
    # 过滤路径
    paths = swagger_data.get("paths", {})
    filtered_paths = {}
    
    if filter_paths:
        log_message(ctx, f"应用路径过滤: {filter_paths}")
            
        for path in filter_paths:
            if path in paths:
                filtered_paths[path] = paths[path]
        
        # 更新swagger_data中的paths为过滤后的路径
        swagger_data["filtered_paths"] = filtered_paths
        
        log_message(ctx, f"过滤后的路径数量: {len(filtered_paths)}")
    else:
        filtered_paths = paths
    
    log_message(ctx, f"成功获取 API 信息: {info['title']} v{info['version']}")
    log_message(ctx, f"包含 {len(filtered_paths)} 个过滤后的接口和 {info['definitions_count']} 个定义")
    
    return {
        "success": True,
        "info": info,
        "paths": list(filtered_paths.keys())[:10],  # 只返回前10个路径作为预览
        "filtered": bool(filter_paths),
        "message": "Swagger 信息获取成功"
    }

def log_message(ctx, message):
    """记录消息"""
    if ctx:
        ctx.info(message)
    else:
        print(message) 