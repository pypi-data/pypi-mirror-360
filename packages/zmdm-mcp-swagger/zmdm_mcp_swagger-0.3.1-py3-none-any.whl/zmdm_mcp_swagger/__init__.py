#!/usr/bin/env python3
"""
MCP 代码生成服务器
功能：
1. 获取 Swagger 接口信息
2. 生成 TypeScript 类型和服务函数
3. 根据模板生成页面代码
4. 根据用户上传图片生成配置文件
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP, Context

# 导入拆分后的各个模块
from zmdm_mcp_swagger.request import fetch_swaggers
from zmdm_mcp_swagger.swagger_helper import process_swagger_data
from zmdm_mcp_swagger.typescript_generator import (
    convert_swagger_to_typescript,
    generate_service_functions as gen_services
)
from zmdm_mcp_swagger.config_generator import generate_mock_config
from zmdm_mcp_swagger.file_utils import safe_write_file, ensure_dir_exists, verify_file

app = FastMCP("代码生成器")

# 全局存储
swagger_data = {}
generated_types = {}
generated_services = {}

@app.tool()
def fetch_swagger_info(swagger_url: str, filter_paths: List[str] = None, ctx: Context = None) -> Dict[str, Any]:
    """
    获取 Swagger 接口信息
    
    Args:
        swagger_url: 要获取的swagger地址
        filter_paths: 要过滤的路径列表，只处理这些路径对应的API (可选)
    """
    global swagger_data
    
    try:
        swagger_data = fetch_swaggers(swagger_url,filter_paths)
        result = process_swagger_data(swagger_data, filter_paths, ctx)
        return result
    except Exception as e:
        log_error(ctx, f"获取 Swagger 信息失败: {str(e)}")
        return {"success": False, "error": str(e)}

@app.tool()
def generate_typescript_types(output_dir: str = None, ctx: Context = None) -> Dict[str, Any]:
    """
    根据 Swagger 定义生成 TypeScript 类型
    
    Args:
        output_dir: 输出当前项目的绝对目录路径，如：/Users/xxx/业务项目
    """
    global swagger_data, generated_types
    
    if not swagger_data:
        return {"success": False, "error": "请先调用 fetch_swagger_info 获取 API 信息"}
    
    try:
        log_info(ctx, "开始生成 TypeScript 类型...")
        
        # 如果未指定输出目录，则使用当前目录下的types目录
        if output_dir is None:
            current_dir = os.getcwd()
            output_dir = os.path.join(current_dir, "types")
            log_info(ctx, f"未指定输出目录，使用默认目录: {output_dir}")
        
        # 确保输出目录存在
        ensure_dir_exists(output_dir)
        
        # 生成TypeScript类型定义
        result = convert_swagger_to_typescript(
            swagger_data, 
            output_dir, 
            ctx
        )
        
        generated_types = result.get("generated_types", {})
        return result
        
    except Exception as e:
        log_error(ctx, f"生成 TypeScript 类型失败: {str(e)}")
        return {"success": False, "error": str(e)}

@app.tool()
def generate_service_functions(api_prefix: str, output_dir: str = None, ctx: Context = None) -> Dict[str, Any]:
    """
    生成 TypeScript 服务函数到 service.ts 文件
    
    Args:
        api_prefix: 请求url前缀
        output_dir: 输出目录路径
    """
    global swagger_data, generated_services
    
    if not swagger_data:
        return {"success": False, "error": "请先调用 fetch_swagger_info 获取 API 信息"}
    
    try:
        log_info(ctx, "开始生成服务函数...")
        
        # 确保输出目录存在
        ensure_dir_exists(output_dir)
        
        # 生成服务函数
        result = gen_services(api_prefix,swagger_data, output_dir, ctx)
        generated_services = result.get("generated_services", {})
        
        return result
        
    except Exception as e:
        log_error(ctx, f"生成服务函数失败: {str(e)}")
        return {"success": False, "error": str(e)}

# @app.tool()
# def generate_page_from_template(
#     page_name: str,
#     api_functions: List[str],
#     output_dir: str = "./pages",
#     ctx: Context = None
# ) -> Dict[str, Any]:
#     """
#     根据模板生成页面代码，自动引入类型和服务函数
    
