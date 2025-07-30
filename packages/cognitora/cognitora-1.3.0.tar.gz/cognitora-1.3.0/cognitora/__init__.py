"""
Cognitora Python SDK - Operating System for Autonomous AI Agents

This SDK provides a comprehensive interface to interact with the Cognitora platform,
including code execution, session management, and container orchestration.

Example usage:
    from cognitora import Cognitora

    # Initialize client
    client = Cognitora(api_key="your_api_key_here")

    # Execute Python code
    result = client.code_interpreter.execute(
        code='print("Hello from Cognitora!")',
        language="python"
    )
    print(result.data.outputs)

    # Create persistent session
    session = client.code_interpreter.create_session(
        language="python",
        timeout_minutes=30
    )

    # Execute code in session (variables persist)
    result1 = client.code_interpreter.execute(
        code="x = 42",
        session_id=session.data.session_id
    )

    result2 = client.code_interpreter.execute(
        code="print(f'The value of x is {x}')",
        session_id=session.data.session_id
    )

    # Use compute for containers
    execution = client.compute.create_execution(
        image="docker.io/library/python:3.11",
        command=["python", "-c", "print('Hello from container!')"],
        cpu_cores=1.0,
        memory_mb=512,
        max_cost_credits=10
    )
"""

import asyncio
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional, Union

import aiohttp
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

__version__ = "1.3.0"
__all__ = [
    "Cognitora",
    "CodeInterpreter",
    "AsyncCodeInterpreter",
    "Compute",
    "AsyncCompute",
    "ExecuteCodeRequest",
    "ExecuteCodeResponse",
    "CreateSessionRequest",
    "Session",
    "SessionDetails",
    "ComputeExecutionRequest",
    "Execution",
    "CognitoraError",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
]


class CognitoraError(Exception):
    """Base exception for Cognitora SDK errors."""

    pass


class APIError(CognitoraError):
    """API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class AuthenticationError(APIError):
    """Authentication-related errors."""

    pass


class RateLimitError(APIError):
    """Rate limit exceeded errors."""

    pass


@dataclass
class FileUpload:
    """File to upload with code execution."""

    name: str
    content: str
    encoding: str = "string"  # "string" or "base64"


@dataclass
class ExecuteCodeRequest:
    """Request for code execution."""

    code: str
    language: str = "python"
    session_id: Optional[str] = None
    files: Optional[List[FileUpload]] = None
    timeout_seconds: int = 60
    environment: Optional[Dict[str, str]] = None


@dataclass
class ExecuteCodeOutput:
    """Single output from code execution."""

    type: str  # stdout, stderr, display_data, execution_result, error
    data: Any
    timestamp: str


@dataclass
class ExecuteCodeData:
    """Data section of execute code response."""

    session_id: str
    status: str  # completed, failed, timeout
    outputs: List[ExecuteCodeOutput]
    execution_time_ms: int
    created_at: str


@dataclass
class ExecuteCodeResponse:
    """Response from code execution."""

    data: ExecuteCodeData
    errors: Optional[List[str]] = None


@dataclass
class CreateSessionRequest:
    """Request for session creation."""

    language: str = "python"
    timeout_minutes: int = 60
    environment: Optional[Dict[str, str]] = None
    resources: Optional[Dict[str, Union[int, float]]] = None


@dataclass
class SessionResources:
    """Session resource allocation."""

    cpu_cores: float = 1.0
    memory_mb: int = 512
    storage_gb: int = 5


@dataclass
class Session:
    """Session information."""

    session_id: str
    language: str
    status: str
    expires_at: str
    created_at: str
    resources: SessionResources


@dataclass
class SessionExecution:
    """Execution within a session."""

    id: str
    language: str
    status: str
    outputs: List[Dict]
    uploaded_files: List[str]
    errors: Optional[List[str]]
    created_at: str


@dataclass
class SessionDetails:
    """Detailed session information with execution history."""

    session_id: str
    language: str
    status: str
    expires_at: str
    created_at: str
    resources: SessionResources
    executions: List[SessionExecution]


@dataclass
class ComputeExecutionRequest:
    """Request for compute execution."""

    image: str
    command: List[str]
    cpu_cores: float
    memory_mb: int
    max_cost_credits: int
    environment: Optional[Dict[str, str]] = None
    timeout_seconds: int = 300
    storage_gb: int = 5
    gpu_count: int = 0


@dataclass
class ExecutionResources:
    """Execution resource allocation."""

    cpu_cores: float
    memory_mb: int
    storage_gb: int
    gpu_count: int

    @classmethod
    def from_api_response(cls, data: Dict) -> "ExecutionResources":
        """Create ExecutionResources from API response (handles camelCase)"""
        return cls(
            cpu_cores=data.get("cpuCores", data.get("cpu_cores", 1.0)),
            memory_mb=data.get("memoryMb", data.get("memory_mb", 512)),
            storage_gb=data.get("storageGb", data.get("storage_gb", 5)),
            gpu_count=data.get("gpuCount", data.get("gpu_count", 0)),
        )


@dataclass
class Execution:
    """Compute execution information."""

    id: str
    status: str
    image: str
    command: List[str]
    resources: ExecutionResources
    max_cost_credits: int
    created_at: str
    actual_cost_credits: Optional[int] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class BaseClient:
    """Base client with common functionality."""

    def __init__(
        self, api_key: str, base_url: str = "http://localhost:8080", timeout: int = 30
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        # Setup requests session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"cognitora-python-sdk/{__version__}",
            }
        )

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request with error handling."""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)

            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", f"HTTP {response.status_code}")
                except:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                raise APIError(
                    error_msg,
                    response.status_code,
                    error_data if "error_data" in locals() else None,
                )

            return response.json()

        except requests.exceptions.RequestException as e:
            raise CognitoraError(f"Request failed: {str(e)}")


