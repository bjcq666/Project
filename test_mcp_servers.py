#!/usr/bin/env python3
"""
Unit Tests for MCP Servers

Tests for mcp_file_server.py and mcp_network_server.py
"""

import unittest
import asyncio
import json
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import sys

class TestMCPFileServer(unittest.TestCase):
    """Test suite for File Operations MCP Server"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
        self.test_content = "Hello, MCP File Server!"
        
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_read_file_success(self):
        """Test reading a file successfully"""
        with open(self.test_file, 'w') as f:
            f.write(self.test_content)
        
        from mcp_file_server import handle_call_tool
        
        async def run_test():
            result = await handle_call_tool("read_file", {
                "path": self.test_file
            })
            
            self.assertEqual(len(result), 1)
            data = json.loads(result[0].text)
            self.assertTrue(data["success"])
            self.assertEqual(data["content"], self.test_content)
            self.assertEqual(data["path"], self.test_file)
        
        asyncio.run(run_test())
    
    def test_read_file_not_found(self):
        """Test reading non-existent file"""
        from mcp_file_server import handle_call_tool
        
        async def run_test():
            result = await handle_call_tool("read_file", {
                "path": "/nonexistent/file.txt"
            })
            
            data = json.loads(result[0].text)
            self.assertFalse(data["success"])
            self.assertIn("not found", data["error"].lower())
        
        asyncio.run(run_test())
    
    def test_write_file_success(self):
        """Test writing a file successfully"""
        from mcp_file_server import handle_call_tool
        
        new_file = os.path.join(self.test_dir, "new_file.txt")
        content = "New content"
        
        async def run_test():
            result = await handle_call_tool("write_file", {
                "path": new_file,
                "content": content
            })
            
            data = json.loads(result[0].text)
            self.assertTrue(data["success"])
            self.assertTrue(os.path.exists(new_file))
            
            with open(new_file, 'r') as f:
                self.assertEqual(f.read(), content)
        
        asyncio.run(run_test())
    
    def test_write_file_append(self):
        """Test appending to a file"""
        from mcp_file_server import handle_call_tool
        
        with open(self.test_file, 'w') as f:
            f.write("Initial content\n")
        
        async def run_test():
            result = await handle_call_tool("write_file", {
                "path": self.test_file,
                "content": "Appended content\n",
                "append": True
            })
            
            data = json.loads(result[0].text)
            self.assertTrue(data["success"])
            
            with open(self.test_file, 'r') as f:
                content = f.read()
                self.assertIn("Initial content", content)
                self.assertIn("Appended content", content)
        
        asyncio.run(run_test())
    
    def test_list_directory_success(self):
        """Test listing directory contents"""
        from mcp_file_server import handle_call_tool
        
        os.makedirs(os.path.join(self.test_dir, "subdir"))
        Path(os.path.join(self.test_dir, "file1.txt")).touch()
        Path(os.path.join(self.test_dir, "file2.txt")).touch()
        
        async def run_test():
            result = await handle_call_tool("list_directory", {
                "path": self.test_dir
            })
            
            data = json.loads(result[0].text)
            self.assertTrue(data["success"])
            self.assertEqual(data["count"], 3)
            
            names = [entry["name"] for entry in data["entries"]]
            self.assertIn("subdir", names)
            self.assertIn("file1.txt", names)
            self.assertIn("file2.txt", names)
        
        asyncio.run(run_test())
    
    def test_create_directory_success(self):
        """Test creating a directory"""
        from mcp_file_server import handle_call_tool
        
        new_dir = os.path.join(self.test_dir, "new_directory")
        
        async def run_test():
            result = await handle_call_tool("create_directory", {
                "path": new_dir
            })
            
            data = json.loads(result[0].text)
            self.assertTrue(data["success"])
            self.assertTrue(os.path.isdir(new_dir))
        
        asyncio.run(run_test())
    
    def test_delete_file_success(self):
        """Test deleting a file"""
        from mcp_file_server import handle_call_tool
        
        Path(self.test_file).touch()
        
        async def run_test():
            result = await handle_call_tool("delete_file", {
                "path": self.test_file
            })
            
            data = json.loads(result[0].text)
            self.assertTrue(data["success"])
            self.assertFalse(os.path.exists(self.test_file))
        
        asyncio.run(run_test())
    
    def test_move_file_success(self):
        """Test moving a file"""
        from mcp_file_server import handle_call_tool
        
        with open(self.test_file, 'w') as f:
            f.write("Test content")
        
        dest = os.path.join(self.test_dir, "moved.txt")
        
        async def run_test():
            result = await handle_call_tool("move_file", {
                "source": self.test_file,
                "destination": dest
            })
            
            data = json.loads(result[0].text)
            self.assertTrue(data["success"])
            self.assertFalse(os.path.exists(self.test_file))
            self.assertTrue(os.path.exists(dest))
        
        asyncio.run(run_test())
    
    def test_copy_file_success(self):
        """Test copying a file"""
        from mcp_file_server import handle_call_tool
        
        with open(self.test_file, 'w') as f:
            f.write("Test content")
        
        dest = os.path.join(self.test_dir, "copied.txt")
        
        async def run_test():
            result = await handle_call_tool("copy_file", {
                "source": self.test_file,
                "destination": dest
            })
            
            data = json.loads(result[0].text)
            self.assertTrue(data["success"])
            self.assertTrue(os.path.exists(self.test_file))
            self.assertTrue(os.path.exists(dest))
        
        asyncio.run(run_test())
    
    def test_file_info_success(self):
        """Test getting file information"""
        from mcp_file_server import handle_call_tool
        
        with open(self.test_file, 'w') as f:
            f.write("Test content")
        
        async def run_test():
            result = await handle_call_tool("file_info", {
                "path": self.test_file
            })
            
            data = json.loads(result[0].text)
            self.assertTrue(data["success"])
            self.assertEqual(data["type"], "file")
            self.assertEqual(data["name"], os.path.basename(self.test_file))
            self.assertGreater(data["size"], 0)
        
        asyncio.run(run_test())


class TestMCPNetworkServer(unittest.TestCase):
    """Test suite for Network Operations MCP Server"""
    
    @patch('aiohttp.ClientSession')
    def test_http_get_success(self, mock_session_class):
        """Test HTTP GET request"""
        from mcp_network_server import handle_call_tool
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json = AsyncMock(return_value={"message": "success"})
        mock_response.url = "https://api.example.com/data"
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        async def run_test():
            result = await handle_call_tool("http_get", {
                "url": "https://api.example.com/data"
            })
            
            data = json.loads(result[0].text)
            self.assertTrue(data["success"])
            self.assertEqual(data["status"], 200)
            self.assertEqual(data["data"]["message"], "success")
        
        asyncio.run(run_test())
    
    @patch('aiohttp.ClientSession')
    def test_http_post_success(self, mock_session_class):
        """Test HTTP POST request"""
        from mcp_network_server import handle_call_tool
        
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json = AsyncMock(return_value={"id": "123", "created": True})
        mock_response.url = "https://api.example.com/create"
        
        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        async def run_test():
            result = await handle_call_tool("http_post", {
                "url": "https://api.example.com/create",
                "data": {"name": "test"}
            })
            
            data = json.loads(result[0].text)
            self.assertTrue(data["success"])
            self.assertEqual(data["status"], 201)
            self.assertTrue(data["data"]["created"])
        
        asyncio.run(run_test())
    
    @patch('aiohttp.ClientSession')
    def test_http_put_success(self, mock_session_class):
        """Test HTTP PUT request"""
        from mcp_network_server import handle_call_tool
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json = AsyncMock(return_value={"updated": True})
        mock_response.url = "https://api.example.com/update/123"
        
        mock_session = AsyncMock()
        mock_session.put = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        async def run_test():
            result = await handle_call_tool("http_put", {
                "url": "https://api.example.com/update/123",
                "data": {"name": "updated"}
            })
            
            data = json.loads(result[0].text)
            self.assertTrue(data["success"])
            self.assertEqual(data["status"], 200)
        
        asyncio.run(run_test())
    
    @patch('aiohttp.ClientSession')
    def test_http_delete_success(self, mock_session_class):
        """Test HTTP DELETE request"""
        from mcp_network_server import handle_call_tool
        
        mock_response = AsyncMock()
        mock_response.status = 204
        mock_response.headers = {'Content-Type': 'text/plain'}
        mock_response.text = AsyncMock(return_value="")
        mock_response.url = "https://api.example.com/delete/123"
        
        mock_session = AsyncMock()
        mock_session.delete = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        async def run_test():
            result = await handle_call_tool("http_delete", {
                "url": "https://api.example.com/delete/123"
            })
            
            data = json.loads(result[0].text)
            self.assertTrue(data["success"])
            self.assertEqual(data["status"], 204)
        
        asyncio.run(run_test())
    
    @patch('aiohttp.ClientSession')
    def test_download_file_success(self, mock_session_class):
        """Test file download"""
        from mcp_network_server import handle_call_tool
        
        test_content = b"File content here"
        
        async def async_iter_chunks(chunks):
            for chunk in chunks:
                yield chunk
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {'Content-Type': 'application/octet-stream'}
        mock_response.content.iter_chunked = lambda size: async_iter_chunks([test_content])
        
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_response)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        with tempfile.TemporaryDirectory() as tmpdir:
            dest = os.path.join(tmpdir, "downloaded.dat")
            
            async def run_test():
                result = await handle_call_tool("download_file", {
                    "url": "https://example.com/file.dat",
                    "destination": dest
                })
                
                data = json.loads(result[0].text)
                self.assertTrue(data["success"])
                self.assertTrue(os.path.exists(dest))
                
                with open(dest, 'rb') as f:
                    self.assertEqual(f.read(), test_content)
            
            asyncio.run(run_test())


class TestMCPClientWebSocket(unittest.TestCase):
    """Test suite for WebSocket transport in MCP Client"""
    
    @patch('websockets.connect')
    def test_websocket_connect_success(self, mock_connect):
        """Test WebSocket connection"""
        from mcp_client import WebSocketTransport, MCPConfig, TransportType
        
        mock_ws = AsyncMock()
        mock_connect.return_value = mock_ws
        
        config = MCPConfig(
            server_url="ws://localhost:8080",
            transport_type=TransportType.WEBSOCKET
        )
        
        transport = WebSocketTransport(config)
        
        async def run_test():
            result = await transport.connect()
            self.assertTrue(result)
            self.assertTrue(transport.connected)
        
        asyncio.run(run_test())
    
    @patch('websockets.connect')
    def test_websocket_send_receive(self, mock_connect):
        """Test WebSocket send and receive"""
        from mcp_client import WebSocketTransport, MCPConfig, TransportType
        
        response_data = {
            "jsonrpc": "2.0",
            "id": None,
            "result": {"tools": []}
        }
        
        mock_ws = AsyncMock()
        
        async def mock_iter():
            yield json.dumps(response_data)
        
        mock_ws.__aiter__ = lambda self: mock_iter()
        mock_connect.return_value = mock_ws
        
        config = MCPConfig(
            server_url="ws://localhost:8080",
            transport_type=TransportType.WEBSOCKET
        )
        
        transport = WebSocketTransport(config)
        
        async def run_test():
            await transport.connect()
            
            await asyncio.sleep(0.1)
            
            if transport.receive_task:
                transport.receive_task.cancel()
                try:
                    await transport.receive_task
                except asyncio.CancelledError:
                    pass
            
            await transport.disconnect()
            self.assertFalse(transport.connected)
        
        asyncio.run(run_test())


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestMCPFileServer))
    suite.addTests(loader.loadTestsFromTestCase(TestMCPNetworkServer))
    suite.addTests(loader.loadTestsFromTestCase(TestMCPClientWebSocket))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
