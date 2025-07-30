#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mcp.server.fastmcp import FastMCP
import requests
import json
import os
import argparse
from datetime import datetime, timedelta
from typing import List, Optional

# 解析命令行参数
parser = argparse.ArgumentParser(description='广告数据下探查询MCP服务')
parser.add_argument('--token', type=str, required=True, help='API访问token')
args = parser.parse_args()

# 创建MCP服务器
mcp = FastMCP("广告数据下探查询服务")

# 从命令行获取token
def get_token_from_config():
    # 只从命令行获取token
    if args.token:
        return args.token
    else:
        raise ValueError("必须提供命令行参数--token")

@mcp.tool()
def get_order_list(
    appid: str = "59",
    start_time: str = None,
    end_time: str = None,
    dt_part_time_col: str = "toYYYYMMDD(dt_part_date)",
    isDistinct: bool = False,
    is_new_ver: bool = True,
    page: int = 1,
    ui: str = None,
    limit: int = 20,
    type: int = 1,
    openID: Optional[str] = None,
    orderByCol: Optional[str] = None,
    orderByType: Optional[str] = None,
    version: str = "0.1.77"
) -> dict:
    """
    广告数据下探功能，根据指标ID获取详细订单列表数据。
    """
    
    token = get_token_from_config()
    
    # 设置默认值
    if start_time is None:
        # 默认查询昨天的数据
        yesterday = datetime.now() - timedelta(days=1)
        start_time = yesterday.strftime("%Y%m%d")
    
    if end_time is None:
        # 默认查询到今天
        end_time = datetime.now().strftime("%Y%m%d")
    
    if ui is None:
        raise ValueError("必须提供下探行唯一ID (ui)")

    # API接口地址
    url = "https://bi.dartou.com/testapi/ad/GetOrderList"
    
    # 设置请求头
    headers = {
        "X-Token": token,
        "X-Ver": version,
        "Content-Type": "application/json"
    }
    
    # 构建请求体
    payload = {
        "appid": appid,
        "start_time": start_time,
        "end_time": end_time,
        "dt_part_time_col": dt_part_time_col,
        "isDistinct": isDistinct,
        "is_new_ver": is_new_ver,
        "page": page,
        "ui": ui,
        "limit": limit,
        "type": type
    }
    
    # 添加可选参数
    if openID is not None and openID != "":
        payload["openID"] = openID
    
    if orderByCol is not None and orderByCol != "":
        payload["orderByCol"] = orderByCol
    
    if orderByType is not None and orderByType != "":
        payload["orderByType"] = orderByType
    
    try:
        # 发送POST请求
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # 解析响应
        result = response.json()
        
        # 检查响应状态
        if result.get("code") == 0:
            print("数据下探请求成功!")
            return result
        else:
            print(f"数据下探请求失败: {result.get('msg')}")
            return result
    
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return {"code": -1, "msg": str(e)}

def main() -> None:
    mcp.run(transport="stdio") 