class CodeInterpreter(BaseClient):
    """Code Interpreter client for executing code in sandboxed environments."""

    def __init__(
        self, api_key: str, base_url: str = "http://localhost:8080", timeout: int = 30
    ):
        super().__init__(api_key, base_url, timeout)
        self.endpoint_prefix = "/api/v1/code-interpreter"

    def execute(
        self,
        code: str,
        language: str = "python",
        session_id: Optional[str] = None,
        files: Optional[List[FileUpload]] = None,
        timeout_seconds: int = 60,
        environment: Optional[Dict[str, str]] = None,
    ) -> ExecuteCodeResponse:
        """
        Execute code in a new or existing session.

        Args:
            code: The code to execute
            language: Programming language (python, javascript, bash)
            session_id: Optional session ID to reuse existing session
            files: Optional list of files to upload
            timeout_seconds: Execution timeout in seconds
            environment: Optional environment variables

        Returns:
            ExecuteCodeResponse with execution results
        """
        request_data = {
            "code": code,
            "language": language,
            "timeout_seconds": timeout_seconds,
        }

        if session_id:
            request_data["session_id"] = session_id
        if files:
            request_data["files"] = [asdict(f) for f in files]
        if environment:
            request_data["environment"] = environment

        response_data = self._make_request(
            "POST", f"{self.endpoint_prefix}/execute", json=request_data
        )

        # Convert response to dataclass
        data = response_data["data"]
        outputs = [
            ExecuteCodeOutput(
                type=output["type"],
                data=output["data"],
                timestamp=output.get("timestamp", ""),
            )
            for output in data["outputs"]
        ]

        execute_data = ExecuteCodeData(
            session_id=data["session_id"],
            status=data["status"],
            outputs=outputs,
            execution_time_ms=data["execution_time_ms"],
            created_at=data["created_at"],
        )

        return ExecuteCodeResponse(
            data=execute_data, errors=response_data.get("errors")
        )

    def create_session(
        self,
        language: str = "python",
        timeout_minutes: int = 60,
        environment: Optional[Dict[str, str]] = None,
        resources: Optional[Dict[str, Union[int, float]]] = None,
    ) -> Session:
        """
        Create a new persistent session.

        Args:
            language: Programming language for the session
            timeout_minutes: Session timeout in minutes
            environment: Optional environment variables
            resources: Optional resource constraints

        Returns:
            Session object with session details
        """
        request_data = {"language": language, "timeout_minutes": timeout_minutes}

        if environment:
            request_data["environment"] = environment
        if resources:
            request_data["resources"] = resources

        response_data = self._make_request(
            "POST", f"{self.endpoint_prefix}/sessions", json=request_data
        )

        data = response_data["data"]
        return Session(
            session_id=data["session_id"],
            language=data["language"],
            status=data["status"],
            expires_at=data["expires_at"],
            created_at=data["created_at"],
            resources=SessionResources(**data.get("resources", {})),
        )

    def list_sessions(self) -> List[Session]:
        """List all active sessions for the account."""
        response_data = self._make_request("GET", f"{self.endpoint_prefix}/sessions")

        sessions = []
        for session_data in response_data["data"]["sessions"]:
            sessions.append(
                Session(
                    session_id=session_data["id"],
                    language=session_data["language"],
                    status=session_data["status"],
                    expires_at=session_data["expires_at"],
                    created_at=session_data["created_at"],
                    resources=SessionResources(**session_data.get("resources", {})),
                )
            )

        return sessions

    def get_session(self, session_id: str) -> SessionDetails:
        """Get detailed session information with execution history."""
        response_data = self._make_request(
            "GET", f"{self.endpoint_prefix}/sessions/{session_id}"
        )

        data = response_data["data"]

        executions = []
        for exec_data in data.get("executions", []):
            executions.append(
                SessionExecution(
                    id=exec_data["id"],
                    language=exec_data["language"],
                    status=exec_data["status"],
                    outputs=exec_data["outputs"],
                    uploaded_files=exec_data.get("uploaded_files", []),
                    errors=exec_data.get("errors"),
                    created_at=exec_data["created_at"],
                )
            )

        return SessionDetails(
            session_id=data["session_id"],
            language=data["language"],
            status=data["status"],
            expires_at=data["expires_at"],
            created_at=data["created_at"],
            resources=SessionResources(**data.get("resources", {})),
            executions=executions,
        )

    def delete_session(self, session_id: str) -> bool:
        """Terminate a session."""
        self._make_request("DELETE", f"{self.endpoint_prefix}/sessions/{session_id}")
        return True

    def get_session_logs(
        self, session_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict]:
        """Get session execution logs."""
        params = {"limit": limit, "offset": offset}
        response_data = self._make_request(
            "GET", f"{self.endpoint_prefix}/sessions/{session_id}/logs", params=params
        )

        return response_data["data"]["logs"]

    # Convenience methods
    def run_python(
        self, code: str, session_id: Optional[str] = None
    ) -> ExecuteCodeResponse:
        """Execute Python code."""
        return self.execute(code, "python", session_id)

    def run_javascript(
        self, code: str, session_id: Optional[str] = None
    ) -> ExecuteCodeResponse:
        """Execute JavaScript code."""
        return self.execute(code, "javascript", session_id)

    def run_bash(
        self, command: str, session_id: Optional[str] = None
    ) -> ExecuteCodeResponse:
        """Execute bash command."""
        return self.execute(command, "bash", session_id)

    def run_with_files(
        self,
        code: str,
        files: List[FileUpload],
        language: str = "python",
        session_id: Optional[str] = None,
    ) -> ExecuteCodeResponse:
        """Execute code with file uploads."""
        return self.execute(
            code=code, language=language, session_id=session_id, files=files
        )


