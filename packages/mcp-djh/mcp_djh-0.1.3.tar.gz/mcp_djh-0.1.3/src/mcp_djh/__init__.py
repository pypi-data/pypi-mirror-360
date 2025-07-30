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
parser = argparse.ArgumentParser(description='广告数据查询MCP服务')
parser.add_argument('--token', type=str, required=True, help='API访问token')
args = parser.parse_args()

# 创建MCP服务器
mcp = FastMCP("广告数据查询服务")

# 从命令行获取token
def get_token_from_config():
    # 只从命令行获取token
    if args.token:
        return args.token
    else:
        raise ValueError("必须提供命令行参数--token")

@mcp.tool()
def get_ad_count_list(
    version: str = "0.1.85", 
    appid: str = "59",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    zhibiao_list: Optional[List[str]] = None,
    media: Optional[List[str]] = None,
    group_key: Optional[str] = None,
    toushou: Optional[List[str]] = None,
    self_cid: Optional[List[str]] = None,
    ji_hua_id: Optional[List[str]] = None,
    ji_hua_name: Optional[str] = None,
    ad_status: Optional[List[str]] = None,
    creative_id: Optional[List[str]] = None,
    vp_adgroup_id: Optional[List[str]] = None,
    is_deep: Optional[bool] = True,
) -> dict:
    """
    广告数据相关功能，包括查询广告数据、获取指标列表和媒体列表等。
    """
    

    token = get_token_from_config()
    
    # 设置默认值
    if start_time is None:
        # 默认查询昨天的数据
        yesterday = datetime.now() - timedelta(days=1)
        start_time = yesterday.strftime("%Y-%m-%d")
    
    if end_time is None:
        # 默认查询到今天
        end_time = datetime.now().strftime("%Y-%m-%d")
    if zhibiao_list is None:
        zhibiao_list = ["日期", "创角成本", "新增创角", "广告计划名称", "创意名称", "项目名称", "广告状态", "备注", "新增注册", "创角率", "点击率", "激活率", "点击成本", "活跃用户", "曝光次数", "千次展现均价", "点击数", "一阶段花费", "二阶段花费", "当日充值", "当日付费次数", "当日充值人数", "新增付费人数", "首充付费人数", "首充付费次数", "老用户付费人数", "新增付费金额", "首充付费金额", "老用户付费金额", "新增付费率", "活跃付费率", "活跃arppu", "新增arppu", "小游戏注册首日广告变现金额", "小游戏注册首日广告变现ROI", "当月注册用户充值金额", "消耗", "新增付费成本", "付费成本", "注册成本", "首日ROI", "累计ROI", "分成后首日ROI", "分成后累计ROI", "付费首日ROI", "付费累计ROI", "付费分成后首日ROI", "付费分成后累计ROI", "计算累计ROI所用金额", "计算累计ROI所用消耗", "24小时ROI"]

    # API接口地址
    url = "https://bi.dartou.com/testapi/ad/GetAdCountList"
    
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
        "zhibiao_list": zhibiao_list,
        "media": media,
        "group_key": group_key,
        "toushou": toushou,
        "self_cid": self_cid,
        "ji_hua_id": ji_hua_id,
        "ji_hua_name": ji_hua_name,
        "ad_status": ad_status,
        "creative_id": creative_id,
        "vp_adgroup_id": vp_adgroup_id,
        "is_deep": is_deep
    }
    
    
    try:
        # 发送POST请求
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # 解析响应
        result = response.json()
        
        # 检查响应状态
        if result.get("code") == 0:
            print("请求成功!")
            return result
        else:
            print(f"请求失败: {result.get('msg')}")
            return result
    
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return {"code": -1, "msg": str(e)}

def main() -> None:
    mcp.run(transport="stdio")
