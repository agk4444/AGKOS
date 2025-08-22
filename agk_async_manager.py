"""
Async/Await Manager for AGK Language Compiler
Provides asynchronous programming support for web calls and external APIs
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import time
import threading
import concurrent.futures


class AsyncOperationType(Enum):
    """Types of asynchronous operations"""
    HTTP_REQUEST = "http"
    API_CALL = "api"
    FILE_OPERATION = "file"
    DATABASE_QUERY = "database"
    CUSTOM_TASK = "custom"


@dataclass
class AsyncTask:
    """Represents an asynchronous task"""
    id: str
    operation_type: AsyncOperationType
    coroutine: Awaitable
    callback: Optional[Callable] = None
    timeout: Optional[float] = None
    start_time: float = field(default_factory=time.time)
    completed: bool = False
    result: Any = None
    error: Optional[Exception] = None


@dataclass
class AsyncContext:
    """Context for async operations"""
    session: Optional[aiohttp.ClientSession] = None
    thread_pool: Optional[concurrent.futures.ThreadPoolExecutor] = None
    event_loop: Optional[asyncio.AbstractEventLoop] = None
    active_tasks: Dict[str, AsyncTask] = field(default_factory=dict)
    task_counter: int = 0


class AsyncError(Exception):
    """Exception raised for async-related errors"""
    pass


class AGKAsyncManager:
    """Manages asynchronous operations for AGK"""

    def __init__(self):
        self.contexts: Dict[str, AsyncContext] = {}
        self.default_timeout = 30.0
        self.max_concurrent_tasks = 100
        self._lock = threading.Lock()

    def create_context(self, context_id: str = "default") -> AsyncContext:
        """Create a new async context"""
        with self._lock:
            if context_id in self.contexts:
                return self.contexts[context_id]

            context = AsyncContext()
            self.contexts[context_id] = context
            return context

    def get_context(self, context_id: str = "default") -> AsyncContext:
        """Get an existing async context"""
        return self.contexts.get(context_id)

    async def initialize_context(self, context: AsyncContext):
        """Initialize async context with necessary resources"""
        if context.session is None:
            context.session = aiohttp.ClientSession()

        if context.thread_pool is None:
            context.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)

        if context.event_loop is None:
            context.event_loop = asyncio.get_event_loop()

    async def cleanup_context(self, context: AsyncContext):
        """Clean up async context resources"""
        if context.session:
            await context.session.close()
            context.session = None

        if context.thread_pool:
            context.thread_pool.shutdown(wait=True)
            context.thread_pool = None

    def create_async_task(self, context_id: str, operation_type: AsyncOperationType,
                         coroutine: Awaitable, callback: Optional[Callable] = None,
                         timeout: Optional[float] = None) -> str:
        """Create and register an async task"""
        context = self.get_context(context_id) or self.create_context(context_id)

        with self._lock:
            context.task_counter += 1
            task_id = f"{context_id}_{context.task_counter}_{int(time.time())}"

        task = AsyncTask(
            id=task_id,
            operation_type=operation_type,
            coroutine=coroutine,
            callback=callback,
            timeout=timeout or self.default_timeout
        )

        context.active_tasks[task_id] = task
        return task_id

    async def execute_task(self, context: AsyncContext, task: AsyncTask) -> Any:
        """Execute an async task with timeout and error handling"""
        try:
            if task.timeout:
                result = await asyncio.wait_for(task.coroutine, timeout=task.timeout)
            else:
                result = await task.coroutine

            task.completed = True
            task.result = result

            if task.callback:
                task.callback(result)

            return result

        except asyncio.TimeoutError:
            task.completed = True
            task.error = AsyncError(f"Task timed out after {task.timeout} seconds")
            raise task.error
        except Exception as e:
            task.completed = True
            task.error = e
            raise e

    async def await_task(self, context_id: str, task_id: str) -> Any:
        """Wait for a specific task to complete and return its result"""
        context = self.get_context(context_id)
        if not context or task_id not in context.active_tasks:
            raise AsyncError(f"Task {task_id} not found in context {context_id}")

        task = context.active_tasks[task_id]

        if task.completed:
            if task.error:
                raise task.error
            return task.result

        # Execute the task if not already running
        return await self.execute_task(context, task)

    async def await_all(self, context_id: str, task_ids: List[str]) -> List[Any]:
        """Wait for multiple tasks to complete"""
        context = self.get_context(context_id)
        if not context:
            raise AsyncError(f"Context {context_id} not found")

        tasks = []
        for task_id in task_ids:
            if task_id in context.active_tasks:
                task = context.active_tasks[task_id]
                if not task.completed:
                    tasks.append(self.execute_task(context, task))

        if tasks:
            return await asyncio.gather(*tasks, return_exceptions=True)
        return []

    async def http_get(self, context_id: str, url: str, headers: Optional[Dict[str, str]] = None,
                      timeout: Optional[float] = None) -> Dict[str, Any]:
        """Async HTTP GET request"""
        context = self.get_context(context_id) or self.create_context(context_id)
        await self.initialize_context(context)

        async def _http_get():
            async with context.session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=timeout or self.default_timeout)) as response:
                return {
                    'status': response.status,
                    'headers': dict(response.headers),
                    'url': str(response.url),
                    'body': await response.text(),
                    'json': await response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                }

        task_id = self.create_async_task(context_id, AsyncOperationType.HTTP_REQUEST, _http_get(), timeout=timeout)
        return await self.await_task(context_id, task_id)

    async def http_post(self, context_id: str, url: str, data: Any = None,
                       headers: Optional[Dict[str, str]] = None, json_data: Any = None,
                       timeout: Optional[float] = None) -> Dict[str, Any]:
        """Async HTTP POST request"""
        context = self.get_context(context_id) or self.create_context(context_id)
        await self.initialize_context(context)

        async def _http_post():
            async with context.session.post(
                url,
                data=data,
                json=json_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout or self.default_timeout)
            ) as response:
                return {
                    'status': response.status,
                    'headers': dict(response.headers),
                    'url': str(response.url),
                    'body': await response.text(),
                    'json': await response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                }

        task_id = self.create_async_task(context_id, AsyncOperationType.HTTP_REQUEST, _http_post(), timeout=timeout)
        return await self.await_task(context_id, task_id)

    async def http_put(self, context_id: str, url: str, data: Any = None,
                      headers: Optional[Dict[str, str]] = None, json_data: Any = None,
                      timeout: Optional[float] = None) -> Dict[str, Any]:
        """Async HTTP PUT request"""
        context = self.get_context(context_id) or self.create_context(context_id)
        await self.initialize_context(context)

        async def _http_put():
            async with context.session.put(
                url,
                data=data,
                json=json_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout or self.default_timeout)
            ) as response:
                return {
                    'status': response.status,
                    'headers': dict(response.headers),
                    'url': str(response.url),
                    'body': await response.text(),
                    'json': await response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                }

        task_id = self.create_async_task(context_id, AsyncOperationType.HTTP_REQUEST, _http_put(), timeout=timeout)
        return await self.await_task(context_id, task_id)

    async def http_delete(self, context_id: str, url: str, headers: Optional[Dict[str, str]] = None,
                         timeout: Optional[float] = None) -> Dict[str, Any]:
        """Async HTTP DELETE request"""
        context = self.get_context(context_id) or self.create_context(context_id)
        await self.initialize_context(context)

        async def _http_delete():
            async with context.session.delete(url, headers=headers, timeout=aiohttp.ClientTimeout(total=timeout or self.default_timeout)) as response:
                return {
                    'status': response.status,
                    'headers': dict(response.headers),
                    'url': str(response.url),
                    'body': await response.text(),
                    'json': await response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                }

        task_id = self.create_async_task(context_id, AsyncOperationType.HTTP_REQUEST, _http_delete(), timeout=timeout)
        return await self.await_task(context_id, task_id)

    async def api_call(self, context_id: str, url: str, method: str = "GET",
                      headers: Optional[Dict[str, str]] = None, data: Any = None,
                      api_key: Optional[str] = None, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Generic async API call"""
        context = self.get_context(context_id) or self.create_context(context_id)
        await self.initialize_context(context)

        # Add API key to headers if provided
        if api_key:
            headers = headers or {}
            headers['Authorization'] = f"Bearer {api_key}"

        async def _api_call():
            async with context.session.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                timeout=aiohttp.ClientTimeout(total=timeout or self.default_timeout)
            ) as response:
                return {
                    'status': response.status,
                    'headers': dict(response.headers),
                    'url': str(response.url),
                    'body': await response.text(),
                    'json': await response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                }

        task_id = self.create_async_task(context_id, AsyncOperationType.API_CALL, _api_call(), timeout=timeout)
        return await self.await_task(context_id, task_id)

    async def parallel_requests(self, context_id: str, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple HTTP requests in parallel"""
        context = self.get_context(context_id) or self.create_context(context_id)
        await self.initialize_context(context)

        async def _execute_request(req):
            method = req.get('method', 'GET')
            url = req.get('url')
            headers = req.get('headers')
            data = req.get('data')
            json_data = req.get('json')
            timeout = req.get('timeout', self.default_timeout)

            async with context.session.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                json=json_data,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                return {
                    'status': response.status,
                    'headers': dict(response.headers),
                    'url': str(response.url),
                    'body': await response.text(),
                    'json': await response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                }

        tasks = [_execute_request(req) for req in requests]
        return await asyncio.gather(*tasks, return_exceptions=True)

    def get_active_tasks(self, context_id: str) -> List[str]:
        """Get list of active task IDs"""
        context = self.get_context(context_id)
        if context:
            return list(context.active_tasks.keys())
        return []

    def get_task_status(self, context_id: str, task_id: str) -> Dict[str, Any]:
        """Get status of a specific task"""
        context = self.get_context(context_id)
        if context and task_id in context.active_tasks:
            task = context.active_tasks[task_id]
            return {
                'id': task.id,
                'type': task.operation_type.value,
                'completed': task.completed,
                'start_time': task.start_time,
                'runtime': time.time() - task.start_time,
                'has_error': task.error is not None,
                'error_message': str(task.error) if task.error else None
            }
        return {}

    def cancel_task(self, context_id: str, task_id: str) -> bool:
        """Cancel a running task"""
        context = self.get_context(context_id)
        if context and task_id in context.active_tasks:
            # In a real implementation, you'd need to store task handles
            # For now, just mark as completed with cancellation error
            task = context.active_tasks[task_id]
            if not task.completed:
                task.completed = True
                task.error = AsyncError("Task cancelled")
                return True
        return False

    async def cleanup_all(self):
        """Clean up all async contexts"""
        for context in self.contexts.values():
            await self.cleanup_context(context)
        self.contexts.clear()


# Global async manager instance
async_manager = AGKAsyncManager()

# Convenience functions for use in generated code
async def http_get_async(context_id: str, url: str, headers: Optional[Dict[str, str]] = None, timeout: Optional[float] = None):
    """Async HTTP GET (for use in generated Python code)"""
    return await async_manager.http_get(context_id, url, headers, timeout)

async def http_post_async(context_id: str, url: str, data: Any = None, headers: Optional[Dict[str, str]] = None, json_data: Any = None, timeout: Optional[float] = None):
    """Async HTTP POST (for use in generated Python code)"""
    return await async_manager.http_post(context_id, url, data, headers, json_data, timeout)

async def api_call_async(context_id: str, url: str, method: str = "GET", headers: Optional[Dict[str, str]] = None, data: Any = None, api_key: Optional[str] = None, timeout: Optional[float] = None):
    """Async API call (for use in generated Python code)"""
    return await async_manager.api_call(context_id, url, method, headers, data, api_key, timeout)

async def await_task(context_id: str, task_id: str):
    """Await a task (for use in generated Python code)"""
    return await async_manager.await_task(context_id, task_id)

async def await_all(context_id: str, task_ids: List[str]):
    """Await multiple tasks (for use in generated Python code)"""
    return await async_manager.await_all(context_id, task_ids)

# Example usage and testing
if __name__ == "__main__":
    async def test_async_manager():
        """Test the async manager functionality"""
        print("Testing AGK Async Manager...")

        try:
            # Test HTTP GET
            result = await async_manager.http_get("test", "https://httpbin.org/get", timeout=10)
            print(f"GET Result: Status {result['status']}")

            # Test HTTP POST
            post_data = {"test": "data"}
            result = await async_manager.http_post("test", "https://httpbin.org/post", json_data=post_data, timeout=10)
            print(f"POST Result: Status {result['status']}")

            print("All async tests passed!")

        except Exception as e:
            print(f"Async test error: {e}")

        finally:
            await async_manager.cleanup_all()

    # Run the test
    asyncio.run(test_async_manager())