import time
from typing import Any
import webbrowser
import httpx
from mcp.server.fastmcp import FastMCP
import re
import lark_oapi as lark
from lark_oapi.api.docx.v1 import *
from lark_oapi.api.auth.v3 import *
from lark_oapi.api.wiki.v2 import *
import json
import os
import asyncio  # Add to imports at the beginning
from lark_oapi.api.search.v2 import *
from aiohttp import web
import secrets
from urllib.parse import quote

# Get configuration from environment variables
# Add global variables below imports
LARK_APP_ID = os.getenv("LARK_APP_ID", "")
LARK_APP_SECRET = os.getenv("LARK_APP_SECRET", "")
OAUTH_HOST = os.getenv("OAUTH_HOST", "localhost")  # 添加 OAuth 主机配置
OAUTH_PORT = int(os.getenv("OAUTH_PORT", "19997"))  # 添加 OAuth 端口配置
REDIRECT_URI = f"http://{OAUTH_HOST}:{OAUTH_PORT}/oauth/callback"
USER_ACCESS_TOKEN = None  # Add global variable
REFRESH_TOKEN = None  # 添加刷新令牌存储
TOKEN_EXPIRES_AT = None  # 添加过期时间存储
REFRESH_TOKEN_EXPIRES_AT = None  # 添加刷新令牌过期时间存储
FEISHU_AUTHORIZE_URL = "https://accounts.feishu.cn/open-apis/authen/v1/authorize"
token_lock = asyncio.Lock()  # Add token lock

try:
    larkClient = lark.Client.builder() \
        .app_id(LARK_APP_ID) \
        .app_secret(LARK_APP_SECRET) \
        .build()
except Exception as e:
    print(f"Failed to initialize Lark client: {str(e)}")
    larkClient = None

# Initialize FastMCP server
mcp = FastMCP("lark_doc")

@mcp.tool()
async def get_lark_doc_content(documentUrl: str) -> str:
    """Get Lark document content
    
    Args:
        documentUrl: Lark document URL
    """
    if not larkClient or not larkClient.auth or not larkClient.docx or not larkClient.wiki:
        return "Lark client not properly initialized"
                
    async with token_lock:
        current_token = USER_ACCESS_TOKEN
    if not current_token or await _check_token_expired():
        try:
            current_token = await _auth_flow()
        except Exception as e:
            return f"Failed to get user access token: {str(e)}"

    # 1. Extract document ID
    docMatch = re.search(r'/(?:docx|wiki)/([A-Za-z0-9]+)', documentUrl)
    if not docMatch:
        return "Invalid Lark document URL format"

    docID = docMatch.group(1)
    client = lark.Client.builder() \
        .enable_set_token(True) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    option = lark.RequestOption.builder().user_access_token(current_token).build()

    # 4. Get actual document content
    contentRequest: RawContentDocumentRequest = RawContentDocumentRequest.builder() \
        .document_id(docID) \
        .lang(0) \
        .build()
        
    contentResponse: RawContentDocumentResponse = client.docx.v1.document.raw_content(contentRequest, option)

    if not contentResponse.success():
        return f"Failed to get document content: code {contentResponse.code}, message: {contentResponse.msg}"
 
    if not contentResponse.data or not contentResponse.data.content:
        return f"Document content is empty, {contentResponse}"
        
    return contentResponse.data.content  # Ensure return string type


