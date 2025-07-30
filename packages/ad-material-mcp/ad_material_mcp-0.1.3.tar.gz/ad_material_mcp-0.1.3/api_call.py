import requests
import json
import os
import re
import time
from datetime import datetime


def extract_mcp_tool_call(response_text):
    """从模型响应中提取MCP工具调用参数"""
    if response_text is None:
        return None

    json_match = re.search(r'<tool_call>\s*(.*?)\s*</tool_call>', response_text, re.DOTALL)
    if json_match:
        try:
            tool_call = json.loads(json_match.group(1))
            # 如果存在arguments字段，则返回其内容
            if "arguments" in tool_call:
                return tool_call["arguments"]
            return tool_call
        except:
            return None
    return None


def extract_thinking_and_response(model_output):
    """从模型输出中提取思考过程和最终回答"""
    if not model_output:
        return "", ""

    # DeepSeek-R1模型特有的<think>标签格式
    think_match = re.search(r'<think>(.*?)</think>', model_output, re.DOTALL)
    if think_match:
        thinking = think_match.group(1).strip()
        # 回答部分是<think>标签后的内容
        response = re.sub(r'<think>.*?</think>', '', model_output, flags=re.DOTALL).strip()
        return thinking, response

    # 如果没有找到<think>标签，则认为整个输出是回答
    return "", model_output


def call_mcpo_get_ad_count_list(params, max_retries=3):
    """调用MCPO get_ad_count_list接口，失败时请求模型修正"""
    # MCPO服务端点
    mcpo_url = "http://127.0.0.1:8001/get_ad_count_list"

    # 参数校验
    if not params:
        raise Exception("参数不能为空")

    # 检查必要参数
    if "version" not in params:
        params["version"] = "0.1.85"  # 仅保留版本号默认值

    # 检查必要的日期参数，不使用默认值
    if "start_time" not in params or not params["start_time"]:
        raise Exception("缺少必要参数 start_time")

    if "end_time" not in params or not params["end_time"]:
        raise Exception("缺少必要参数 end_time")

    # 检查指标列表参数
    if "zhibiao_list" not in params or not params["zhibiao_list"]:
        raise Exception("缺少必要参数 zhibiao_list")

    # 调用接口
    try:
        print(f"调用MCPO get_ad_count_list接口，参数: {json.dumps(params, ensure_ascii=False)}")
        print(f"调用前打印参数测试{params}")
        response = requests.post(mcpo_url, json=params, timeout=30)

        if response.status_code == 200:
            print(f"调用成功，返回结果打印测试: {response.json()}")
            return response.json()
        else:
            error_message = f"MCPO调用失败: 状态码 {response.status_code}, 响应: {response.text}"
            print(error_message)

            # 不再重试相同的调用，而是返回错误信息给上层函数处理
            raise Exception(error_message)

    except requests.exceptions.RequestException as e:
        error_message = f"连接MCPO失败: {e}"
        print(error_message)
        raise Exception(error_message)


