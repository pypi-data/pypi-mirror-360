# 헥토파이낸셜 MCP 서버

헥토파이낸셜의 연동 문서를 쉽고 빠르게 검색·조회할 수 있는 MCP(Model Context Protocol) 서버입니다.

## 📋 개요

이 MCP 서버는 헥토파이낸셜의 연동 문서를 검색하고, 개발자들이 필요한 정보를 빠르게 찾을 수 있도록 도와줍니다. 전자결제(PG) 서비스와 내통장결제(간편현금결제) 서비스 관련 문서를 제공합니다.

### 🛠️ 제공 도구
- `list_docs`: 문서 목록 조회
- `get_doc`: 문서 ID로 내용 조회
- `search_docs`: 키워드 기반 검색

## 🖇️ MCP 클라이언트 연동 예시 (Cursor AI)

프로젝트 루트에 `.cursor/mcp.json` 파일을 아래와 같이 생성하세요:

```json
{
  "mcpServers": {
    "hecto-financial": {
      "command": "uvx",
      "args": ["pg-mcp-server-beta@latest"]
    }
  }
}
```

## 📄 License

This project is licensed under the MIT License.