#!/usr/bin/env python3
import pytest
import json
import os
from unittest.mock import Mock, patch, AsyncMock
from ai_navigator.ai_provider import (
    ClaudeProvider,
    OpenAICompatibleProvider,
    create_ai_provider
)


class TestClaudeProvider:
    
    @pytest.mark.asyncio
    async def test_parse_navigation_request_success(self):
        provider = ClaudeProvider(api_key="test-key")
        
        mock_message = Mock()
        mock_message.content = [Mock(text='{"start": "北京", "end": "上海"}')]
        
        with patch.object(provider.client.messages, 'create', return_value=mock_message):
            result = await provider.parse_navigation_request("从北京到上海")
            
            assert result == {"start": "北京", "end": "上海"}
    
    @pytest.mark.asyncio
    async def test_parse_navigation_request_with_embedded_json(self):
        provider = ClaudeProvider(api_key="test-key")
        
        mock_message = Mock()
        mock_message.content = [Mock(text='Here is the result: {"start": "广州", "end": "深圳"} done')]
        
        with patch.object(provider.client.messages, 'create', return_value=mock_message):
            result = await provider.parse_navigation_request("从广州到深圳")
            
            assert result == {"start": "广州", "end": "深圳"}
    
    def test_parse_json_response_valid_json(self):
        provider = ClaudeProvider(api_key="test-key")
        result = provider._parse_json_response('{"start": "A", "end": "B"}')
        assert result == {"start": "A", "end": "B"}
    
    def test_parse_json_response_invalid_json_raises_error(self):
        provider = ClaudeProvider(api_key="test-key")
        with pytest.raises(ValueError, match="Failed to parse AI response"):
            provider._parse_json_response("not a json string")
    
    def test_parse_json_response_extracts_json_from_text(self):
        provider = ClaudeProvider(api_key="test-key")
        result = provider._parse_json_response('Some text {"key": "value"} more text')
        assert result == {"key": "value"}
    
    @pytest.mark.asyncio
    async def test_select_mcp_tool_success(self):
        provider = ClaudeProvider(api_key="test-key")
        
        mock_message = Mock()
        mock_message.content = [Mock(text='''{
            "tool_name": "geocode",
            "arguments": {"address": "北京"},
            "reasoning": "Use geocode to get coordinates for Beijing"
        }''')]
        
        available_tools = [
            {
                "name": "geocode",
                "description": "Convert address to coordinates",
                "inputSchema": {
                    "type": "object",
                    "properties": {"address": {"type": "string"}},
                    "required": ["address"]
                }
            },
            {
                "name": "search_poi",
                "description": "Search for points of interest",
                "inputSchema": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"]
                }
            }
        ]
        
        with patch.object(provider.client.messages, 'create', return_value=mock_message):
            result = await provider.select_mcp_tool(
                user_intent="获取北京的坐标",
                available_tools=available_tools
            )
            
            assert result["tool_name"] == "geocode"
            assert result["arguments"] == {"address": "北京"}
            assert "reasoning" in result
    
    @pytest.mark.asyncio
    async def test_select_mcp_tool_with_context(self):
        provider = ClaudeProvider(api_key="test-key")
        
        mock_message = Mock()
        mock_message.content = [Mock(text='''{
            "tool_name": "get_current_location",
            "arguments": {},
            "reasoning": "User wants current location based on context"
        }''')]
        
        available_tools = [
            {
                "name": "get_current_location",
                "description": "Get user's current location",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "geocode",
                "description": "Convert address to coordinates",
                "inputSchema": {
                    "type": "object",
                    "properties": {"address": {"type": "string"}}
                }
            }
        ]
        
        context = {"is_current_location": True}
        
        with patch.object(provider.client.messages, 'create', return_value=mock_message):
            result = await provider.select_mcp_tool(
                user_intent="获取当前位置的坐标",
                available_tools=available_tools,
                context=context
            )
            
            assert result["tool_name"] == "get_current_location"
            assert result["arguments"] == {}