def call_api_with_reasoner(prompt, context=None, stream=True):
    """调用deepseek-reasoner模型"""
    api_url = "https://u712009-adb1-31a0235d.cqa1.seetacloud.com:8443/api/chat/completions"
    api_key = "sk-112aabfea1f94e1eac9a995bad114fc6"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    if stream:
        headers["Accept"] = "text/event-stream"

    # 修改系统提示词，去除对思考过程的强制要求
    system_prompt = """您是一个广告投放数据分析专家。"""

    messages = [{"role": "system", "content": system_prompt}]

    # 添加用户的原始问题
    full_prompt = prompt
    if context:
        full_prompt += f"\n\n{context}"

    messages.append({"role": "user", "content": full_prompt})

    # 使用deepseek-reasoner模型
    payload = {
        "model": "deepseek-reasoner",
        "messages": messages,
        "stream": stream
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    mode = "stream" if stream else "regular"
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log", f"{mode}_{timestamp}.txt")
    json_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log", f"{mode}_{timestamp}.json")

    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            stream=stream
        )

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            if stream:
                with open(output_file, "w", encoding="utf-8") as f:
                    print("\n开始流式输出:")
                    full_response = ""
                    chunks = []

                    for line in response.iter_lines():
                        if line:
                            line = line.decode('utf-8')
                            if not line or line == "data: [DONE]":
                                continue

                            if line.startswith('data: '):
                                try:
                                    data = json.loads(line[6:])
                                    chunks.append(data)

                                    if "choices" in data and len(data["choices"]) > 0:
                                        if "delta" in data["choices"][0] and "content" in data["choices"][0]["delta"]:
                                            content = data["choices"][0]["delta"]["content"]
                                            full_response += content
                                            print(content, end="", flush=True)
                                            f.write(content)
                                            f.flush()
                                except:
                                    pass

                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(chunks, f, ensure_ascii=False, indent=2)

                print(f"\n\n流式输出完成")
                print(f"文本响应保存到: {output_file}")
                print(f"JSON响应保存到: {json_file}")

                return full_response
            else:
                result = response.json()

                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                content = ""
                if "choices" in result and len(result["choices"]) > 0:
                    if "message" in result["choices"][0] and "content" in result["choices"][0]["message"]:
                        content = result["choices"][0]["message"]["content"]
                        print("\n模型回复:")
                        print(content)

                        with open(output_file, "w", encoding="utf-8") as f:
                            f.write(content)

                print(f"文本响应保存到: {output_file}")
                print(f"JSON响应保存到: {json_file}")

                return content
        else:
            print(f"错误响应: {response.text}")
            return None

    except Exception as e:
        print(f"请求异常: {e}")
        return None


