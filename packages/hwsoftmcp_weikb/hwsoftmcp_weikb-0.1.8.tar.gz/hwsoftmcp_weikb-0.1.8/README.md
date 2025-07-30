MCP 配置, env中只能以string方式存在
{
    "mcpServers":{
        "WeiKB": {
            "env": {
                "kbIds": "",
                "fieldIds": "doc-202506040001",
                "knowledge": "背景知识",
                "server_url": "http://192.168.3.23:30012",
                "systemCode": "luzhiliang-001",
                "model": "Qwen3-30B-A3B",
                "replyOrigin": 1
            },
            "args": [
                "hwsoftmcp_weikb@0.1.8"
            ],
            "command": "uvx",
            "description": "华微软件提供的知识库服务，可以通过该服务与华微软件建立的知识库进行交互，检索知识库内容，获得相关信息"
        }
    }
}