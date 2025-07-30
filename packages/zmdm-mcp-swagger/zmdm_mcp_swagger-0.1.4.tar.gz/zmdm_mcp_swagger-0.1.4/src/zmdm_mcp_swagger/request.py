import requests

def fetch_swaggers(url,path_list=None):
    """
    获取Swagger文档
    
    参数:
        url: 要获取的swagger地址
        path_list (list, optional): 要过滤的路径列表。如果提供，则只返回这些路径的API信息。
    """
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en-GB;q=0.7,en;q=0.6",
        "knfie4j-gateway-request": "8ebfe4d7564e38e5fbd7f01304d4b705",
        "knife4j-gateway-code": "ROOT",
        "language": "zh-CN",
        "Referer": "http://172.28.6.86:18000/doc.html",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }
    
    response = requests.get(url, headers=headers)
    
    if not response.ok:
        raise Exception("接口调用失败")
    
    data = response.json()
    
    # 如果提供了path_list，过滤paths字段
    if path_list and isinstance(path_list, list) and "paths" in data:
        filtered_paths = {}
        for path in path_list:
            if path in data["paths"]:
                filtered_paths[path] = data["paths"][path]
        data["paths"] = filtered_paths
    
    return data