#     Args:
#         page_name: 页面名称
#         api_functions: 要使用的 API 函数名列表
#         output_dir: 输出目录路径
#     """
#     try:
#         log_info(ctx, f"开始生成页面: {page_name}")
        
#         # 确保输出目录存在
#         ensure_dir_exists(output_dir)
        
#         # 从output_dir路径提取module_name和feature_name
#         # 解析路径，例如: D:\code\prm\zmdms-newprm-front\src\pages\modules\transaction\futures\accountfuture
#         path_parts = Path(output_dir).parts
        
#         # 查找modules在路径中的位置
#         modules_index = -1
#         for i, part in enumerate(path_parts):
#             if part.lower() == "modules":
#                 modules_index = i
#                 break
        
#         # 默认值
#         module_name = page_name
#         feature_name = page_name
        
#         # 如果找到了modules，提取后面的两级和最后一级作为module_name和feature_name
#         if modules_index != -1 and len(path_parts) > modules_index + 2:
#             # 路径中，modules之后的两级作为module_name
#             module_parts = path_parts[modules_index+1:modules_index+3]
#             module_name = os.path.join(*module_parts) if len(module_parts) > 1 else module_parts[0]
            
#             # 最后一级作为feature_name
#             feature_name = path_parts[-1]
        
#         log_info(ctx, f"提取的module_name: {module_name}, feature_name: {feature_name}")
        
#         # 生成导入语句
#         imports = []
#         if api_functions:
#             func_imports = ", ".join(api_functions)
#             imports.append(f"import {{ {func_imports} }} from '@/services/api-service';")
        
#         # 生成各种文件
#         files_to_generate = {
#             # 按钮配置
#             "button.ts": generate_button_file(module_name, feature_name),
            
#             # 路由配置
#             "routes.ts": generate_routes_file(module_name, feature_name, page_name),
            
#             # 枚举定义
#             "enum.ts": generate_enum_file(),
            
#             # 列表页相关文件
#             "list/index.tsx": generate_list_index_file(api_functions),
#             "list/operation.tsx": generate_list_operation_file(),
#             "list/search-form.tsx": generate_list_search_form_file(),
#             "list/table-list.tsx": generate_list_table_file(),
            
#             # 表单页相关文件
#             "making/index.tsx": generate_making_index_file(api_functions),
#             "making/edit-form.tsx": generate_making_edit_form_file(),
            
#             # 详情页相关文件
#             "detail/index.tsx": generate_detail_index_file(api_functions),
#             "detail/detail-form.tsx": generate_detail_form_file(),
#         }
        
#         # 写入文件
#         generated_files = []
#         for file_name, content in files_to_generate.items():
#             file_path = Path(output_dir) / file_name
#             # 确保目录存在
#             file_path.parent.mkdir(parents=True, exist_ok=True)
#             safe_write_file(file_path, content, ctx)
#             generated_files.append(str(file_path))
#             log_info(ctx, f"生成文件: {file_path}")
        
#         return {
#             "success": True,
#             "generated_files": generated_files,
#             "module_name": module_name,
#             "feature_name": feature_name,
#             "page_name": page_name,
#             "message": f"页面代码生成成功，共生成 {len(generated_files)} 个文件"
#         }
        
#     except Exception as e:
#         log_error(ctx, f"生成页面代码失败: {str(e)}")
#         return {"success": False, "error": str(e)}

# 以下是各个文件的生成函数
def generate_button_file(module_name: str, feature_name: str) -> str:
    """生成按钮配置文件"""
    return f'''/**
 * 这个页面是用来配置按钮的权限code的文件。
 * 注意：通常权限按钮配置在模块的列表页。
 * 注意：通常权限按钮的code：以 系统:模块:功能 来命名。
 */
import {{ getButtonAuthsConstants }} from "@/common-utils/utils";

const key = "prm:{module_name.replace("/", ":")}:{feature_name}:";

const buttonAuths = {{
  // 这里会有一些常用的已经定义好的权限按钮code。
  ...getButtonAuthsConstants(key),
}};

const buttonAuthsArray = Object.values(buttonAuths);

export {{ buttonAuths, buttonAuthsArray }};
'''

