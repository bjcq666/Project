#!/usr/bin/env python3
"""
Browser Control MCP Client
Client for connecting to Browser Control MCP Server.
"""

import os
import json
from typing import Optional, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class BrowserMCPClient:
    """Client for interacting with Browser Control MCP Server."""
    
    def __init__(self, server_script_path: Optional[str] = None):
        """
        Initialize Browser MCP Client.
        
        Args:
            server_script_path: Path to the browser MCP server script.
                               If None, will use default location.
        """
        self.server_script_path = server_script_path or os.path.join(
            os.path.dirname(__file__),
            "mcp_browser_server.py"
        )
        self.session: Optional[ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self):
        """Connect to the Browser Control MCP server."""
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script_path],
            env=None
        )
        
        stdio_transport = await stdio_client(server_params)
        self.stdio, self.write = stdio_transport
        self.session = ClientSession(self.stdio, self.write)
        await self.session.initialize()
        
        return self
    
    async def disconnect(self):
        """Disconnect from the Browser Control MCP server."""
        if self.session:
            await self.session.__aexit__(None, None, None)
            self.session = None
    
    async def open_url(self, url: str) -> Dict[str, Any]:
        """
        Open a URL in the default web browser.
        
        Args:
            url: URL to open
            
        Returns:
            Dictionary with success status and message
        """
        if not self.session:
            raise RuntimeError("Not connected to Browser MCP server. Call connect() first.")
        
        try:
            result = await self.session.call_tool(
                "open_url",
                arguments={"url": url}
            )
            
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return json.loads(content.text)
            
            raise ValueError("Failed to open URL")
            
        except Exception as e:
            raise ValueError(f"Browser control error: {str(e)}")
    
    async def open_map_navigation(
        self,
        start_lng: float,
        start_lat: float,
        end_lng: float,
        end_lat: float,
        start_name: Optional[str] = None,
        end_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Open map navigation in browser.
        
        Args:
            start_lng: Start point longitude
            start_lat: Start point latitude
            end_lng: End point longitude
            end_lat: End point latitude
            start_name: Start point name (optional)
            end_name: End point name (optional)
            
        Returns:
            Dictionary with success status, message, and navigation URL
        """
        if not self.session:
            raise RuntimeError("Not connected to Browser MCP server. Call connect() first.")
        
        try:
            args = {
                "start_lng": start_lng,
                "start_lat": start_lat,
                "end_lng": end_lng,
                "end_lat": end_lat
            }
            
            if start_name:
                args["start_name"] = start_name
            if end_name:
                args["end_name"] = end_name
            
            result = await self.session.call_tool(
                "open_map_navigation",
                arguments=args
            )
            
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return json.loads(content.text)
            
            raise ValueError("Failed to open navigation")
            
        except Exception as e:
            raise ValueError(f"Navigation control error: {str(e)}")


def create_browser_client(server_script_path: Optional[str] = None) -> BrowserMCPClient:
    """
    Create a Browser MCP client.
    
    Args:
        server_script_path: Path to the browser MCP server script
        
    Returns:
        BrowserMCPClient instance
    """
    return BrowserMCPClient(server_script_path)