class Compute(BaseClient):
    """Compute client for container orchestration and execution."""

    def __init__(
        self, api_key: str, base_url: str = "http://localhost:8080", timeout: int = 30
    ):
        super().__init__(api_key, base_url, timeout)
        self.endpoint_prefix = "/api/v1/compute"

    def create_execution(
        self,
        image: str,
        command: List[str],
        cpu_cores: float,
        memory_mb: int,
        max_cost_credits: int,
        environment: Optional[Dict[str, str]] = None,
        timeout_seconds: int = 300,
        storage_gb: int = 5,
        gpu_count: int = 0,
    ) -> Execution:
        """
        Create a new compute execution.

        Args:
            image: Container image to use
            command: Command to execute
            cpu_cores: CPU cores to allocate
            memory_mb: Memory in MB to allocate
            max_cost_credits: Maximum credits to spend
            environment: Optional environment variables
            timeout_seconds: Execution timeout
            storage_gb: Storage in GB to allocate
            gpu_count: Number of GPUs to allocate

        Returns:
            Execution object with execution details
        """
        request_data = {
            "image": image,
            "command": command,
            "cpuCores": cpu_cores,
            "memoryMb": memory_mb,
            "maxCostCredits": max_cost_credits,
            "timeoutSeconds": timeout_seconds,
            "storageGb": storage_gb,
            "gpuCount": gpu_count,
        }

        if environment:
            request_data["environment"] = environment

        response_data = self._make_request(
            "POST", f"{self.endpoint_prefix}/executions", json=request_data
        )

        return Execution(
            id=response_data["id"],
            status=response_data["status"],
            image=response_data["image"],
            command=response_data.get("command", []),
            resources=ExecutionResources.from_api_response(response_data["resources"]),
            max_cost_credits=response_data["maxCostCredits"],
            created_at=response_data["createdAt"],
            actual_cost_credits=response_data.get("actualCostCredits"),
            started_at=response_data.get("startedAt"),
            completed_at=response_data.get("completedAt"),
        )

    def list_executions(
        self, limit: int = 50, offset: int = 0, status: Optional[str] = None
    ) -> List[Execution]:
        """List compute executions with optional filtering."""
        params: Dict[str, Union[int, str]] = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status

        response_data = self._make_request(
            "GET", f"{self.endpoint_prefix}/executions", params=params
        )

        executions = []
        for exec_data in response_data["executions"]:
            executions.append(
                Execution(
                    id=exec_data["id"],
                    status=exec_data["status"],
                    image=exec_data["image"],
                    command=exec_data.get("command", []),
                    resources=ExecutionResources.from_api_response(
                        exec_data["resources"]
                    ),
                    max_cost_credits=exec_data["maxCostCredits"],
                    created_at=exec_data["createdAt"],
                    actual_cost_credits=exec_data.get("actualCostCredits"),
                    started_at=exec_data.get("startedAt"),
                    completed_at=exec_data.get("completedAt"),
                )
            )

        return executions

    def get_execution(self, execution_id: str) -> Execution:
        """Get execution details by ID."""
        response_data = self._make_request(
            "GET", f"{self.endpoint_prefix}/executions/{execution_id}"
        )

        return Execution(
            id=response_data["id"],
            status=response_data["status"],
            image=response_data["image"],
            command=response_data.get("command", []),
            resources=ExecutionResources.from_api_response(response_data["resources"]),
            max_cost_credits=response_data["maxCostCredits"],
            created_at=response_data["createdAt"],
            actual_cost_credits=response_data.get("actualCostCredits"),
            started_at=response_data.get("startedAt"),
            completed_at=response_data.get("completedAt"),
        )

    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution."""
        self._make_request(
            "DELETE", f"{self.endpoint_prefix}/executions/{execution_id}"
        )
        return True

    def get_execution_logs(self, execution_id: str) -> str:
        """Get execution logs."""
        response_data = self._make_request(
            "GET", f"{self.endpoint_prefix}/executions/{execution_id}/logs"
        )
        return response_data["logs"]

    def estimate_cost(
        self,
        cpu_cores: float,
        memory_mb: int,
        storage_gb: int = 5,
        gpu_count: int = 0,
        timeout_seconds: int = 300,
    ) -> Dict[str, float]:
        """Estimate cost for execution parameters."""
        request_data = {
            "cpuCores": cpu_cores,
            "memoryMb": memory_mb,
            "storageGb": storage_gb,
            "gpuCount": gpu_count,
            "timeoutSeconds": timeout_seconds,
        }

        return self._make_request(
            "POST", f"{self.endpoint_prefix}/estimate", json=request_data
        )


# Async versions for better performance
class AsyncBaseClient:
    """Async base client with common functionality."""

    def __init__(
        self, api_key: str, base_url: str = "http://localhost:8080", timeout: int = 30
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"cognitora-python-sdk/{__version__}",
            },
            timeout=aiohttp.ClientTimeout(total=self.timeout),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make async HTTP request with error handling."""
        if not self.session:
            raise CognitoraError(
                "Client not initialized. Use 'async with' context manager."
            )

        url = f"{self.base_url}{endpoint}"

        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif response.status >= 400:
                    try:
                        error_data = await response.json()
                        error_msg = error_data.get("error", f"HTTP {response.status}")
                    except:
                        error_msg = f"HTTP {response.status}: {await response.text()}"
                    raise APIError(
                        error_msg,
                        response.status,
                        error_data if "error_data" in locals() else None,
                    )

                return await response.json()

        except aiohttp.ClientError as e:
            raise CognitoraError(f"Request failed: {str(e)}")