def generate_routes_file(module_name: str, feature_name: str, page_name: str) -> str:
    """生成路由配置文件"""
    return f'''import {{ IRouteProp }} from "@/routes/utils/types";
import {{ pathHandle }} from "@/common-utils/utils";

type PathType = "list" | "making" | "patch" | "approve" | "detail";
const paths = {{
  list: "/{feature_name}/list",
  making: "/{feature_name}/making",
  patch: "/{feature_name}/making/:id",
  approve: "/{feature_name}/approve/:id",
  detail: "/{feature_name}/detail/:id",
}};
export const RoutesPaths = (type: PathType, id?: string | number | boolean) => {{
  return pathHandle(paths, type, id);
}};

const routes: IRouteProp[] = [
  {{
    path: RoutesPaths("list"),
    component: () => import("./list"),
    name: "{page_name}",
    isAuth: true,
  }},
  {{
    path: RoutesPaths("making"),
    component: () => import("./making"),
    name: "{page_name}新增",
    isAuth: true,
  }},
  {{
    path: RoutesPaths("patch"),
    component: () => import("./making"),
    name: "{page_name}修改",
    isAuth: true,
  }},
  {{
    path: RoutesPaths("approve"),
    component: () => import("./approve"),
    name: "{page_name}审批",
    isAuth: true,
  }},
  {{
    path: RoutesPaths("detail"),
    component: () => import("./detail"),
    name: "{page_name}详情",
    isAuth: true,
  }},
];
export default routes;
'''

def generate_enum_file() -> str:
    """生成枚举定义文件"""
    return '''export enum StatusEnum {
  DRAFT = 0, // 草稿
  DISCARD = -1, // 作废
  PROCESSING = 1, // 流程中
  FINISHED = 2, // 已完成
}
'''

# def generate_form_config_file(api_functions: List[str]) -> str:
#     """生成表单配置文件"""
#     return '''import { useCallback } from "react";
# import type { IFormItemProps } from "@/components/common/components/form";

# // 列表页表单配置
# export const useListItems = () => {
#   return [
#     {
#       label: "关键字",
#       name: "keyword",
#       type: "input",
#       placeholder: "请输入关键字",
#     },
#     {
#       label: "状态",
#       name: "status",
#       type: "select",
#       options: [
#         { label: "全部", value: "" },
#         { label: "草稿", value: 0 },
#         { label: "流程中", value: 1 },
#         { label: "已完成", value: 2 },
#         { label: "已作废", value: -1 },
#       ],
#     },
#   ];
# };

# // 新增/编辑页表单配置
# export const useMakingItems = useCallback(({ table } = {}) => {
#   return [
#     {
#       label: "标题",
#       name: "title",
#       type: "input",
#       placeholder: "请输入标题",
#       rules: [{ required: true, message: "请输入标题" }],
#     },
#     {
#       label: "描述",
#       name: "description",
#       type: "textarea",
#       placeholder: "请输入描述",
#     },
#     {
#       label: "明细",
#       type: "tableEdit",
#       table,
#       columns: [
#         {
#           title: "名称",
#           dataIndex: "name",
#           width: 200,
#           render: {
#             type: "input",
#             placeholder: "请输入名称",
#             rules: [{ required: true, message: "请输入名称" }],
#           },
#         },
#         {
#           title: "数量",
#           dataIndex: "quantity",
#           width: 150,
#           render: {
#             type: "inputNumber",
#             placeholder: "请输入数量",
#             rules: [{ required: true, message: "请输入数量" }],
#           },
#         },
#       ],
#     },
#   ];
# }, []);
# '''

# def generate_table_config_file(api_functions: List[str]) -> str:
#     """生成表格配置文件"""
#     return '''import { useCallback } from "react";

# export const useListColumns = useCallback(({ operation } = {}) => {
#   return [
#     {
#       title: "序号",
#       dataIndex: "index",
#       width: 80,
#       render: (_, __, index) => index + 1,
#     },
#     {
#       title: "标题",
#       dataIndex: "title",
#       width: 200,
#     },
#     {
#       title: "描述",
#       dataIndex: "description",
#       width: 300,
#     },
#     {
#       title: "创建时间",
#       dataIndex: "createTime",
#       width: 180,
#     },
#     {
#       title: "状态",
#       dataIndex: "status",
#       width: 100,
#       render: (status) => {
#         const statusMap = {
#           0: "草稿",
#           1: "流程中",
#           2: "已完成",
#           "-1": "已作废",
#         };
#         return statusMap[status] || "-";
#       },
#     },
#     {
#       title: "操作",
#       dataIndex: "operation",
#       width: 120,
#       fixed: "right",
#       render: operation,
#     },
#   ];
# }, []);
# '''

