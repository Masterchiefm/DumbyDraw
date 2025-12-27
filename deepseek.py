import time

API_key = ""
from openai import OpenAI  # 假设使用OpenAI格式的SDK


class DeepSeek:
    def __init__(self, base_url="", API_key='', prompt='', model="deepseek-ai/DeepSeek-V3"):
        if base_url == "":
            self.base_url = "https://api.siliconflow.cn/v1/"
        else:
            self.base_url = base_url

        # 修正这里的变量名一致性问题
        if API_key == "":
            self.API_key = ""
        else:
            self.API_key = API_key  # 这里改为一致的变量名

        self.client = OpenAI(
            api_key=self.API_key,
            base_url=self.base_url)  # 假设的API地址
        self.prompt = prompt
        self.model = model

    def get_response(self, query, temperature=0, prompt='', model="deepseek-ai/DeepSeek-V3", return_type="string"):
        """
        Args: 。
            query: Str
            prompt: Str
            model: Str, include deepseek-ai/DeepSeek-V3 and deepseek-ai/DeepSeek-R1
            return_type: "string" or "list", 返回字符串还是列表
        Returns:
            response: str 或 list
        """
        system_prompt = prompt
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            stream=True,  # 启用流式传输
            temperature=temperature,
        )

        full_response = []
        print("Thinking:")
        reason_complete = False
        current_line = ""  # 用于缓存当前行的内容

        def flush_line(line):
            """输出并清空当前行"""
            if line:
                print(line, flush=True)
            return ""

        for chunk in response:
            chunk_content = chunk.choices[0].delta.content
            chunk_reasoning_content = chunk.choices[0].delta.reasoning_content

            if chunk_reasoning_content:  # 过滤空内容
                # 处理reasoning内容，按行输出
                for char in chunk_reasoning_content:
                    if char == '\n':
                        current_line = flush_line(current_line)
                    else:
                        current_line += char
                full_response.append(chunk_reasoning_content)

            if chunk_content:  # 过滤空内容
                if not reason_complete:
                    current_line = flush_line(current_line)  # 确保之前的行被输出
                    print("\nEnd of thinking\n\nOutput:\n")
                    reason_complete = True
                # 处理普通内容，按行输出
                for char in chunk_content:
                    if char == '\n':
                        current_line = flush_line(current_line)
                    else:
                        current_line += char
                full_response.append(chunk_content)

        # 输出最后一行（如果有）
        flush_line(current_line)

        # 根据 return_type 返回不同类型
        if return_type == "string":
            return ''.join(full_response)
        else:
            return full_response

    def check_connection(self):
        t0 = time.ctime()
        response = self.get_response("你是谁")
        # 这里需要处理 response
        return response