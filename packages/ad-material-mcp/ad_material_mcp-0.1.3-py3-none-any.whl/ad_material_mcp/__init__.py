#!/opt/anaconda3/envs/mcp_env/bin/python
from mcp.server.fastmcp import FastMCP
import requests
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Optional
from enum import IntEnum

# 解析命令行参数
parser = argparse.ArgumentParser(description='广告素材数据查询MCP服务')
parser.add_argument('--token', type=str, required=True, help='API访问token')
args = parser.parse_args()

# 创建MCP服务器
mcp = FastMCP("广告素材数据查询服务")


class AdQualityOption(IntEnum):
    DEFAULT = -1
    HIGH_QUALITY = 1
    LOW_QUALITY = 2


def get_token_from_config():
    # 只从命令行获取token
    if args.token:
        return args.token
    else:
        raise ValueError("必须提供命令行参数--token")


# 从命令行获取token
@mcp.tool()
def get_ad_material_list(
        version: str = "0.1.86",
        appid: str = "59",
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        zhibiao_list: Optional[List[str]] = None,
        media: Optional[List[str]] = None,
        self_cid: Optional[List[str]] = None,
        toushou: Optional[List[str]] = None,
        component_id: Optional[List[str]] = None,
        vp_adgroup_id: Optional[List[str]] = None,
        creative_id: Optional[List[str]] = None,
        group_key: Optional[str] = None,
        producer: Optional[List[str]] = None,
        creative_user: Optional[List[str]] = None,
        vp_originality_id: Optional[List[str]] = None,
        vp_originality_name: Optional[List[str]] = None,
        vp_originality_type: Optional[List[str]] = None,
        is_inefficient_material: AdQualityOption = AdQualityOption.DEFAULT,
        is_ad_low_quality_material: AdQualityOption = AdQualityOption.DEFAULT,
        is_old_table: bool = False,
        is_deep: bool = False
) -> dict:
    """
    # get_order_list工具说明

    在分析广告素材数据前，请先调用 get_ad_material_list 工具来查询相关数据。以下是使用该工具时的参数说明和建议：
基本信息
工具名称: get_ad_material_list
用途: 查询广告素材数据，支持多种筛选条件和指标。
默认行为: 如果用户未指定某些参数，则使用默认值。

参数说明与使用建议
1. 版本号 (version)
类型: str
默认值: "0.1.87"
说明: 表示 API 的版本号，如无特别要求无需更改。
2. 游戏 ID (appid)
类型: str
默认值: "59"
说明: 表示游戏的唯一标识符，如无特别要求无需更改。
3. 时间范围 (start_time, end_time)
类型: Optional[str]
默认值:
start_time: 昨天的日期（格式为 "YYYY-MM-DD"）
end_time: 当前日期（格式为 "YYYY-MM-DD"）
说明:
start_time: 查询的起始时间。
end_time: 查询的结束时间。
如果用户只查询一天的数据，将 start_time 和 end_time 设置为相同的值。
4. 指标列表 (zhibiao_list)
类型: Optional[List[str]]
默认值: 包含所有可用指标的列表，包括：
  ["日期", "素材id", "素材名称", "素材类型", "素材封面uri", "制作人", "创意人", "素材创造时间",
   "3秒播放率", "完播率", "是否低效素材", "是否AD低质素材", "是否AD优质素材", "低质原因",
   "新增注册", "新增创角", "创角率", "点击率", "激活率", "点击成本", "活跃用户", "当日充值",
   "当日付费次数", "当日充值人数", "新增付费人数", "首充付费人数", "新增付费金额", "首充付费金额",
   "新增付费率", "活跃付费率", "活跃arppu", "新增arppu", "小游戏注册首日广告变现金额",
   "小游戏注册首日广告变现ROI", "新增付费成本", "消耗", "付费成本", "注册成本", "创角成本",
   "首日ROI", "累计ROI", "分成后首日ROI", "分成后累计ROI"]
  说明:
如果用户没有明确指定任何指标，则默认使用上述所有指标。
用户可以根据需求选择特定的指标。
5. 其他筛选条件（可选）
这些参数用于进一步过滤查询结果，如果用户未提及，则使用默认值或不传参：
a. 媒体 (media)
类型: Optional[List[str]]
说明: 用于指定媒体来源，支持多个媒体组合查询。
b. 广告账户 ID (self_cid)
类型: Optional[List[str]]
说明: 用于指定特定广告账户。
c. 投手 (toushou)
类型: Optional[List[str]]
说明: 用于指定投放人员。
d. 组件 ID (component_id)
类型: Optional[List[str]]
说明: 用于指定特定组件。
e. 计划 ID (vp_adgroup_id)
类型: Optional[List[str]]
说明: 用于指定特定计划。
f. 创意 ID (creative_id)
类型: Optional[List[str]]
说明: 用于指定特定创意。
g. 分组键 (group_key)
类型: Optional[str]
说明: 用于按特定维度分组。
h. 制作人 (producer)
类型: Optional[List[str]]
说明: 用于指定特定制作人。
i. 创意人 (creative_user)
类型: Optional[List[str]]
说明: 用于指定特定创意人。
j. 素材 ID (vp_originality_id)
类型: Optional[List[str]]
说明: 用于指定特定素材。
k. 素材名称 (vp_originality_name)
类型: Optional[List[str]]
说明: 用于按名称筛选素材。
l. 素材类型 (vp_originality_type)
类型: Optional[List[str]]
说明: 用于按类型筛选素材。
6. 状态与选项参数
a. 是否为低效素材 (is_inefficient_material)
类型: AdQualityOption
取值:
AdQualityOption.DEFAULT (-1): 全选
AdQualityOption.HIGH_QUALITY (1): 是
AdQualityOption.LOW_QUALITY (2): 否
b. AD 优/低质素材 (is_ad_low_quality_material)
类型: AdQualityOption
取值:
AdQualityOption.DEFAULT (-1): 全选
AdQualityOption.HIGH_QUALITY (1): 优质
AdQualityOption.LOW_QUALITY (2): 低质

使用建议
如果用户没有明确指定任何指标，则默认使用 zhibiao_list 中的所有指标。
多个筛选条件可以组合使用，例如：媒体 + 投手、广告 ID + 状态等。
用户如果只查询一天的数据，将 start_time 和 end_time 设置为相同的值。
所有参数如果用户未提及，则使用默认值或不传参。
请根据用户的查询需求灵活设置上述参数，并调用 get_ad_material_list 工具获取所需数据。
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
        zhibiao_list = ["日期", "素材id", "素材名称", "素材类型", "素材封面uri", "制作人", "创意人", "素材创造时间",
                        "3秒播放率", "完播率", "是否低效素材", "是否AD低质素材", "是否AD优质素材", "低质原因",
                        "新增注册", "新增创角", "创角率", "点击率", "激活率", "点击成本", "活跃用户", "当日充值",
                        "当日付费次数", "当日充值人数", "新增付费人数", "首充付费人数", "新增付费金额", "首充付费金额",
                        "新增付费率", "活跃付费率", "活跃arppu", "新增arppu", "小游戏注册首日广告变现金额",
                        "小游戏注册首日广告变现ROI", "新增付费成本", "消耗", "付费成本", "注册成本", "创角成本",
                        "首日ROI", "累计ROI", "分成后首日ROI", "分成后累计ROI"]

    # API接口地址
    url = "https://bi.dartou.com/testapi/ad/GetMaterialCountList"

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
        "self_cid": self_cid,
        "toushou": toushou,
        "component_id": component_id,
        "vp_adgroup_id": vp_adgroup_id,
        "creative_id": creative_id,
        "group_key": group_key,
        "producer": producer,
        "creative_user": creative_user,
        "vp_originality_id": vp_originality_id,
        "vp_originality_name": vp_originality_name,
        "vp_originality_type": vp_originality_type,
        "is_ad_low_quality_material": is_ad_low_quality_material.value,
        "is_inefficient_material": is_inefficient_material.value,
        "is_old_table": is_old_table,
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