def generate_list_index_file(api_functions: List[str]) -> str:
    """生成列表页主文件"""
    return '''import React from "react";
// 公用组件引入
import {
  SearchList,
  LinkButton,
  message,
  ExportButton,
} from "@/components/common";
// 业务组件引入
import SearchForm from "./search-form";
import TableList from "./table-list";
import { useNavigate } from "@/hooks/use-route";
import useBasicUser from "@/hooks/use-basic-user";
// api接口
import { pageUsingGET, exportUsingPOST } from "../service";
import { buttonAuths } from "../button";
import { RoutesPaths } from "../routes";
import { StatusEnum } from "../enum";

const List: React.FC = () => {
  const navigate = useNavigate();
  const { userInfo } = useBasicUser();
  // 默认查询参数
  const defaultParams = {
    orgId: userInfo?.firstUnitId,
    subOrgId: userInfo?.secondUnitId,
  };

  const onAdd = () => {
    navigate(RoutesPaths("making"));
  };

  const onReference = (selectedRows) => {
    if (selectedRows?.length !== 1) {
      message.warning("请先选择一条数据!");
      return;
    }
    navigate(RoutesPaths("making"), {
      state: {
        createId: selectedRows[0]?.id,
      },
    });
  };

  return (
    <SearchList
      isInit
      fetchList={pageUsingGET}
      stateKey={RoutesPaths("list")}
      defaultParams={defaultParams}
      formSearch={(props) => {
        return <SearchForm {...props} />;
      }}
      table={(props) => {
        return <TableList {...props} />;
      }}
      middle={({ selectedRows }) => {
        return (
          <>
            <LinkButton
              type="primary"
              onClick={onAdd}
              path={RoutesPaths("list")}
              authority={buttonAuths["add"]}
            >
              新建
            </LinkButton>
            <LinkButton
              type="primary"
              onClick={() => onReference(selectedRows)}
              path={RoutesPaths("list")}
              authority={buttonAuths["referenceCreate"]}
            >
              复制新建
            </LinkButton>
            <ExportButton
              request={exportUsingPOST}
              path={RoutesPaths("list")}
              authority={buttonAuths["excelExport"]}
            >
              列表导出
            </ExportButton>
          </>
        );
      }}
    />
  );
};

export default List;
'''

def generate_list_operation_file() -> str:
    """生成列表操作按钮文件"""
    return '''import { message, Operation } from "@/components/common";
import { useLocation } from "react-router-dom";
import { useNavigate } from "@/hooks/use-route";
import { StatusEnum } from "../enum";
import { buttonAuths } from "../button";
import { RoutesPaths } from "../routes";
import { updateStatus } from "../service";

interface IOperationProps {
  record: any;
  onReload: () => void;
}
const OperationButtons = ({ record, onReload }: IOperationProps) => {
  const navigate = useNavigate();
  const { pathname } = useLocation();

  const buttons = {
    modify: {
      name: "编辑",
      type: buttonAuths.modify,
      authority: buttonAuths.modify,
    },
    cancel: {
      name: "作废",
      type: buttonAuths.cancel,
      confirmMsg: "是否确定作废？",
      authority: buttonAuths.cancel,
    },
  } as const;

  const onClick = async (type) => {
    let request;
    let params: any = {};
    switch (type) {
      case buttonAuths.modify: {
        navigate(RoutesPaths("patch", record.id));
        break;
      }
      case buttonAuths.cancel: {
        request = updateStatus;
        params = {
          id: record.id,
          status: StatusEnum.DISCARD,
        };
        break;
      }
    }
    async function func(req, params) {
      if (!req) return;
      const res = await req(params);
      if (res?.success) {
        message.success(res.msg);
        onReload();
      } else {
        message.error(res.msg);
      }
    }

    func(request, params);
  };

  return (
    <Operation
      status={record?.status}
      path={pathname}
      onClick={onClick}
      // 这里用来设置每个状态下对应的按钮种类。
      buttons={{
        [StatusEnum.DRAFT]: [buttons.modify, buttons.cancel],
      }}
    ></Operation>
  );
};

export default OperationButtons;
'''