def save_conversation(user_prompt, initial_output, tool_params, mcpo_result, final_output, output_file,
                      error_message=None, correction_prompt=None, correction_output=None):
    """保存完整对话为JSON格式，包含错误和修复过程"""
    # 从初始输出中分离思考和回答
    initial_thinking, initial_response = extract_thinking_and_response(initial_output)

    # 从最终输出中分离思考和回答
    final_thinking, final_response = extract_thinking_and_response(final_output)

    # 构建对话数组
    conversation_items = [
        {
            "role": "human",
            "content": user_prompt
        },
        {
            "role": "assistant",
            "thinking": initial_thinking,
        }
    ]

    # 如果有错误和修复过程，添加到对话中
    if error_message and correction_output:
        # 添加错误信息
        conversation_items.append({
            "role": "system",
            "content": f"工具调用失败: {error_message}"
        })

        # 添加修复提示
        if correction_prompt:
            conversation_items.append({
                "role": "human",
                "content": correction_prompt
            })

        # 从修复输出中提取思考和回答
        correction_thinking, correction_response = extract_thinking_and_response(correction_output)

        # 添加修复的思考和工具调用
        conversation_items.append({
            "role": "assistant",
            "thinking": correction_thinking,
            "content": correction_response
        })

    # 添加成功的工具调用和响应
    conversation_items.append({
        "role": "assistant",
        "tool_calls": [
            {
                "name": "get_ad_count_list",
                "arguments": tool_params
            }
        ],
        "tool_responses": [
            {
                "name": "get_ad_count_list",
                "content": mcpo_result
            }
        ]
    })

    # 添加最终分析
    conversation_items.extend([
        {
            "role": "assistant",
            "thinking": final_thinking,
        },
        {
            "role": "assistant",
            "content": final_response
        }
    ])

    # 保存完整对话
    conversation = {
        "conversations": conversation_items
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump([conversation], f, ensure_ascii=False, indent=2)

    print(f"完整对话已保存到: {output_file}")


def generate_ad_query():
    """使用大模型生成关于广告投放数据的提问"""
    prompt = """请生成一个关于广告投放数据分析的问题。今天是2025年7月4日。

    直接输出一个简洁的问题，不需要任何解释或前缀。
    """

    response = call_api_with_reasoner(prompt, stream=False)

    # 清理生成的问题（去除可能的引号或多余格式）
    if response:
        query = response.strip(' \n"\'')
        print(f"\n生成的提问: {query}")
        return query
    else:
        print("\n生成提问失败，使用默认提问")
        return "请分析2025年6月28日至7月4日的广点通数据表现"


def main():
    # 使用大模型生成提问
    prompt = generate_ad_query()

    try:
        # 第一次调用获取MCPO工具调用指令
        print("\n使用Reasoner模型获取工具调用指令...")
        initial_output = call_api_with_reasoner(
            f"分析问题：{prompt}。请思考需要查询哪些广告数据，需要使用哪些参数，最后给出工具调用，格式为<tool_call>...</tool_call>。函数名字段用name，参数名字段用arguments，请确保包含start_time和end_time参数，并设置具体的日期值。用<think>...</think>标签来包裹思考过程。")

        if initial_output is None:
            print("初始API调用失败，程序退出")
            return

        # 提取并执行MCPO工具调用
        mcpo_params = extract_mcp_tool_call(initial_output)
        if mcpo_params:
            print("\n检测到MCPO工具调用，正在调用get_ad_count_list...")
            print(f"提取后的参数: {json.dumps(mcpo_params, ensure_ascii=False, indent=2)}")

            # 检查必要参数，但不设置默认值
            missing_params = []
            if "start_time" not in mcpo_params or not mcpo_params["start_time"]:
                missing_params.append("start_time")
            if "end_time" not in mcpo_params or not mcpo_params["end_time"]:
                missing_params.append("end_time")
            if "zhibiao_list" not in mcpo_params or not mcpo_params["zhibiao_list"]:
                missing_params.append("zhibiao_list")

            if missing_params:
                print(f"警告: 参数中缺少必要字段: {', '.join(missing_params)}")

            # 初始化变量
            mcpo_success = False
            mcpo_result = None
            error_message = ""
            correction_context = ""
            correction_output = None

            # 在发生错误时，不是只尝试一次修正，而是可以多次尝试
            for retry in range(3):  # 最多尝试修正3次
                try:
                    mcpo_result = call_mcpo_get_ad_count_list(mcpo_params)
                    mcpo_success = True
                    break  # 成功就退出循环
                except Exception as e:  # 先修正调用格式
                    error_message = str(e)
                    print(f"\nMCPO调用失败 (尝试 {retry + 1}/3): {error_message}")

                    # 将原始参数和错误信息发送给模型修正
                    correction_context = f"""
尝试调用MCPO工具时出现错误:
{error_message}

原始参数是:
{json.dumps(mcpo_params, ensure_ascii=False, indent=2)}

请修正上述参数中的错误，提供完整的正确的<tool_call>...</tool_call>格式。必须包含以下参数:
1. start_time - 开始日期，格式为YYYY-MM-DD
2. end_time - 结束日期，格式为YYYY-MM-DD
3. zhibiao_list - 要查询的指标列表，至少包含["日期", "曝光次数", "点击率", "消耗"]
4. version - API版本号，使用"0.1.85"

请注意:
- 不要使用占位符，必须提供真实的日期值
- group_key应该是字符串而不是数组
- 所有参数类型必须符合API要求
"""
                    # 调用模型获取修正后的参数
                    correction_output = call_api_with_reasoner(prompt, correction_context)
                    mcpo_params = extract_mcp_tool_call(correction_output)
                    print(f"修正后的参数: {json.dumps(mcpo_params, ensure_ascii=False, indent=2)}")

                    if not mcpo_params and retry == 2:  # 最后一次尝试失败
                        print("\n多次修正后仍未能获取有效参数，程序退出")
                        return

            # 如果成功获取MCPO结果，将结果提交给模型进行分析
            if mcpo_success:
                print("\n将MCPO结果提交给模型进行分析...")
                data_context = f"""
以下是通过MCPO工具查询到的广告数据:
```json
{json.dumps(mcpo_result, ensure_ascii=False, indent=2)}
```

请根据这些数据提供详细分析，用<think>...</think>标签来包裹思考过程。
"""
                final_output = call_api_with_reasoner(prompt, data_context)

                # 保存完整对话
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                conversation_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log",
                                                 f"conversation_{timestamp}.json")
                save_conversation(
                    prompt, initial_output,
                    mcpo_params if mcpo_success else mcpo_params,  # Use mcpo_params here as it's the final state
                    mcpo_result, final_output, conversation_file,
                    error_message=error_message if not mcpo_success else None,
                    correction_prompt=correction_context if not mcpo_success else None,
                    correction_output=correction_output if not mcpo_success else None
                )
        else:
            print("\n未检测到MCPO工具调用参数，请检查初始响应内容")
    except Exception as e:
        print(f"\n错误：{e}")
        print("执行失败，请检查MCPO服务是否正常运行，或者确认网络连接正常")


if __name__ == "__main__":
    main()