async def _refresh_token() -> bool:
    """Refresh the user access token using refresh token"""
    global USER_ACCESS_TOKEN, TOKEN_EXPIRES_AT, REFRESH_TOKEN, REFRESH_TOKEN_EXPIRES_AT
    
    if not REFRESH_TOKEN or not larkClient:
        return False
    
    # 检查refresh_token是否过期
    if await _check_refresh_token_expired():
        print("Refresh token has expired, need to re-authorize")
        # 清除过期的token信息
        async with token_lock:
            USER_ACCESS_TOKEN = None
            REFRESH_TOKEN = None
            TOKEN_EXPIRES_AT = None
            REFRESH_TOKEN_EXPIRES_AT = None
        return False
        
    # 构建刷新token的请求
    request_body = {
        "grant_type": "refresh_token",
        "client_id": LARK_APP_ID,
        "client_secret": LARK_APP_SECRET,
        "refresh_token": REFRESH_TOKEN
    }
    
    request: lark.BaseRequest = lark.BaseRequest.builder() \
        .http_method(lark.HttpMethod.POST) \
        .uri("/open-apis/authen/v2/oauth/token") \
        .body(request_body) \
        .headers({
            "content-type": "application/json"
        }) \
        .build()
            
    option = lark.RequestOption.builder().build()
    
    response: lark.BaseResponse = larkClient.request(request, option)
    
    if not response.success() or not response.raw or not response.raw.content:
        print(f"Failed to refresh token: {response.msg if response else 'No response'} (code: {response.code if response else 'unknown'})")
        return False
        
    result = json.loads(response.raw.content.decode('utf-8'))
    if result.get("code") != 0:
        print(f"Failed to refresh token: {result.get('error_description', 'Unknown error')}")
        return False
    
    # 更新token信息
    async with token_lock:
        USER_ACCESS_TOKEN = result.get("access_token")
        REFRESH_TOKEN = result.get("refresh_token")  # 获取新的refresh_token
        expires_in = result.get("expires_in", 0)
        TOKEN_EXPIRES_AT = time.time() + expires_in if expires_in else None
        
        # 更新refresh_token过期时间
        refresh_expires_in = result.get("refresh_expires_in", 0)
        if refresh_expires_in:
            REFRESH_TOKEN_EXPIRES_AT = time.time() + refresh_expires_in
        
    return True

# 添加一个检查 token 是否过期的函数
async def _check_token_expired() -> bool:
    """Check if the current token has expired"""
    async with token_lock:
        if not TOKEN_EXPIRES_AT or not USER_ACCESS_TOKEN:
            return True
        # 提前 60 秒认为 token 过期，以避免边界情况
        return time.time() + 60 >= TOKEN_EXPIRES_AT
        
# 添加一个检查 refresh_token 是否过期的函数
async def _check_refresh_token_expired() -> bool:
    """Check if the current refresh token has expired"""
    async with token_lock:
        if not REFRESH_TOKEN_EXPIRES_AT or not REFRESH_TOKEN:
            return True
        return time.time() >= REFRESH_TOKEN_EXPIRES_AT