def generate_list_search_form_file() -> str:
    """生成列表查询表单文件"""
    return '''// 公用组件引入
import { Form } from "@/components/common";
import type { IFormItemProps } from "@/components/common/components/form";
import { useListItems } from "../config/form-config";

const SearchForm = (props) => {
  const listItems: IFormItemProps[] = useListItems();
  return (
    <Form
      {...props}
      items={listItems}
      rightWrapVisible
      isToggle
      isResetAndClear
    />
  );
};

export default SearchForm;
'''

def generate_list_table_file() -> str:
    """生成列表表格文件"""
    return '''import React, { memo } from "react";
// 公用组件引入
import { Table } from "@/components/common";
import { useListColumns } from "../config/table-config";
import Operation from "./operation";

interface IProps {
  records: any;
  dynamicKey: string;
  selectedRowKeys: string[];
  selectedRowChange: (keys, rows) => void;
  onReload: any;
  extra?: any;
}

const TableList: React.FC<IProps> = ({
  records,
  dynamicKey,
  selectedRowKeys,
  selectedRowChange,
  onReload,
}) => {
  const columns = useListColumns({
    operation: ({ record }) => {
      return <Operation record={record} onReload={onReload}></Operation>;
    },
  });
  return (
    <Table
      rowKey="id"
      dataSource={records}
      columns={columns}
      isFlex
      dynamicKey={dynamicKey}
      rowSelection={{
        type: "checkbox",
        selectedRowKeys,
        onChange: (selectedRowKeys, rows) => {
          selectedRowChange(selectedRowKeys, rows);
        },
      }}
    />
  );
};

const MemoTableList = memo(TableList);

export default MemoTableList;
'''

def generate_making_index_file(api_functions: List[str]) -> str:
    """生成表单编辑页主文件"""
    return '''import React, { useState, useRef } from "react";
import { Container, Form, message, TableEdit } from "@/components/common";
import EditForm from "./edit-form";
// 页面缓存相关
import usePageCache from "@/hooks/use-page-cache";
// 底部操作栏相关
import useFooterDom from "@/hooks/use-footer-dom";
import type { IUseFooterDom } from "@/hooks/use-footer-dom";
// 路由相关
import { useParams } from "@/common-utils/route";
// 校验相关
import { getValidErrorMessage } from "@/common-utils/utils";
// 接口相关
import { getDetail, addData, updateData, startProcess } from "../service";
import { RoutesPaths } from "../routes";

// 关闭新增修改页时，跳转到哪个页面
const toPath = RoutesPaths("list");

const Making: React.FC = () => {
  const { id }: any = useParams();
  const [form] = Form.useForm();
  const [table] = TableEdit.useTable();
  const uploadRef = useRef<any>(null);
  const [loading, setLoading] = useState(false);

  const [onCloseHandle] = usePageCache({
    // 因为新增、修改页公用一个组件，所以需要区分是新增还是修改
    key: id ? `功能名-change` : "功能名-add",
    save: () => {
      return {
        id,
        params: form.getFieldsValue(true),
        records: table.getter(),
      };
    },
    init: async (state) => {
      if (id && state?.id !== id) {
        /** 请求详情 */
        setLoading(true);
        const res = await getDetail(id);
        setLoading(false);
        if (res?.data?.success) {
          const params = {
            ...(res?.data?.data || {}),
          };
          form.setFieldsValue(params);
          table.setter(params?.detailList || []);
        }
      } else {
        form.setFieldsValue(state?.params);
        table.setter(state?.records || [{ tableKey: "1" }]);
      }
    },
  });

  const validate = async () => {
    await form.validateFields();
    await table.validate();
    if (uploadRef?.current?.validate) {
      await uploadRef?.current?.validate();
    }
  };

  const onSaveAxios = async () => {
    const params = form.getFieldsValue(true);
    await getValidErrorMessage(validate);
    const transList = transListTable.getter();

    const optionListRaw = optionListTable.getter() || [];
    const optionList = processOptionList(optionListRaw, params.optionPortf);

    const swapList = swapListTable.getter();
    const request = id ? strategyMainUpdate : strategyMainSave;
    setLoading(true);
    return request({ ...params, transList, optionList, swapList });
  };

  const onTemplate = async () => {
    onSaveAxios()
      .then((res) => {
        message.success(res.msg || '操作成功');
        onCloseHandle(toPath);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const onSave = async () => {
    try {
      const res: any = await onSaveAxios();
      const resProcess = await startProcess({
        id: res?.data?.id,
        bizServerAddr: RoutesPaths('detail', false),
        editFormUrl: RoutesPaths('making', false),
        mbFormUrl: RoutesPaths('making', false),
        title: res?.data?.title,
      });
      message.success(resProcess.msg || '操作成功');
    } finally {
      setLoading(false);
    }
  };

  const footer: IUseFooterDom[] = [
    {
      DOMType: "button",
      type: "primary",
      text: "暂存",
      onClick: () => onTemplate(),
    },
    {
      DOMType: "button",
      type: "primary",
      text: "提交",
      onClick: () => onSave(),
    },
    {
      DOMType: "button",
      type: "default",
      text: "关闭",
      onClick: () => onCloseHandle(toPath),
    },
  ];

  const footerDom = useFooterDom(footer, toPath);

  return (
    <Container footerDom={footerDom} loading={loading}>
      <EditForm form={form} table={table} />
    </Container>
  );
};

export default Making;
'''

