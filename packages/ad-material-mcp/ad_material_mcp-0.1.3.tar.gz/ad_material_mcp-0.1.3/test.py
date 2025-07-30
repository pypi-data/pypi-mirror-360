import re
import json


def extract_mcp_tool_call(response_text):
    if response_text is None:
        return None

    json_match = re.search(r'<tool_call>\s*(.*?)\s*</tool_call>', response_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except:
            return None
    return None


if __name__ == "__main__":
    response_text = """
<think>
用户要求分析2025年7月1日至7月3日广点通（gdt）和头条（tt）渠道的数据，对比ROI、转化率及创角成本等核心指标。以下是关键分析思路：

1. **时间参数**：日期范围固定为2025-07-01至2025-07-03
2. **媒体渠道**：需指定媒体代码["gdt", "tt"]
3. **核心指标选择**：
   - 必须包含基础指标：日期、广告计划名称（用于识别最佳计划）
   - ROI相关：首日ROI（短期效果）、累计ROI（长期价值）
   - 转化率相关：点击率（曝光→点击）、创角率（注册→创角）
   - 成本相关：创角成本、注册成本
   - 补充指标：消耗、新增注册、新增创角（用于计算衍生指标）
4. **分组逻辑**：按广告计划名称（vp_campaign_id）分组，便于对比不同计划表现
5. **特殊处理**：
   - 用户未指定投手/广告状态，使用默认全量数据
   - 指标未全量指定，但需包含ROI/转化率/成本核心三组指标
   - 媒体名称使用代码["gdt","tt"]而非中文

最终指标列表（共14项）：
["日期","广告计划名称","消耗","新增注册","新增创角","点击率","创角率","创角成本","注册成本","首日ROI","累计ROI","曝光次数","点击数","小游戏注册首日广告变现金额"]
</think>

<tool_call>
{
  "name": "get_ad_count_list",
  "arguments": {
    "version": "0.1.85",
    "start_time": "2025-07-01",
    "end_time": "2025-07-03",
    "zhibiao_list": ["日期","广告计划名称","消耗","新增注册","新增创角","点击率","创角率","创角成本","注册成本","首日ROI","累计ROI","曝光次数","点击数","小游戏注册首日广告变现金额"],
    "media_list": ["gdt","tt"],
    "group_key": ["vp_campaign_id"]
  }
}
</tool_call>
    """
    print(extract_mcp_tool_call(response_text))
