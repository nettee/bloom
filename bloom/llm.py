import os
from typing import List, Dict, Optional, Any, Generator
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk


class LLMClient:
    """
    大模型调用客户端，基于 OpenAI SDK 封装 Cloudflare AI Gateway 调用
    """
    
    def __init__(self):
        self.api_key = self._get_api_key()
        self.base_url = "https://gateway.ai.cloudflare.com/v1/d86fcdf114d9c154ee61f5b601d8cae3/my-agent/compat"
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
    
    def _get_api_key(self) -> str:
        """从环境变量获取API密钥"""
        api_key = os.getenv("GOOGLE_AI_STUDIO_API_KEY")
        if not api_key:
            raise ValueError("环境变量 GOOGLE_AI_STUDIO_API_KEY 未设置")
        return api_key
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "google-ai-studio/gemini-2.5-flash",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> ChatCompletion:
        """
        调用大模型进行对话完成
        
        Args:
            messages: 对话消息列表，格式为 [{"role": "user|assistant|system", "content": "消息内容"}]
            model: 模型名称，默认为 gemini-2.5-flash
            temperature: 温度参数，控制回复的随机性，0-1之间
            max_tokens: 最大token数量
            stream: 是否使用流式输出
            **kwargs: 其他可选参数
            
        Returns:
            ChatCompletion: OpenAI 格式的响应对象
            
        Raises:
            Exception: API调用异常
        """
        try:
            # 构建参数字典
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream,
                **kwargs
            }
            
            if max_tokens is not None:
                params["max_tokens"] = max_tokens
            
            response = self.client.chat.completions.create(**params)
            return response
            
        except Exception as e:
            raise Exception(f"LLM API调用失败: {str(e)}")
    
    def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "google-ai-studio/gemini-2.5-flash",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Generator[ChatCompletionChunk, None, None]:
        """
        流式调用大模型进行对话完成
        
        Args:
            messages: 对话消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数量
            **kwargs: 其他可选参数
            
        Yields:
            ChatCompletionChunk: 流式响应片段
        """
        try:
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": True,
                **kwargs
            }
            
            if max_tokens is not None:
                params["max_tokens"] = max_tokens
            
            stream = self.client.chat.completions.create(**params)
            for chunk in stream:
                yield chunk
                
        except Exception as e:
            raise Exception(f"LLM 流式API调用失败: {str(e)}")
    
    def chat_simple(
        self,
        user_message: str,
        system_message: Optional[str] = None,
        model: str = "google-ai-studio/gemini-2.5-flash",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        简单的单轮对话接口，只支持非流式输出
        
        Args:
            user_message: 用户消息
            system_message: 系统消息（可选）
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数量
            **kwargs: 其他参数
            
        Returns:
            str: 助手的回复文本
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": user_message})
        
        # 强制非流式调用
        response = self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
            **kwargs
        )
        
        # 提取回复文本
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content or ""
        else:
            raise ValueError("API响应格式异常，未找到回复内容")
    



def create_llm_client() -> LLMClient:
    """创建LLM客户端实例"""
    return LLMClient()


if __name__ == "__main__":
    # 测试代码
    try:
        # 创建客户端
        client = create_llm_client()
        
        # 测试简单对话（chat_simple）
        print("=== 测试简单对话（chat_simple）===")
        response = client.chat_simple("你是谁？")
        print(f"回复: {response}")
        
        # 测试带系统消息的简单对话
        print("\n=== 测试带系统消息的简单对话 ===")
        system_msg = "你是一个专业的Python编程助手，请简洁地回答问题。"
        response = client.chat_simple("什么是列表推导式？", system_message=system_msg)
        print(f"回复: {response}")
        
        # 测试多轮对话（chat_completion）
        print("\n=== 测试多轮对话（chat_completion）===")
        messages = [
            {"role": "system", "content": "你是一个友好的助手"},
            {"role": "user", "content": "请用一句话介绍一下Python"},
            {"role": "assistant", "content": "Python是一种简洁、易学且功能强大的编程语言。"},
            {"role": "user", "content": "它主要用在哪些领域？"}
        ]
        
        full_response = client.chat_completion(messages)
        print(f"模型: {full_response.model}")
        print(f"回复: {full_response.choices[0].message.content}")
        print(f"Token使用: {full_response.usage}")
        
        # 测试流式输出（chat_completion_stream）
        print("\n=== 测试流式输出（chat_completion_stream）===")
        messages = [
            {"role": "user", "content": "请说一个编程笑话"}
        ]
        
        print("流式回复: ", end="", flush=True)
        for chunk in client.chat_completion_stream(messages):
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta.content:
                    print(delta.content, end="", flush=True)
        print()  # 换行
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        print("请确保已正确设置环境变量 GOOGLE_AI_STUDIO_API_KEY")
        print("并且安装了 openai 库: pip install openai")