def generate_making_edit_form_file() -> str:
    """生成表单组件文件"""
    return '''import React from "react";
import { Form } from "@/components/common";
import type { IProFormProps, ITableEditProps } from "@/components/common";
import { useMakingItems } from "../config/form-config";

interface EditFormProps {
  form: IProFormProps["form"];
  table: ITableEditProps<any>["table"];
}

const EditForm: React.FC<EditFormProps> = ({ form, table }) => {
  const items = useMakingItems({ table });
  return <Form form={form} items={items} />;
};

export default EditForm;
'''

def generate_detail_index_file(api_functions: List[str]) -> str:
    """生成详情页主文件"""
    return '''import React, { useState } from "react";
import { Container, Form, HeadLayout } from "@/components/common";
import DetailForm from "./detail-form";
// 页面缓存相关
import usePageCache from "@/hooks/use-page-cache";
// 底部操作栏相关
import useFooterDom from "@/hooks/use-footer-dom";
import type { IUseFooterDom } from "@/hooks/use-footer-dom";
// 路由相关
import { useParams } from "@/common-utils/route";
// 接口相关
import { getDetail } from "../service";
import { RoutesPaths } from "../routes";

// 关闭新增修改页时，跳转到哪个页面
const toPath = RoutesPaths("list");

const Detail: React.FC = () => {
  const { id }: any = useParams();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const params = form?.getFieldsValue(true) || {};

  const [onCloseHandle] = usePageCache({
    init: async () => {
      /** 请求详情 */
      setLoading(true);
      const res = await getDetail({ id });
      setLoading(false);
      const params = res.data;
      form.setFieldsValue(params);
    },
  });

  const footer: IUseFooterDom[] = [
    {
      DOMType: "button",
      type: "default",
      text: "关闭",
      onClick: () => onCloseHandle(toPath),
    },
  ];

  const footerDom = useFooterDom(footer, toPath);

  return (
    <Container footerDom={footerDom} loading={loading}>
      <HeadLayout
        params={{
          title: "详情",
          titleNo: params?.number || "",
          updateTitle: params?.updateUserName || params?.createUserName,
          updateTime: params?.updateTime || params?.createTime,
        }}
      />
      <DetailForm form={form} />
    </Container>
  );
};

export default Detail;
'''

def generate_detail_form_file() -> str:
    """生成详情表单组件文件"""
    return '''import React from "react";
import { Form } from "@/components/common";
import type { IProFormProps } from "@/components/common";
import { useMakingItems } from "../config/form-config";

interface FormProps {
  form: IProFormProps["form"];
}

const DetailForm: React.FC<FormProps> = ({ form }) => {
  const items = useMakingItems({});
  return <Form form={form} items={items} readonly />;
};

export default DetailForm;
'''

