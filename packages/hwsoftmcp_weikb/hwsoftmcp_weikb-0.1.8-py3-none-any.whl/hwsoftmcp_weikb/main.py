
import httpx
from mcp.server.fastmcp import FastMCP
import os
import uuid
import json
mcp = FastMCP("Demo")

host = os.getenv("server_url")

# @mcp.tool()
# async def chat_knowledge_base(question: str) -> str:
#     """输入问题，由知识库进行回答

#     Args:
#         question: 检索内容

#     Returns:
#         str: 检索结果
#     """
#     url = f"{host}/api/v1/chat/completions"
    
#     stream = False
    
#     appType = "knowledge"
#     chatId = str(uuid.uuid4())
#     # env 参数
#     systemCode = os.getenv("systemCode")
#     kbIds = os.getenv("kbIds")
#     if kbIds is not None:
#         if kbIds == "":
#             kbIds = None
#         else:
#             kbIds = kbIds.split(",")
#     fieldIds = os.getenv("fieldIds")
#     if fieldIds is not None:
#         if fieldIds == "":
#             fieldIds = None
#         else:
#             fieldIds = fieldIds.split(",")
#     knowledge = os.getenv("knowledge")
#     model = os.getenv("model","Qwen3-30B-A3B")
#     replyOrigin = os.getenv("replyOrigin",1)
   
#     data = {
#         "question": question,
#         "knowledge": knowledge,
#         "stream": stream,
#         "model": model,
#         "appType": appType,
#         "chatId": chatId,
#         "systemCode": systemCode,
#         "kbIds": kbIds,
#         "fieldIds": fieldIds,
#         "replyOrigin": replyOrigin
#     }
#     async with httpx.AsyncClient(timeout=120) as client:
#         response = await client.post(url, json=data)
#         # 解析结果
#         try:
#             result = response.json()
#             content = result["choices"][0]["message"]["content"]
#             return content
#         except Exception as e:
#             return response.text


@mcp.tool()
async def search_knowledge_base(question: str) -> str:
    """输入关键词，查询知识库进行检索，返回检索结果

    Args:
        question: 检索关键词

    Returns:
        str: 检索结果
    """
    if host is None:
        return "请在MCP环境变量中指定server_url"

    url = f"{host}/api/v1/chat/queryKnowledge"
    
    # env 参数
    params = os.getenv("params")
    try:
        params = json.loads(params)
    except Exception as e:
        return "解析参数列表失败"

    systemCode = params.get("systemCode")
    kbIds = params.get("kbIds")
    if kbIds is not None:
        if kbIds == "":
            kbIds = None
        else:
            kbIds = kbIds.split(",")
    fieldIds = params.get("fieldIds")
    if fieldIds is not None:
        if fieldIds == "":
            fieldIds = None
        else:
            fieldIds = fieldIds.split(",")
    knowledge = params.get("knowledge")
    departmentPaths = params.get("departmentPaths")
    minScore = params.get("minScore",0.6)
    size = params.get("size",10)
    rerank = params.get("rerank",True)
    useLLMExtractMeta = params.get("useLLMExtractMeta",True)
    searchType = params.get("searchType","hybrid")    #vector": 向量检索- "text": 全文检索- "hybrid": 混合检索（默认）
    # 用户、部门、角色用于权限过滤
    userId = params.get("userId",None)
    roleIds = params.get("roleIds",None)
    departmentPaths = params.get("departmentPaths",None)

    data = {
        "question": question,
        "systemCode": systemCode,
        "kbIds": kbIds,
        "fileIds": fieldIds,
        "includeFeatures": False,
        "searchType": searchType, 
        "size": size,
        "minScore": minScore,
        "rerank": rerank,
        "useLLMExtractMeta": useLLMExtractMeta,
        "backgroundKnowledge": knowledge,
        "userId": userId,
        "departmentPaths": departmentPaths,
        "roleIds": roleIds
    }
    print("search_knowledge_base",json.dumps(data,ensure_ascii=False))

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json=data)
        return response.text


def main():
    """Entry point for the MCP Ops Toolkit"""
    mcp.run(transport='stdio')

if __name__ == "__main__":
   import asyncio   
   import os
   os.environ["server_url"] = "http://192.168.3.44:30012"
   host = os.getenv("server_url")

   os.environ["params"] = "{\"kbIds\": \"595474560116064256\",\"knowledge\": \"背景知识\",\"systemCode\": \"wei_bots_knowledge_meta-1\"}"
   os.environ["model"] = "Qwen3-30B-A3B"
   ret = asyncio.run(search_knowledge_base("2025年李静董事长发言"))
   print(ret)