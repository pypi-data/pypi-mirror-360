import os
import re
import sys
import copy
import json
import difflib
import platform
from pathlib import Path
from datetime import datetime

class Tee:
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()

    def flush(self):
        for f in self.files:
            f.flush()

from ..aient.src.aient.models import chatgpt
from ..aient.src.aient.plugins import register_tool, get_function_call_list, registry
from ..prompt import worker_system_prompt, instruction_system_prompt
from ..utils import extract_xml_content, get_current_screen_image_message, replace_xml_content, register_mcp_tools
from ..bemcp.bemcp import MCPClient, convert_tool_format, MCPManager

manager = MCPManager()

@register_tool()
async def worker(goal, tools, work_dir, cache_messages=None):
    """
    启动一个 **工作智能体 (Worker Agent)** 来自动完成指定的任务目标 (`goal`)。

    这个工作智能体接收一个清晰的任务描述、一组可供调用的工具 (`tools`)，以及一个工作目录 (`work_dir`)。
    它会利用语言模型的能力，结合可用的工具，自主规划并逐步执行必要的操作，直到最终完成指定的任务目标。
    核心功能是根据输入的目标，驱动整个任务执行流程。

    Args:
        goal (str): 需要完成的具体任务目标描述。工作智能体将围绕此目标进行工作。必须清晰、具体。
        tools (list[str]): 一个包含可用工具函数对象的列表。工作智能体在执行任务时可能会调用这些工具来与环境交互（例如读写文件、执行命令等）。
        work_dir (str): 工作目录的绝对路径。工作智能体将在此目录上下文中执行操作。

    Returns:
        str: 当任务成功完成时，返回字符串 "任务已完成"。
    """
    DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "t", "yes")
    if DEBUG:
        log_file = open(Path(work_dir) / ".beswarm" / "history.log", "a", encoding="utf-8")
        log_file.write(f"========== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==========\n")
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = Tee(original_stdout, log_file)
        sys.stderr = Tee(original_stderr, log_file)

    start_time = datetime.now()
    os.chdir(Path(work_dir).absolute())
    finish_flag = 0
    goal_diff = None

    mcp_list = [item for item in tools if isinstance(item, dict)]
    if mcp_list:
        for mcp_item in mcp_list:
            mcp_name, mcp_config = list(mcp_item.items())[0]
            await manager.add_server(mcp_name, mcp_config)
            client = manager.clients.get(mcp_name)
            await register_mcp_tools(client, registry)
        all_tools = await manager.get_all_tools()
        mcp_tools_name = [tool.name for tool in sum(all_tools.values(), [])]
        tools += mcp_tools_name

    tools = [item for item in tools if not isinstance(item, dict)]

    tools_json = [value for _, value in get_function_call_list(tools).items()]
    work_agent_system_prompt = worker_system_prompt.format(
        os_version=platform.platform(),
        workspace_path=work_dir,
        shell=os.getenv('SHELL', 'Unknown'),
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        tools_list=tools_json
    )

    work_agent_config = {
        "api_key": os.getenv("API_KEY"),
        "api_url": os.getenv("BASE_URL"),
        "engine": os.getenv("MODEL"),
        "system_prompt": work_agent_system_prompt,
        "print_log": True,
        # "max_tokens": 8000,
        "temperature": 0.5,
        "function_call_max_loop": 100,
    }
    if cache_messages:
        if isinstance(cache_messages, bool) and cache_messages == True:
            cache_messages = None
            cache_file_path = Path(work_dir) / ".beswarm" / "work_agent_conversation_history.json"
            if cache_file_path.exists():
                with cache_file_path.open("r", encoding="utf-8") as f:
                    cache_messages = json.load(f)
        if cache_messages and isinstance(cache_messages, list) and len(cache_messages) > 1:
            old_goal = extract_xml_content(cache_messages[1]["content"], "goal")
            if old_goal.strip() != goal.strip():
                diff_generator = difflib.ndiff(old_goal.splitlines(), goal.splitlines())
                changed_lines = []
                for line in diff_generator:
                    if (line.startswith('+ ') or line.startswith('- ')) and line[2:].strip():
                        changed_lines.append(line)
                goal_diff = '\n'.join(changed_lines).strip()
            first_user_message = replace_xml_content(cache_messages[1]["content"], "goal", goal)
            work_agent_config["cache_messages"] = cache_messages[0:1] + [{"role": "user", "content": first_user_message}] + cache_messages[2:]

    instruction_agent_config = {
        "api_key": os.getenv("API_KEY"),
        "api_url": os.getenv("BASE_URL"),
        "engine": os.getenv("MODEL"),
        "system_prompt": instruction_system_prompt.format(os_version=platform.platform(), tools_list=tools_json, workspace_path=work_dir, current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "print_log": DEBUG,
        # "max_tokens": 4000,
        "temperature": 0.7,
        "use_plugins": False,
    }

    # 工作agent初始化
    work_agent = chatgpt(**work_agent_config)
    async def instruction_agent_task():
        last_instruction = None
        while True:
            instruction_prompt = "".join([
                    "</work_agent_conversation_end>\n\n",
                    f"任务目标: {goal}\n\n",
                    f"任务目标新变化：\n{goal_diff}\n\n" if goal_diff else "",
                    "在 tag <work_agent_conversation_start>...</work_agent_conversation_end> 之前的对话历史都是工作智能体的对话历史。\n\n",
                    "根据以上对话历史和目标，请生成下一步指令。如果任务已完成，请回复'任务已完成'。\n\n",
                ])
            if last_instruction:
                instruction_prompt = (
                    f"{instruction_prompt}\n\n"
                    "你生成的指令格式错误，必须把给assistant的指令放在<instructions>...</instructions>标签内。请重新生成格式正确的指令。"
                    f"这是你上次给assistant的错误格式的指令：\n{last_instruction}"
                )
            # 让指令agent分析对话历史并生成新指令
            instruction_agent = chatgpt(**instruction_agent_config)
            conversation_history = copy.deepcopy(work_agent.conversation["default"])

            cache_dir = os.path.join(work_dir, ".beswarm")
            os.makedirs(cache_dir, exist_ok=True)
            cache_file = os.path.join(cache_dir, "work_agent_conversation_history.json")
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(conversation_history, ensure_ascii=False, indent=4))

            work_agent_system_prompt = conversation_history.pop(0)
            if conversation_history:
                # 获取原始内容
                original_content = work_agent_system_prompt["content"]

                # 定义正则表达式
                regex = r"<latest_file_content>(.*?)</latest_file_content>"

                # 进行匹配
                match = re.search(regex, original_content, re.DOTALL)

                # 提取内容或设置为空字符串
                if match:
                    extracted_content = f"<latest_file_content>{match.group(1)}</latest_file_content>\n\n"
                else:
                    extracted_content = ""
                if isinstance(conversation_history[0]["content"], str):
                    conversation_history[0]["content"] = extracted_content + conversation_history[0]["content"]
                elif isinstance(conversation_history[0]["content"], list) and extracted_content:
                    conversation_history[0]["content"].append({"type": "text", "text": extracted_content})

            instruction_agent.conversation["default"][1:] = conversation_history
            if "find_and_click_element" in str(tools_json):
                instruction_prompt = await get_current_screen_image_message(instruction_prompt)
            next_instruction = await instruction_agent.ask_async(instruction_prompt)
            print("\n🤖 指令智能体生成的下一步指令:", next_instruction)
            if "fetch_gpt_response_stream HTTP Error', 'status_code': 404" in next_instruction:
                raise Exception(f"Model: {instruction_agent_config['engine']} not found!")
            if "'status_code': 413" in next_instruction:
                end_time = datetime.now()
                total_time = end_time - start_time
                print(f"\n任务开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"任务结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"总用时: {total_time}")
                raise Exception(f"The request body is too long, please try again.")
            if "任务已完成" == next_instruction.strip():
                break
            last_instruction = next_instruction
            next_instruction = extract_xml_content(next_instruction, "instructions")
            if not next_instruction:
                print("\n❌ 指令智能体生成的指令不符合要求，请重新生成。")
                continue
            else:
                if conversation_history == []:
                    next_instruction = (
                        "任务描述：\n"
                        f"<goal>{goal}</goal>\n\n"
                        "你作为指令的**执行者**，而非任务的**规划师**，你必须严格遵循以下单步工作流程：\n"
                        "**执行指令**\n"
                        "   - **严格遵从：** 只执行我当前下达的明确指令。在我明确给出下一步指令前，绝不擅自行动或推测、执行任何未明确要求的后续步骤。\n"
                        "   - **严禁越权：** 禁止执行任何我未指定的步骤。`<goal>` 标签中的内容仅为背景信息，不得据此进行任务规划或推测。\n"
                        "**汇报结果**\n"
                        "   - **聚焦单步：** 指令完成后，仅汇报该步骤的执行结果与产出。\n"
                        "**暂停等待**\n"
                        "   - **原地待命：** 汇报后，任务暂停。在收到我新的指令前，严禁发起任何新的工具调用或操作。\n"
                        "   - **请求指令：** 回复的最后必须明确请求我提供下一步指令。\n"
                        "**注意：** 禁止完成超出下面我未规定的步骤，`<goal>` 标签中的内容仅为背景信息。"
                        "现在开始执行第一步：\n"
                        f"{next_instruction}"
                    )
                break
        return next_instruction

    need_instruction = True
    while True:
        next_instruction = ''
        if need_instruction:
            next_instruction = await instruction_agent_task()

            # 检查任务是否完成
            if "任务已完成" in next_instruction and len(next_instruction) < 10:
                if finish_flag == 0:
                    finish_flag = 1
                    continue
                elif finish_flag == 1:
                    print("\n✅ 任务已完成！")
                    break
            else:
                finish_flag = 0
        if "find_and_click_element" in str(tools_json):
            next_instruction = await get_current_screen_image_message(next_instruction)
        result = await work_agent.ask_async(next_instruction)
        if result.strip() == '' or result.strip() == '</content>\n</write_to_file>':
            print("\n❌ 工作智能体回复为空，请重新生成指令。")
            need_instruction = False
            continue
        print("✅ 工作智能体回复:", result)
        need_instruction = True

    end_time = datetime.now()
    total_time = end_time - start_time
    print(f"\n任务开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"任务结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总用时: {total_time}")
    await manager.cleanup()
    return "任务已完成"

async def worker_gen(goal, tools, work_dir, cache_messages=None):
    DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "t", "yes")
    if DEBUG:
        log_file = open(Path(work_dir) / ".beswarm" / "history.log", "a", encoding="utf-8")
        log_file.write(f"========== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==========\n")
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = Tee(original_stdout, log_file)
        sys.stderr = Tee(original_stderr, log_file)

    start_time = datetime.now()
    os.chdir(Path(work_dir).absolute())
    finish_flag = 0
    goal_diff = None

    mcp_list = [item for item in tools if isinstance(item, dict)]
    if mcp_list:
        for mcp_item in mcp_list:
            mcp_name, mcp_config = list(mcp_item.items())[0]
            await manager.add_server(mcp_name, mcp_config)
            client = manager.clients.get(mcp_name)
            await register_mcp_tools(client, registry)
        all_tools = await manager.get_all_tools()
        mcp_tools_name = [tool.name for tool in sum(all_tools.values(), [])]
        tools += mcp_tools_name

    tools = [item for item in tools if not isinstance(item, dict)]

    tools_json = [value for _, value in get_function_call_list(tools).items()]
    work_agent_system_prompt = worker_system_prompt.format(
        os_version=platform.platform(),
        workspace_path=work_dir,
        shell=os.getenv('SHELL', 'Unknown'),
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        tools_list=tools_json
    )

    work_agent_config = {
        "api_key": os.getenv("API_KEY"),
        "api_url": os.getenv("BASE_URL"),
        "engine": os.getenv("MODEL"),
        "system_prompt": work_agent_system_prompt,
        "print_log": True,
        # "max_tokens": 8000,
        "temperature": 0.5,
        "function_call_max_loop": 100,
    }
    if cache_messages:
        if isinstance(cache_messages, bool) and cache_messages == True:
            cache_messages = None
            cache_file_path = Path(work_dir) / ".beswarm" / "work_agent_conversation_history.json"
            if cache_file_path.exists():
                with cache_file_path.open("r", encoding="utf-8") as f:
                    cache_messages = json.load(f)
        if cache_messages and isinstance(cache_messages, list) and len(cache_messages) > 1:
            old_goal = extract_xml_content(cache_messages[1]["content"], "goal")
            if old_goal.strip() != goal.strip():
                diff_generator = difflib.ndiff(old_goal.splitlines(), goal.splitlines())
                changed_lines = []
                for line in diff_generator:
                    if (line.startswith('+ ') or line.startswith('- ')) and line[2:].strip():
                        changed_lines.append(line)
                goal_diff = '\n'.join(changed_lines).strip()
            first_user_message = replace_xml_content(cache_messages[1]["content"], "goal", goal)
            work_agent_config["cache_messages"] = cache_messages[0:1] + [{"role": "user", "content": first_user_message}] + cache_messages[2:]

    instruction_agent_config = {
        "api_key": os.getenv("API_KEY"),
        "api_url": os.getenv("BASE_URL"),
        "engine": os.getenv("MODEL"),
        "system_prompt": instruction_system_prompt.format(os_version=platform.platform(), tools_list=tools_json, workspace_path=work_dir, current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "print_log": DEBUG,
        # "max_tokens": 4000,
        "temperature": 0.7,
        "use_plugins": False,
    }

    # 工作agent初始化
    work_agent = chatgpt(**work_agent_config)
    async def instruction_agent_task():
        last_instruction = None
        while True:
            instruction_prompt = "".join([
                    "</work_agent_conversation_end>\n\n",
                    f"任务目标: {goal}\n\n",
                    f"任务目标新变化：\n{goal_diff}\n\n" if goal_diff else "",
                    "在 tag <work_agent_conversation_start>...</work_agent_conversation_end> 之前的对话历史都是工作智能体的对话历史。\n\n",
                    "根据以上对话历史和目标，请生成下一步指令。如果任务已完成，请回复'任务已完成'。\n\n",
                ])
            if last_instruction:
                instruction_prompt = (
                    f"{instruction_prompt}\n\n"
                    "你生成的指令格式错误，必须把给assistant的指令放在<instructions>...</instructions>标签内。请重新生成格式正确的指令。"
                    f"这是你上次给assistant的错误格式的指令：\n{last_instruction}"
                )
            # 让指令agent分析对话历史并生成新指令
            instruction_agent = chatgpt(**instruction_agent_config)
            conversation_history = copy.deepcopy(work_agent.conversation["default"])

            cache_dir = os.path.join(work_dir, ".beswarm")
            os.makedirs(cache_dir, exist_ok=True)
            cache_file = os.path.join(cache_dir, "work_agent_conversation_history.json")
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(conversation_history, ensure_ascii=False, indent=4))

            work_agent_system_prompt = conversation_history.pop(0)
            if conversation_history:
                # 获取原始内容
                original_content = work_agent_system_prompt["content"]

                # 定义正则表达式
                regex = r"<latest_file_content>(.*?)</latest_file_content>"

                # 进行匹配
                match = re.search(regex, original_content, re.DOTALL)

                # 提取内容或设置为空字符串
                if match:
                    extracted_content = f"<latest_file_content>{match.group(1)}</latest_file_content>\n\n"
                else:
                    extracted_content = ""
                if isinstance(conversation_history[0]["content"], str):
                    conversation_history[0]["content"] = extracted_content + conversation_history[0]["content"]
                elif isinstance(conversation_history[0]["content"], list) and extracted_content:
                    conversation_history[0]["content"].append({"type": "text", "text": extracted_content})

            instruction_agent.conversation["default"][1:] = conversation_history
            if "find_and_click_element" in str(tools_json):
                instruction_prompt = await get_current_screen_image_message(instruction_prompt)
            next_instruction = await instruction_agent.ask_async(instruction_prompt)
            print("\n🤖 指令智能体生成的下一步指令:", next_instruction)
            if "fetch_gpt_response_stream HTTP Error', 'status_code': 404" in next_instruction:
                raise Exception(f"Model: {instruction_agent_config['engine']} not found!")
            if "'status_code': 413" in next_instruction:
                end_time = datetime.now()
                total_time = end_time - start_time
                print(f"\n任务开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"任务结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"总用时: {total_time}")
                raise Exception(f"The request body is too long, please try again.")
            if "任务已完成" == next_instruction.strip():
                break
            last_instruction = next_instruction
            next_instruction = extract_xml_content(next_instruction, "instructions")
            if not next_instruction:
                print("\n❌ 指令智能体生成的指令不符合要求，请重新生成。")
                continue
            else:
                if conversation_history == []:
                    next_instruction = (
                        "任务描述：\n"
                        f"<goal>{goal}</goal>\n\n"
                        "你作为指令的**执行者**，而非任务的**规划师**，你必须严格遵循以下单步工作流程：\n"
                        "**执行指令**\n"
                        "   - **严格遵从：** 只执行我当前下达的明确指令。在我明确给出下一步指令前，绝不擅自行动或推测、执行任何未明确要求的后续步骤。\n"
                        "   - **严禁越权：** 禁止执行任何我未指定的步骤。`<goal>` 标签中的内容仅为背景信息，不得据此进行任务规划或推测。\n"
                        "**汇报结果**\n"
                        "   - **聚焦单步：** 指令完成后，仅汇报该步骤的执行结果与产出。\n"
                        "**暂停等待**\n"
                        "   - **原地待命：** 汇报后，任务暂停。在收到我新的指令前，严禁发起任何新的工具调用或操作。\n"
                        "   - **请求指令：** 回复的最后必须明确请求我提供下一步指令。\n"
                        "**注意：** 禁止完成超出下面我未规定的步骤，`<goal>` 标签中的内容仅为背景信息。"
                        "现在开始执行第一步：\n"
                        f"{next_instruction}"
                    )
                break
        return next_instruction

    need_instruction = True
    while True:
        next_instruction = ''
        if need_instruction:
            next_instruction = await instruction_agent_task()

            yield {"user": next_instruction}

            # 检查任务是否完成
            if "任务已完成" in next_instruction and len(next_instruction) < 10:
                if finish_flag == 0:
                    finish_flag = 1
                    continue
                elif finish_flag == 1:
                    print("\n✅ 任务已完成！")
                    break
            else:
                finish_flag = 0
        if "find_and_click_element" in str(tools_json):
            next_instruction = await get_current_screen_image_message(next_instruction)
        result = await work_agent.ask_async(next_instruction)
        if result.strip() == '' or result.strip() == '</content>\n</write_to_file>':
            print("\n❌ 工作智能体回复为空，请重新生成指令。")
            need_instruction = False
            continue
        yield {"assistant": result}
        print("✅ 工作智能体回复:", result)
        need_instruction = True

    end_time = datetime.now()
    total_time = end_time - start_time
    print(f"\n任务开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"任务结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总用时: {total_time}")
    await manager.cleanup()