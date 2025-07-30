#!/usr/bin/env python3
"""
TypeScript代码生成模块
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Set
from mcp.server.fastmcp import Context

# 从file_utils导入日志和文件操作工具
from src.utils.file_utils import log_info, log_error, ensure_dir_exists

def convert_swagger_to_typescript(swagger_data: Dict, output_dir: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
    """将Swagger定义转换为TypeScript类型"""
    generated_types = {}
    
    try:
        # 准备输出目录和文件路径
        if not os.path.isabs(output_dir):
            output_dir = os.path.abspath(output_dir)
            log_info(ctx, f"使用绝对路径: {output_dir}")
        
        types_file = Path(output_dir) / "types.ts"
        ensure_dir_exists(output_dir)
        
        # 检查权限
        if not os.access(str(types_file.parent), os.W_OK):
            error_msg = f"没有写入权限: {types_file.parent}"
            log_error(ctx, error_msg)
            return {"success": False, "error": error_msg, "output_dir": output_dir}
        
        # 生成内容
        types_content = generate_typescript_content(swagger_data, generated_types, ctx)
        
        # 写入文件
        with open(types_file, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(types_content))
        
        success_msg = f"TypeScript 类型文件已成功写入: {types_file}"
        log_info(ctx, success_msg)
        
        return {
            "success": True,
            "file_path": str(types_file),
            "absolute_path": os.path.abspath(str(types_file)),
            "output_dir": output_dir,
            "types_count": len(generated_types),
            "generated_types": generated_types,
            "message": success_msg,
            "first_few_types": types_content[:min(3, len(types_content))]
        }
        
    except Exception as e:
        error_msg = f"生成TypeScript类型失败: {str(e)}"
        log_error(ctx, error_msg)
        return {"success": False, "error": error_msg}


def generate_typescript_content(swagger_data: Dict, generated_types: Dict, ctx: Optional[Context] = None) -> List[str]:
    """生成TypeScript类型内容"""
    types_content = []
    types_content.append("// 自动生成的 TypeScript 类型定义")
    types_content.append("// 请勿手动修改此文件\n")
    
    # 处理定义
    definitions = swagger_data.get("definitions", {})
    if not definitions and "components" in swagger_data:
        definitions = swagger_data.get("components", {}).get("schemas", {})
    
    # 获取使用的类型引用集合
    all_types = collect_types_from_swagger(swagger_data, definitions)
    
    # 生成TypeScript接口
    if not all_types or "filtered_paths" not in swagger_data:
        log_info(ctx, "生成所有类型定义")
        for def_name, definition in definitions.items():
            sanitized_name = sanitize_type_name(def_name)
            ts_interface = convert_swagger_definition_to_ts(sanitized_name, definition)
            types_content.append(ts_interface)
            generated_types[def_name] = ts_interface
    else:
        log_info(ctx, f"生成 {len(all_types)} 个过滤后的类型定义")
        for def_name in all_types:
            if def_name in definitions:
                sanitized_name = sanitize_type_name(def_name)
                ts_interface = convert_swagger_definition_to_ts(sanitized_name, definitions[def_name])
                types_content.append(ts_interface)
                generated_types[def_name] = ts_interface
    
    # 生成请求和响应类型
    generate_request_response_types(swagger_data, types_content)
    
    return types_content


def generate_request_response_types(swagger_data: Dict, types_content: List[str]) -> None:
    """生成请求和响应类型"""
    if "filtered_paths" in swagger_data:
        paths_to_process = swagger_data.get("filtered_paths", {})
    else:
        paths_to_process = swagger_data.get("paths", {})
    
    for path, methods in paths_to_process.items():
        for method, operation in methods.items():
            if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                request_type, response_type = generate_operation_types(path, method, operation)
                if request_type:
                    types_content.append(request_type)
                if response_type:
                    types_content.append(response_type)


def collect_types_from_swagger(swagger_data: Dict, definitions: Dict) -> Set[str]:
    """从Swagger数据中收集类型引用"""
    # 获取使用的类型引用集合
    used_types = set()
    
    # 判断是否有过滤路径
    if "filtered_paths" in swagger_data:
        paths = swagger_data.get("filtered_paths", {})
    else:
        paths = swagger_data.get("paths", {})
    
    # 收集所有API使用的类型引用
    for path, methods in paths.items():
        for method, operation in methods.items():
            if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                # 检查请求参数
                for param in operation.get("parameters", []):
                    if "$ref" in param:
                        ref = param["$ref"].split("/")[-1]
                        used_types.add(ref)
                    elif "schema" in param and "$ref" in param["schema"]:
                        ref = param["schema"]["$ref"].split("/")[-1]
                        used_types.add(ref)
                
                # 检查响应
                for status, response in operation.get("responses", {}).items():
                    schema = response.get("schema", {})
                    if schema and "$ref" in schema:
                        ref = schema["$ref"].split("/")[-1]
                        used_types.add(ref)
    
    # 递归收集依赖类型
    processed_types = set()
    all_types = set(used_types)
    
    while used_types:
        current_type = used_types.pop()
        processed_types.add(current_type)
        
        if current_type in definitions:
            definition = definitions[current_type]
            properties = definition.get("properties", {})
            
            for _, prop_def in properties.items():
                if "$ref" in prop_def:
                    ref = prop_def["$ref"].split("/")[-1]
                    if ref not in processed_types:
                        used_types.add(ref)
                        all_types.add(ref)
                elif prop_def.get("type") == "array" and "items" in prop_def:
                    items = prop_def["items"]
                    if "$ref" in items:
                        ref = items["$ref"].split("/")[-1]
                        if ref not in processed_types:
                            used_types.add(ref)
                            all_types.add(ref)
    
    return all_types


def sanitize_type_name(name: str) -> str:
    """清理类型名称，移除无效字符，替换中文为拼音或英文"""
    # 替换常见中文后缀
    name = name.replace("对象", "Obj").replace("列表", "List")
    
    # 移除其他非法字符，只保留字母、数字和下划线
    name = re.sub(r'[^\w]', '', name)
    
    # 确保首字母不是数字
    if name and name[0].isdigit():
        name = "T" + name
        
    return name


def convert_swagger_definition_to_ts(name: str, definition: Dict) -> str:
    """将Swagger定义转换为TypeScript接口"""
    lines = [f"export interface {name} {{"]
    
    properties = definition.get("properties", {})
    required = definition.get("required", [])
    
    for prop_name, prop_def in properties.items():
        is_required = prop_name in required
        prop_type = swagger_type_to_ts_type(prop_def)
        optional = "" if is_required else "?"
        
        # 添加注释
        description = prop_def.get("description", "")
        if description:
            lines.append(f"  /** {description} */")
        
        lines.append(f"  {prop_name}{optional}: {prop_type};")
    
    lines.append("}")
    
    return '\n'.join(lines)


def swagger_type_to_ts_type(prop_def: Dict) -> str:
    """将Swagger类型转换为TypeScript类型"""
    prop_type = prop_def.get("type", "any")
    
    if prop_type == "string":
        return "string"
    elif prop_type == "number" or prop_type == "integer":
        return "number"
    elif prop_type == "boolean":
        return "boolean"
    elif prop_type == "array":
        items = prop_def.get("items", {})
        item_type = swagger_type_to_ts_type(items)
        return f"{item_type}[]"
    elif prop_type == "object":
        return "Record<string, any>"
    elif "$ref" in prop_def:
        ref = prop_def["$ref"]
        type_name = ref.split("/")[-1]  # 提取类型名
        return sanitize_type_name(type_name)
    else:
        return "any"


def fix_generic_type(type_str: str) -> str:
    """修复泛型类型表示法，将«»替换为<>"""
    # 替换泛型符号
    type_str = type_str.replace("«", "<").replace("»", ">")
    
    # 处理泛型中的类型名
    def replace_match(match):
        type_name = match.group(1)
        sanitized = sanitize_type_name(type_name)
        return f"<{sanitized}"
    
    # 查找并处理泛型内的所有类型名
    type_str = re.sub(r"<([^<>,]+)(?=[,>])", replace_match, type_str)
    
    return type_str


def generate_operation_types(path: str, method: str, operation: Dict) -> Tuple[Optional[str], Optional[str]]:
    """生成API操作的请求和响应类型"""
    operation_id = operation.get("operationId", f"{method}_{path.replace('/', '_')}")
    
    # 生成请求类型
    request_type = None
    parameters = operation.get("parameters", [])
    if parameters:
        request_props = []
        for param in parameters:
            param_name = param.get("name", "")
            param_type = swagger_type_to_ts_type(param)
            required = param.get("required", False)
            optional = "" if required else "?"
            
            description = param.get("description", "")
            if description:
                request_props.append(f"  /** {description} */")
            
            request_props.append(f"  {param_name}{optional}: {param_type};")
        
        if request_props:
            request_type = f"export interface {operation_id}Request {{\n" + '\n'.join(request_props) + "\n}"
    
    # 生成响应类型
    response_type = None
    responses = operation.get("responses", {})
    if "200" in responses:
        success_response = responses["200"]
        schema = success_response.get("schema", {})
        if schema:
            resp_type = swagger_type_to_ts_type(schema)
            resp_type = fix_generic_type(resp_type)
            response_type = f"export type {operation_id}Response = {resp_type};"
    
    return request_type, response_type


# 服务函数生成部分

def generate_service_functions(api_prefix: str,swagger_data: Dict, output_dir: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
    """生成TypeScript服务函数"""
    generated_services = {}
    
    try:
        # 确保输出目录存在
        ensure_dir_exists(output_dir)
        
        # 生成内容
        service_content = generate_service_content(api_prefix,swagger_data, generated_services, ctx)
        
        # 写入文件
        service_file = Path(output_dir) / "service.ts"
        with open(service_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(service_content))
        
        log_info(ctx, f"服务函数文件已生成: {service_file}")
        log_info(ctx, f"生成了 {len(generated_services)} 个服务函数")
        
        return {
            "success": True,
            "file_path": str(service_file),
            "functions_count": len(generated_services),
            "generated_services": generated_services,
            "message": "服务函数生成成功"
        }
        
    except Exception as e:
        error_msg = f"生成服务函数失败: {str(e)}"
        log_error(ctx, error_msg)
        return {"success": False, "error": error_msg}


def generate_service_content(api_prefix: str,swagger_data: Dict, generated_services: Dict, ctx: Optional[Context] = None) -> List[str]:
    """生成服务内容"""
    service_content = []
    service_content.append("")
    service_content.append("import { requestError } from '@/utils/request';")
    
    # 收集需要导入的类型
    imported_types = set()
    for path, methods in swagger_data.get("filtered_paths", swagger_data.get("paths", {})).items():
        for method, operation in methods.items():
            if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                operation_id = operation.get("operationId")
                if operation_id:
                    if operation.get("parameters", []):
                        imported_types.add(f"{operation_id}Request")
                    imported_types.add(f"{operation_id}Response")
    
    # 添加类型导入
    if imported_types:
        type_imports = ", ".join(sorted(imported_types))
        service_content.append(f"import {{ {type_imports} }} from './types';")
    
    service_content.append("")
    
    # 判断是否有过滤路径
    if "filtered_paths" in swagger_data:
        paths = swagger_data.get("filtered_paths", {})
        log_info(ctx, "使用过滤后的路径生成服务函数")
    else:
        paths = swagger_data.get("paths", {})
        log_info(ctx, "使用所有路径生成服务函数")
    
    # 按标签分组 API
    apis_by_tag = group_apis_by_tag(paths)
    
    # 生成服务函数
    for tag, apis in apis_by_tag.items():
        service_content.append(f"// {tag} 相关 API")
        service_content.append("")
        
        for api in apis:
            func_code = generate_service_function(api_prefix,api["path"], api["method"], api["operation"])
            service_content.append(func_code)
            service_content.append("")
            
            func_name = get_function_name(api["path"], api["method"], api["operation"].get("operationId"))
            generated_services[func_name] = func_code
    
    return service_content


def group_apis_by_tag(paths: Dict) -> Dict:
    """将API按标签分组"""
    apis_by_tag = {}
    
    for path, methods in paths.items():
        for method, operation in methods.items():
            if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                tags = operation.get("tags", ["default"])
                tag = tags[0] if tags else "default"
                
                if tag not in apis_by_tag:
                    apis_by_tag[tag] = []
                
                apis_by_tag[tag].append({
                    "path": path,
                    "method": method.upper(),
                    "operation": operation
                })
    
    return apis_by_tag


def generate_service_function(api_prefix: str, path: str, method: str, operation: Dict) -> str:
    """生成单个服务函数代码"""
    operation_id = operation.get("operationId")
    func_name = get_function_name(path, method, operation_id)
    
    summary = operation.get("summary", "")
    
    # 确定是否有请求类型
    has_request_type = bool(operation.get("parameters", []))
    
    # 使用TypeScript类型作为参数
    if has_request_type:
        param_type = f": {operation_id}Request"
        param_str = f"params{param_type}"
    else:
        param_str = ""
    
    func_lines = []
    if summary:
        func_lines.append(f"/** {summary} */")
    
    func_lines.append(f"export async function {func_name}({param_str}) {{")
    
    # 构建请求 URL
    request_path = path
    
    # 处理路径参数，从params中提取
    path_params = []
    for param in operation.get("parameters", []):
        if param.get("in") == "path":
            path_params.append(param.get("name"))
    
    # 替换URL中的路径参数
    for param in path_params:
        request_path = request_path.replace(f"{{{param}}}", f"${{{f'params.{param}'}}}")
    
    func_lines.append(f"  const url = `{api_prefix}{request_path}`;")
    
    # 构建请求选项
    options = [f"method: '{method.upper()}'"]
    options.append(f"url: url")
    
    # 检查是否有查询参数
    has_query_params = any(param.get("in") == "query" for param in operation.get("parameters", []))
    has_body_param = any(param.get("in") == "body" for param in operation.get("parameters", []))
    
    if has_query_params:
        options.append(f"params: params")
    
    if has_body_param:
        # 使用params作为请求体数据
        options.append(f"data: params")
    
    options_str = "{\n    " + ",\n    ".join(options) + "\n  }"
    
    # 添加返回语句，并使用生成的响应类型
    func_lines.append(f"  return requestError<{operation_id}Response>({options_str});")
    func_lines.append("}")
    
    return '\n'.join(func_lines)


def build_function_parameters(operation: Dict) -> Tuple[List[str], List[str], List[str], Optional[str]]:
    """构建函数参数"""
    parameters = operation.get("parameters", [])
    params = []
    path_params = []
    query_params = []
    body_param = None
    
    for param in parameters:
        param_name = param.get("name", "")
        param_in = param.get("in", "")
        
        if param_in == "path":
            path_params.append(param_name)
        elif param_in == "query":
            query_params.append(param_name)
        elif param_in == "body":
            body_param = param_name
    
    return params, path_params, query_params, body_param


def get_function_name(path: str, method: str, operation_id: str = None) -> str:
    """生成函数名"""
    if operation_id:
        return operation_id
    
    # 从路径生成函数名
    path_parts = [part for part in path.split('/') if part and not part.startswith('{')]
    path_name = ''.join([part.capitalize() for part in path_parts])
    
    method_prefix = {
        'GET': 'get',
        'POST': 'create',
        'PUT': 'update',
        'DELETE': 'delete',
        'PATCH': 'patch'
    }.get(method.upper(), method.lower())
    
    return f"{method_prefix}{path_name}" 