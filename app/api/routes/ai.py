# Please install OpenAI SDK first: `pip3 install openai`
import os
import json
import logging
from openai import OpenAI
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# 配置日志
logger = logging.getLogger(__name__)

load_dotenv()  # 从 .env 文件读取环境变量

router = APIRouter()


def get_openai_client():
    """获取 OpenAI 客户端实例"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, detail="缺少 DEEPSEEK_API_KEY 环境变量"
        )
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


# AI 聊天接口（非流式），调用 DeepSeek 模型生成回复
@router.post("/chat", summary="AI 聊天接口（非流式）")
def chat(userinput: str = Body(embed=True)):
    client = get_openai_client()

    response = client.chat.completions.create(
        model="deepseek-chat",
        temperature=0,
        max_tokens=1024,
        messages=[
            {
                "role": "system",
                "content": "你是一个擅长反驳用户观点的助手。无论用户说什么，你都要试图反驳他。",
            },
            {"role": "user", "content": f"{userinput}"},
        ],
        stream=False,
    )

    ai_response = response.choices[0].message.content
    return ai_response


# AI 聊天接口（流式），实时返回生成的内容
@router.post("/chat_stream", summary="AI 聊天接口（流式）")
def chat_stream(userinput: str = Body(embed=True)):
    client = get_openai_client()

    def generate():
        """生成器函数，逐块返回 AI 响应（累加方式）"""
        response = client.chat.completions.create(
            model="deepseek-chat",
            temperature=0.7,
            max_tokens=1024,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个擅长反驳用户观点的助手。无论用户说什么，你都要试图反驳他。",
                },
                {"role": "user", "content": f"{userinput}"},
            ],
            stream=True,
        )

        # 累加所有已生成的文本
        accumulated_content = ""

        # 遍历流式响应，逐块输出累加的内容
        for chunk in response:
            if chunk.choices[0].delta.content:
                chunk_content = chunk.choices[0].delta.content
                # 打印接收到的每个chunk
                logger.info(f"接收到chunk: {chunk_content}")
                # 累加新的内容
                accumulated_content += chunk_content
                # 返回累加后的完整内容
                yield f"data: {json.dumps({'content': accumulated_content}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# AI 聊天接口（流式），实时返回生成的内容


class DivinationRequest(BaseModel):
    q: str = Field(..., description="用户提出的问题")
    current: str = Field(..., description="当前卦象")
    future: str = Field(..., description="未来卦象")


@router.post("/divination", summary="基于易经起卦结果进行解读")
def divination(request: DivinationRequest):
    client = get_openai_client()

    prompt = f"""<divination>
  <role>你是一个深谙中国易经玄学的人工智能</role>
  <method>三钱法起卦</method>
  <question>{request.q}</question>
  <current_hexagram>{request.current}</current_hexagram>
  <current_hexagram_meaning>current代表用户所问之事的当前状态</current_hexagram_meaning>
  <future_hexagram>{request.future}</future_hexagram>
  <future_hexagram_meaning>future代表用户所问之事的未来发展图景</future_hexagram_meaning>
  <task>请基于易经的原理和哲学思想,结合用户的问题,详细解读这个卦象。注意current卦象反映的是当前状态,future卦象反映的是未来发展趋势。请给出有深度的分析和建议。</task>
  <style>请使用古朴典雅的语言风格,融入易经经典语句和哲学智慧,展现深厚的学识底蕴。语言要庄重而不失温度,专业而易于理解,让用户感受到极高的专业信任度和情绪价值。可适当引用《易经》原文、卦辞、爻辞等经典内容。</style>
</divination>"""

    def generate():
        """生成器函数，逐块返回 AI 响应（累加方式）"""
        response = client.chat.completions.create(
            model="deepseek-chat",
            temperature=0.7,
            max_tokens=1024,
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {"role": "user", "content": "开始吧"},
            ],
            stream=True,
        )

        # 累加所有已生成的文本
        accumulated_content = ""

        # 遍历流式响应，逐块输出累加的内容
        for chunk in response:
            if chunk.choices[0].delta.content:
                chunk_content = chunk.choices[0].delta.content
                # 打印接收到的每个chunk
                logger.info(f"接收到chunk: {chunk_content}")
                # 累加新的内容
                accumulated_content += chunk_content
                # 返回累加后的完整内容
                yield f"data: {json.dumps({'content': accumulated_content}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