class AsyncCodeInterpreter(AsyncBaseClient):
    """Async Code Interpreter client."""

    def __init__(
        self, api_key: str, base_url: str = "http://localhost:8080", timeout: int = 30
    ):
        super().__init__(api_key, base_url, timeout)
        self.endpoint_prefix = "/api/v1/code-interpreter"

    async def execute(
        self,
        code: str,
        language: str = "python",
        session_id: Optional[str] = None,
        files: Optional[List[FileUpload]] = None,
        timeout_seconds: int = 60,
        environment: Optional[Dict[str, str]] = None,
    ) -> ExecuteCodeResponse:
        """Async version of execute."""
        request_data = {
            "code": code,
            "language": language,
            "timeout_seconds": timeout_seconds,
        }

        if session_id:
            request_data["session_id"] = session_id
        if files:
            request_data["files"] = [asdict(f) for f in files]
        if environment:
            request_data["environment"] = environment

        response_data = await self._make_request(
            "POST", f"{self.endpoint_prefix}/execute", json=request_data
        )

        # Convert response to dataclass (same logic as sync version)
        data = response_data["data"]
        outputs = [
            ExecuteCodeOutput(
                type=output["type"],
                data=output["data"],
                timestamp=output.get("timestamp", ""),
            )
            for output in data["outputs"]
        ]

        execute_data = ExecuteCodeData(
            session_id=data["session_id"],
            status=data["status"],
            outputs=outputs,
            execution_time_ms=data["execution_time_ms"],
            created_at=data["created_at"],
        )

        return ExecuteCodeResponse(
            data=execute_data, errors=response_data.get("errors")
        )


