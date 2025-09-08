import json
from llm import client
from prompt import REACT_PROMPT
from tools import get_closing_price,tools
import re

def send_messages(messages):
    response = client.chat.completions.create(
        model="qwen-max",
        messages=messages,
    )
    return response

if __name__ == "__main__":
    instructions = "你是一个股票小助手"

    query = "请比较青岛啤酒和贵州茅台的股票收盘价谁高？"
    
    prompt = REACT_PROMPT.replace("{tools}", json.dumps(tools)).replace("{input}", query)
    messages = [{"role": "user", "content": prompt}]

    while True:
        response = send_messages(messages)
        response_text = response.choices[0].message.content

        print("大模型的回复：")
        print(response_text)

        final_answer_match = re.search(r'Final Answer:\s*(.*)', response_text)
        if final_answer_match:
            final_answer = final_answer_match.group(1)
            print("最终答案:", final_answer)
            break

        messages.append(response.choices[0].message)

        action_match = re.search(r'Action:\s*(\w+)', response_text)
        action_input_match = re.search(r'Action Input:\s*({.*?}|".*?")', response_text, re.DOTALL)

        if action_match and action_input_match:
            tool_name = action_match.group(1)
            params = json.loads(action_input_match.group(1))

            observation = ""
            if tool_name == "get_scoreget_closing_price_by_name":
                observation = get_closing_price(params['name'])
                print("人类的回复：Observation:", observation)         

            messages.append({"role": "user", "content": f"Observation: {observation}"})
