"""FastAPI-based local logging server and HTTP logger."""

import asyncio
import sys
import threading
from typing import TYPE_CHECKING

from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import BaseModel
import uvicorn

from bear_utils.constants import SERVER_OK
from bear_utils.logger_manager._log_level import LogLevel, log_levels
from bear_utils.time import EpochTimestamp

if TYPE_CHECKING:
    from httpx import Response


VERBOSE: LogLevel = log_levels.get("VERBOSE")
DEBUG: LogLevel = log_levels.get("DEBUG")
INFO: LogLevel = log_levels.get("INFO")
WARNING: LogLevel = log_levels.get("WARNING")
ERROR: LogLevel = log_levels.get("ERROR")


def get_level(level: str) -> int:
    """Get the numeric value for a given level string."""
    return log_levels.get_int(level)


def get_name(level: int) -> str:
    """Get the name of a logging level by its integer value."""
    return log_levels.get_name(level)


class LogRequest(BaseModel):
    """Request model for logging messages."""

    level: str
    message: str
    args: list[str] = []
    kwargs: dict[str, str] = {}


class LocalLoggingServer:
    """A local server that writes logs to a file."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        log_file: str = "server.log",
        min_level: LogLevel | int | str = DEBUG,
    ) -> None:
        """Initialize the logging server."""
        self.host: str = host
        self.port: int = port
        self.log_file: str = log_file
        self.min_level: LogLevel = log_levels.get(min_level)
        self.app = FastAPI()
        self.server_thread = None
        self._running = False
        self._setup_routes()
        self.buffer: list[str] = []

    def _setup_routes(self) -> None:
        """Set up the FastAPI routes for logging and health check."""

        @self.app.post("/log")
        async def log_message(request: LogRequest) -> dict[str, str]:
            self.write_log(request.level, request.message, *request.args, **request.kwargs)
            return {"status": "success"}

        @self.app.get("/health")
        async def health_check() -> dict[str, str]:
            return {"status": "healthy"}

    def write_log(self, level: str, message: str, *args: str, end: str = "\n", **kwargs: str) -> None:
        """Write a log entry to the file - same logic as original logger."""
        timestamp: str = EpochTimestamp.now().to_string()
        try:
            level_t: LogLevel = log_levels.get(level)
            if level_t.value >= self.min_level.value:
                log_entry: str = f"[{timestamp}] {level}: {message}"
                self.buffer.append(log_entry)
                if args:
                    self.buffer.append(f"{end}".join(str(arg) for arg in args))
                if kwargs:
                    for key, value in kwargs.items():
                        self.buffer.append(f"{key}={value}{end}")
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.writelines(self.buffer)
                print(f"{end}".join(self.buffer), file=sys.stderr)
        except Exception:
            print(f"[{timestamp}] {level}: {message}", file=sys.stderr)
        finally:
            self.buffer.clear()

    def start(self) -> None:
        """Start the logging server in a separate thread."""
        if self._running:
            return

        def run_server() -> None:
            """Run the FastAPI server in a new event loop."""
            asyncio.set_event_loop(asyncio.new_event_loop())
            uvicorn.run(self.app, host=self.host, port=self.port, log_level="warning")

        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        self._running = True
        print(f"Logging server started on {self.host}:{self.port}")

    def stop(self) -> None:
        """Stop the logging server."""
        if self._running:
            self._running = False
            print("Logging server stopped")


class ServerLogger:
    """Logger that calls HTTP endpoints but behaves like SimpleLogger."""

    def __init__(self, server_url: str = "http://localhost:8080", min_level: LogLevel | int | str = INFO) -> None:
        """Initialize the ServerLogger."""
        self.server_url: str = server_url.rstrip("/")
        self.min_level: LogLevel = log_levels.get(min_level)
        self.client: AsyncClient = AsyncClient(timeout=5.0)
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

    async def _log(self, lvl: LogLevel, msg: object, *args, **kwargs) -> None:
        """Same interface as SimpleLogger._log but calls HTTP endpoint."""
        if lvl.value >= self.min_level.value:
            try:
                response: Response = await self.client.post(
                    url=f"{self.server_url}/log",
                    json={
                        "level": lvl.value,
                        "message": msg,
                        "args": args,
                        "kwargs": kwargs,
                    },
                )
                if response.status_code != SERVER_OK:
                    self._fallback_log(lvl, msg, *args, **kwargs)
            except Exception:
                self._fallback_log(lvl, msg, *args, **kwargs)

    def _fallback_log(self, lvl: LogLevel, msg: object, *args, **kwargs) -> None:
        """Fallback - same as original SimpleLogger._log."""
        timestamp: str = EpochTimestamp.now().to_string()
        print(f"[{timestamp}] {lvl.value}: {msg}", file=sys.stderr)
        if args:
            print(" ".join(str(arg) for arg in args), file=sys.stderr)
        if kwargs:
            for key, value in kwargs.items():
                print(f"{key}={value}", file=sys.stderr)

    async def verbose(self, msg: object, *args, **kwargs) -> None:
        """Log a verbose message."""
        await self._log(VERBOSE, msg, *args, **kwargs)

    async def debug(self, msg: object, *args, **kwargs) -> None:
        """Log a debug message."""
        await self._log(DEBUG, msg, *args, **kwargs)

    async def info(self, msg: object, *args, **kwargs) -> None:
        """Log an info message."""
        await self._log(INFO, msg, *args, **kwargs)

    async def warning(self, msg: object, *args, **kwargs) -> None:
        """Log a warning message."""
        await self._log(WARNING, msg, *args, **kwargs)

    async def error(self, msg: object, *args, **kwargs) -> None:
        """Log an error message."""
        await self._log(ERROR, msg, *args, **kwargs)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()


if __name__ == "__main__":
    server = LocalLoggingServer(port=8080, log_file="server.log")
    try:
        while True:
            server.start()
    except KeyboardInterrupt:
        print("Stopping server...")
        server.stop()
        sys.exit(0)
#     time.sleep(2)

#     # Use logger exactly like SimpleLogger
#     logger = HTTPLogger("http://localhost:8080")

#     logger.verbose("This is a verbose message")
#     logger.debug("This is a debug message")
#     logger.info("This is an info message")
#     logger.warning("This is a warning message")
#     logger.error("This is an error message")

#     logger.close()
#     time.sleep(1)
#     server.stop()