class AsyncCompute(AsyncBaseClient):
    """Async Compute client."""

    def __init__(
        self, api_key: str, base_url: str = "http://localhost:8080", timeout: int = 30
    ):
        super().__init__(api_key, base_url, timeout)
        self.endpoint_prefix = "/api/v1/compute"

    async def create_execution(
        self,
        image: str,
        command: List[str],
        cpu_cores: float,
        memory_mb: int,
        max_cost_credits: int,
        environment: Optional[Dict[str, str]] = None,
        timeout_seconds: int = 300,
        storage_gb: int = 5,
        gpu_count: int = 0,
    ) -> Execution:
        """Async version of create_execution."""
        request_data = {
            "image": image,
            "command": command,
            "cpuCores": cpu_cores,
            "memoryMb": memory_mb,
            "maxCostCredits": max_cost_credits,
            "timeoutSeconds": timeout_seconds,
            "storageGb": storage_gb,
            "gpuCount": gpu_count,
        }

        if environment:
            request_data["environment"] = environment

        response_data = await self._make_request(
            "POST", f"{self.endpoint_prefix}/executions", json=request_data
        )

        return Execution(
            id=response_data["id"],
            status=response_data["status"],
            image=response_data["image"],
            command=response_data.get("command", []),
            resources=ExecutionResources.from_api_response(response_data["resources"]),
            max_cost_credits=response_data["maxCostCredits"],
            created_at=response_data["createdAt"],
            actual_cost_credits=response_data.get("actualCostCredits"),
            started_at=response_data.get("startedAt"),
            completed_at=response_data.get("completedAt"),
        )


class Cognitora:
    """
    Main Cognitora client providing access to all services.

    This is the primary interface for interacting with the Cognitora platform.
    It provides access to both code interpreter and compute capabilities.

    Example:
        client = Cognitora(api_key="your_api_key")

        # Use code interpreter
        result = client.code_interpreter.execute("print('Hello!')")

        # Use compute
        execution = client.compute.create_execution(
            image="docker.io/library/python:3.11",
            command=["python", "-c", "print('Hello!')"],
            cpu_cores=1.0,
            memory_mb=512,
            max_cost_credits=5
        )
    """

    def __init__(
        self, api_key: str, base_url: str = "http://localhost:8080", timeout: int = 30
    ):
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

        # Initialize service clients
        self.code_interpreter = CodeInterpreter(api_key, base_url, timeout)
        self.compute = Compute(api_key, base_url, timeout)

    def __repr__(self) -> str:
        return f"Cognitora(base_url='{self.base_url}')"

    async def async_client(self):
        """Get async client context manager."""
        return CognitoraAsync(self.api_key, self.base_url, self.timeout)


class CognitoraAsync:
    """Async version of main Cognitora client."""

    def __init__(
        self, api_key: str, base_url: str = "http://localhost:8080", timeout: int = 30
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

    async def __aenter__(self):
        self.code_interpreter = AsyncCodeInterpreter(
            self.api_key, self.base_url, self.timeout
        )
        self.compute = AsyncCompute(self.api_key, self.base_url, self.timeout)

        await self.code_interpreter.__aenter__()
        await self.compute.__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.code_interpreter.__aexit__(exc_type, exc_val, exc_tb)
        await self.compute.__aexit__(exc_type, exc_val, exc_tb)
