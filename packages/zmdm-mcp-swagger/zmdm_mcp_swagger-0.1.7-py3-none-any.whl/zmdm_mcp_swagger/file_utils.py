#!/usr/bin/env python3
"""
文件操作工具模块
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from mcp.server.fastmcp import Context

def ensure_dir_exists(directory_path: str) -> None:
    """确保目录存在"""
    Path(directory_path).mkdir(parents=True, exist_ok=True)

def safe_write_file(file_path: Path, content: str, ctx: Optional[Context] = None) -> None:
    """安全写入文件，确保目录存在且具有写权限"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 检查写入权限
        if not os.access(str(file_path.parent), os.W_OK):
            error_msg = f"没有写入权限: {file_path.parent}"
            log_error(ctx, error_msg)
            raise PermissionError(error_msg)
            
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    except Exception as e:
        error_msg = f"写入文件失败: {str(e)}, 路径: {file_path}"
        log_error(ctx, error_msg)
        raise

def verify_file(file_path: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
    """验证文件是否存在并返回内容预览"""
    # 确保使用绝对路径
    if not os.path.isabs(file_path):
        abs_path = os.path.abspath(file_path)
    else:
        abs_path = file_path
    
    log_info(ctx, f"验证文件: {abs_path}")
    
    if not os.path.exists(abs_path):
        error_msg = f"文件不存在: {abs_path}"
        log_error(ctx, error_msg)
        return {
            "success": False, 
            "error": error_msg, 
            "exists": False
        }
    
    # 读取文件内容
    with open(abs_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 获取文件大小
    file_size = os.path.getsize(abs_path)
    
    # 获取文件目录列表
    dir_path = os.path.dirname(abs_path)
    try:
        dir_files = os.listdir(dir_path)
    except:
        dir_files = ["无法读取目录"]
    
    return {
        "success": True,
        "exists": True,
        "file_path": file_path,
        "absolute_path": abs_path,
        "file_size": file_size,
        "content_preview": content[:500] + ("..." if len(content) > 500 else ""),
        "dir_files": dir_files
    }

def log_info(ctx, message):
    """记录信息日志"""
    if ctx:
        ctx.info(message)
    else:
        print(message)

def log_error(ctx, message):
    """记录错误日志"""
    if ctx:
        ctx.error(message)
    else:
        print(message) 