async def _handle_oauth_callback(webReq: web.Request) -> web.Response:
    """Handle OAuth callback from Feishu"""
    code = webReq.query.get('code')
    if not code:
        return web.Response(text="No authorization code received", status=400)
        
    # Exchange code for user_access_token using raw API mode
    request_body = {
        "grant_type": "authorization_code",
        "client_id": LARK_APP_ID,
        "client_secret": LARK_APP_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    
    request: lark.BaseRequest  = lark.BaseRequest.builder() \
        .http_method(lark.HttpMethod.POST) \
        .uri("/open-apis/authen/v2/oauth/token") \
        .body(request_body) \
        .headers({
            "content-type": "application/json"
        }) \
        .build()
            
    # 使用 None 作为 option 参数调用 request 方法
    # 创建一个空的 RequestOption 对象来替代 None
    option = lark.RequestOption.builder().build()
    
    if not larkClient:
        return web.Response(text="Lark client not initialized", status=500)

    response: lark.BaseResponse = larkClient.request(request, option)
    
    if not response.success():
        # print(f"OAuth token request failed:")
        # print(f"Response code: {response.code}")
        # print(f"Response msg: {response.msg}")
        # print(f"Raw response: {response.raw.content if response.raw else 'No raw content'}")
        return web.Response(text=f"Failed to get token: {response.msg} (code: {response.code})", status=500)
        
    # Parse response
    if not response.raw or not response.raw.content:
        return web.Response(text="Empty response from server", status=500)
        
    result = json.loads(response.raw.content.decode('utf-8'))
    if result.get("code") != 0:
        return web.Response(
            text=f"Failed to get token: {result.get('error_description', 'Unknown error')}",
            status=500
        )
    
    # Store token
    global USER_ACCESS_TOKEN, TOKEN_EXPIRES_AT, REFRESH_TOKEN, REFRESH_TOKEN_EXPIRES_AT
    async with token_lock:
        USER_ACCESS_TOKEN = result.get("access_token")
        REFRESH_TOKEN = result.get("refresh_token")
        expires_in = result.get("expires_in", 0)
        TOKEN_EXPIRES_AT = time.time() + expires_in if expires_in else None
        
        # 更新refresh_token过期时间
        refresh_expires_in = result.get("refresh_expires_in", 0)
        if refresh_expires_in:
            REFRESH_TOKEN_EXPIRES_AT = time.time() + refresh_expires_in
        
    return web.Response(text="Authorization successful! You can close this window.")

async def _start_oauth_server() -> str:
    """Start local server to handle OAuth callback"""
    app = web.Application()
    app.router.add_get('/oauth/callback', _handle_oauth_callback)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', OAUTH_PORT)
    await site.start()
    
    try:
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(16)
        
        # Generate authorization URL with state
        params = {
            "client_id": LARK_APP_ID,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "state": state,
            "scope": "docs:document.content:read docx:document:readonly sheets:spreadsheet.meta:read sheets:spreadsheet:read wiki:node:read wiki:wiki:readonly offline_access"  # 移除 %20，使用普通空格

        }
        
        query = "&".join([f"{k}={quote(str(v))}" for k, v in params.items()])
        auth_url = f"{FEISHU_AUTHORIZE_URL}?{query}"
        
        # Open browser for authorization
        webbrowser.open(auth_url)
        
        # Wait for callback to set the token with timeout
        start_time = asyncio.get_event_loop().time()
        while True:
            if asyncio.get_event_loop().time() - start_time > 300:  # 5分钟超时
                raise TimeoutError("Authorization timeout after 5 minutes")
                
            await asyncio.sleep(1)
            async with token_lock:
                if USER_ACCESS_TOKEN:
                    return USER_ACCESS_TOKEN
    finally:
        # 确保服务器总是被清理
        await runner.cleanup()
        
    return None

# Update _auth_flow to use the server
async def _auth_flow() -> str:
    """Internal method to handle Feishu authentication flow"""
    global USER_ACCESS_TOKEN, REFRESH_TOKEN, REFRESH_TOKEN_EXPIRES_AT
    
    async with token_lock:
        if USER_ACCESS_TOKEN and not await _check_token_expired():
            return USER_ACCESS_TOKEN
    
    # 检查refresh_token是否过期
    refresh_token_expired = await _check_refresh_token_expired()
    if refresh_token_expired:
        print("Refresh token has expired, need to re-authorize")
        # 清除过期的token信息
        async with token_lock:
            USER_ACCESS_TOKEN = None
            REFRESH_TOKEN = None
            TOKEN_EXPIRES_AT = None
            REFRESH_TOKEN_EXPIRES_AT = None
    
    # 如果access_token过期但有refresh_token且refresh_token未过期，尝试刷新token
    if USER_ACCESS_TOKEN and REFRESH_TOKEN and not refresh_token_expired:
        refresh_success = await _refresh_token()
        if refresh_success:
            async with token_lock:
                return USER_ACCESS_TOKEN

    if not larkClient or not larkClient.auth:
        raise Exception("Lark client not properly initialized")
        
    # 如果刷新失败或没有refresh_token或refresh_token过期，启动OAuth流程
    token = await _start_oauth_server()
    if not token:
        raise Exception("Failed to get user access token")
        
    return token