class TestOpenAICompatibleProvider:
    
    @pytest.mark.asyncio
    async def test_parse_navigation_request_success(self):
        provider = OpenAICompatibleProvider(
            api_key="test-key",
            base_url="https://api.test.com/v1",
            model="gpt-3.5-turbo"
        )
        
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.aread = AsyncMock(return_value=json.dumps({
            "choices": [{"message": {"content": '{"start": "杭州", "end": "南京"}'}}]
        }).encode('utf-8'))
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            result = await provider.parse_navigation_request("从杭州到南京")
            
            assert result == {"start": "杭州", "end": "南京"}
    
    @pytest.mark.asyncio
    async def test_parse_navigation_request_http_error(self):
        provider = OpenAICompatibleProvider(
            api_key="test-key",
            base_url="https://api.test.com/v1",
            model="gpt-3.5-turbo"
        )
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=Exception("HTTP Error")
            )
            
            with pytest.raises(Exception, match="HTTP Error"):
                await provider.parse_navigation_request("test")
    
    def test_parse_json_response_valid_json(self):
        provider = OpenAICompatibleProvider(
            api_key="test-key",
            base_url="https://api.test.com",
            model="test-model"
        )
        result = provider._parse_json_response('{"start": "C", "end": "D"}')
        assert result == {"start": "C", "end": "D"}
    
    def test_parse_json_response_invalid_json_raises_error(self):
        provider = OpenAICompatibleProvider(
            api_key="test-key",
            base_url="https://api.test.com",
            model="test-model"
        )
        with pytest.raises(ValueError, match="Failed to parse AI response"):
            provider._parse_json_response("invalid json")
    
    def test_base_url_rstrip_slash(self):
        provider = OpenAICompatibleProvider(
            api_key="test-key",
            base_url="https://api.test.com/v1/",
            model="test-model"
        )
        assert provider.base_url == "https://api.test.com/v1"
    
    @pytest.mark.asyncio
    async def test_select_mcp_tool_success(self):
        provider = OpenAICompatibleProvider(
            api_key="test-key",
            base_url="https://api.test.com/v1",
            model="gpt-3.5-turbo"
        )
        
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.aread = AsyncMock(return_value=json.dumps({
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "tool_name": "maps_geo",
                        "arguments": {"address": "上海市"},
                        "reasoning": "Use maps_geo to geocode Shanghai"
                    }, ensure_ascii=False)
                }
            }]
        }).encode('utf-8'))
        
        available_tools = [
            {
                "name": "maps_geo",
                "description": "Geocode an address to get coordinates",
                "inputSchema": {
                    "type": "object",
                    "properties": {"address": {"type": "string"}},
                    "required": ["address"]
                }
            },
            {
                "name": "maps_text_search",
                "description": "Search for places by text",
                "inputSchema": {
                    "type": "object",
                    "properties": {"keywords": {"type": "string"}},
                    "required": ["keywords"]
                }
            }
        ]
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            result = await provider.select_mcp_tool(
                user_intent="获取上海市的坐标",
                available_tools=available_tools
            )
            
            assert result["tool_name"] == "maps_geo"
            assert result["arguments"] == {"address": "上海市"}
            assert "reasoning" in result
    
    @pytest.mark.asyncio
    async def test_select_mcp_tool_with_context(self):
        provider = OpenAICompatibleProvider(
            api_key="test-key",
            base_url="https://api.test.com/v1",
            model="gpt-3.5-turbo"
        )
        
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.aread = AsyncMock(return_value=json.dumps({
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "tool_name": "get_ip_location",
                        "arguments": {},
                        "reasoning": "Use IP location for current position"
                    }, ensure_ascii=False)
                }
            }]
        }).encode('utf-8'))
        
        available_tools = [
            {
                "name": "get_ip_location",
                "description": "Get location based on IP address",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "geocode",
                "description": "Convert address to coordinates",
                "inputSchema": {
                    "type": "object",
                    "properties": {"address": {"type": "string"}}
                }
            }
        ]
        
        context = {"user_preference": "quick_location"}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            result = await provider.select_mcp_tool(
                user_intent="快速获取我的位置",
                available_tools=available_tools,
                context=context
            )
            
            assert result["tool_name"] == "get_ip_location"
            assert result["arguments"] == {}


class TestCreateAIProvider:
    
    def test_create_anthropic_provider_success(self):
        with patch.dict(os.environ, {"AI_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "test-key"}):
            provider = create_ai_provider()
            assert isinstance(provider, ClaudeProvider)
    
    def test_create_anthropic_provider_missing_key(self):
        with patch.dict(os.environ, {"AI_PROVIDER": "anthropic"}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY environment variable not set"):
                create_ai_provider()
    
    def test_create_openai_provider_success(self):
        with patch.dict(os.environ, {
            "AI_PROVIDER": "openai",
            "OPENAI_API_KEY": "test-key",
            "OPENAI_BASE_URL": "https://api.test.com",
            "OPENAI_MODEL": "gpt-4"
        }):
            provider = create_ai_provider()
            assert isinstance(provider, OpenAICompatibleProvider)
            assert provider.model == "gpt-4"
    
    def test_create_openai_provider_missing_api_key(self):
        with patch.dict(os.environ, {
            "AI_PROVIDER": "openai",
            "OPENAI_BASE_URL": "https://api.test.com"
        }, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable not set"):
                create_ai_provider()
    
    def test_create_openai_provider_missing_base_url(self):
        with patch.dict(os.environ, {
            "AI_PROVIDER": "openai",
            "OPENAI_API_KEY": "test-key"
        }, clear=True):
            with pytest.raises(ValueError, match="OPENAI_BASE_URL environment variable not set"):
                create_ai_provider()
    
    def test_create_provider_default_to_anthropic(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=True):
            provider = create_ai_provider()
            assert isinstance(provider, ClaudeProvider)
    
    def test_create_provider_unsupported_type(self):
        with patch.dict(os.environ, {"AI_PROVIDER": "unsupported"}, clear=True):
            with pytest.raises(ValueError, match="Unsupported AI provider: unsupported"):
                create_ai_provider()