# @app.tool()
# def generate_config_from_image(
#     image_data: str,
#     config_type: str,
#     output_dir: str = None,
#     ctx: Context = None
# ) -> Dict[str, Any]:
#     """
#     根据用户上传的图片生成对应的配置文件
    
#     Args:
#         image_data: base64 编码的图片数据
#         config_type: 配置类型 (form, table, chart)
#         output_dir: 输出目录路径
#     """
#     import json
    
#     try:
#         log_info(ctx, f"开始根据图片生成 {config_type} 配置...")
        
#         # 确保输出目录存在
#         ensure_dir_exists(output_dir)
        
#         # 生成配置
#         config_data = generate_mock_config(config_type)
        
#         # 写入配置文件
#         config_file = Path(output_dir) / f"{config_type}-config.json"
#         with open(config_file, 'w', encoding='utf-8') as f:
#             json.dump(config_data, f, indent=2, ensure_ascii=False)
        
#         log_info(ctx, f"配置文件已生成: {config_file}")
            
#         return {
#             "success": True,
#             "file_path": str(config_file),
#             "config_type": config_type,
#             "config": config_data,
#             "message": "配置文件生成成功"
#         }
        
#     except Exception as e:
#         log_error(ctx, f"生成配置文件失败: {str(e)}")
#         return {"success": False, "error": str(e)}

@app.tool()
def verify_typescript_file(file_path: str, ctx: Context = None) -> Dict[str, Any]:
    """
    验证TypeScript类型文件是否已成功生成并返回内容预览
    
    Args:
        file_path: 文件路径
    """
    try:
        log_info(ctx, f"正在验证文件: {file_path}")
        return verify_file(file_path, ctx)
    except Exception as e:
        log_error(ctx, f"验证文件失败: {str(e)}")
        return {"success": False, "error": str(e)}

# 辅助函数
def log_info(ctx, message):
    """统一日志输出"""
    if ctx:
        ctx.info(message)
    else:
        print(message)

def log_error(ctx, message):
    """统一错误日志输出"""
    if ctx:
        ctx.error(message)
    else:
        print(message)

# 资源定义
@app.resource(uri="help://usage", name="使用说明", description="MCP 代码生成器使用指南")
async def get_usage_help():
    return """
# MCP 代码生成器使用指南

## 工具功能

### 1. fetch_swagger_info(swagger_url, [filter_paths])
- 获取 Swagger API 文档信息
- 参数: 
  - swagger_url: 要获取的swagger地址
  - filter_paths - 要过滤的路径列表，只处理这些路径对应的API（可选）
- 返回: API 基本信息和路径列表

### 2. generate_typescript_types(output_dir)
- 根据 Swagger 定义生成 TypeScript 类型
- 如果指定了过滤路径，则只生成相关类型
- 参数: output_dir - 输出当前项目的绝对目录路径，如：/Users/xxx/业务项目
- 生成文件: types.ts

### 3. generate_service_functions(api_prefix,output_dir)
- 生成 TypeScript 服务函数
- 如果指定了过滤路径，则只生成相关服务函数
- 参数:api_prefix - 请求url前缀 output_dir - 输出当前项目的绝对目录路径，如：/Users/xxx/业务项目
- 生成文件: api-service.ts


## 使用流程

1. 首先调用 fetch_swagger_info 获取 API 信息，可选择性过滤指定路径
2. 调用 generate_typescript_types 生成类型定义
3. 调用 generate_service_functions 生成服务函数

## 示例

```
# 1. 只获取特定路径的API信息
fetch_swagger_info("http://172.28.6.86:18000/zmdms-prm-datamanage/v2/api-docs", ["/users", "/products"])

# 2. 生成类型定义（会根据上面的过滤自动处理）
generate_typescript_types("/Users/xxx/业务项目")

# 3. 生成服务函数（会根据上面的过滤自动处理）
generate_service_functions("/api/zmdms-prm-datamanage","/Users/xxx/业务项目")

```
"""

def main():
    app.run(transport="stdio")

if __name__ == "__main__":
    main()