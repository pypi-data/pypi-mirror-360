"""FastAPI-based local logging server and HTTP logger."""

import asyncio
import sys
import threading
from typing import TYPE_CHECKING

from fastapi import FastAPI
from httpx import Client
from pydantic import BaseModel
import uvicorn

from bear_utils.constants import SERVER_OK
from bear_utils.logger_manager._common import DEBUG, ERROR, INFO, VERBOSE, WARNING, LogLevel
from bear_utils.time import EpochTimestamp

if TYPE_CHECKING:
    from httpx import Response


class LogRequest(BaseModel):
    """Request model for logging messages."""

    level: str
    message: str


class LocalLoggingServer:
    """A local server that writes logs to a file."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        log_file: str = "server.log",
        min_level: LogLevel = VERBOSE,
    ) -> None:
        """Initialize the logging server."""
        self.host: str = host
        self.port: int = port
        self.log_file: str = log_file
        self.min_level: LogLevel = min_level
        self.app = FastAPI()
        self.server_thread = None
        self._running = False
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Set up the FastAPI routes for logging and health check."""

        @self.app.post("/log")
        async def log_message(request: LogRequest) -> dict[str, str]:
            self.write_log(request.level, request.message)
            return {"status": "success"}

        @self.app.get("/health")
        async def health_check() -> dict[str, str]:
            return {"status": "healthy"}

    def write_log(self, level: str, message: str) -> None:
        """Write a log entry to the file - same logic as original logger."""
        try:
            log_level = LogLevel(level)
            if log_level.value >= self.min_level.value:
                timestamp = EpochTimestamp.now().to_string()
                log_entry = f"[{timestamp}] {level}: {message}\n"
                print(log_entry, file=sys.stderr)
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(log_entry)
        except Exception:
            # Fallback to stderr like original
            timestamp = EpochTimestamp.now().to_string()
            print(f"[{timestamp}] {level}: {message}", file=sys.stderr)

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

    def __init__(self, server_url: str = "http://localhost:8080", min_level: LogLevel = INFO) -> None:
        """Initialize the ServerLogger."""
        self.server_url: str = server_url.rstrip("/")
        self.min_level: LogLevel = min_level
        self.client = Client(timeout=5.0)

    def _log(self, level: LogLevel, msg: object, *args, **kwargs) -> None:
        """Same interface as SimpleLogger._log but calls HTTP endpoint."""
        if isinstance(level, LogLevel) and level.value >= self.min_level.value:
            try:
                response: Response = self.client.post(
                    url=f"{self.server_url}/log",
                    json={
                        "level": level.value,
                        "message": msg,
                    },
                )
                if response.status_code != SERVER_OK:
                    self._fallback_log(level, msg, *args, **kwargs)
            except Exception:
                self._fallback_log(level, msg, *args, **kwargs)

    def _fallback_log(self, level: LogLevel, msg: object, *args, **kwargs) -> None:
        """Fallback - same as original SimpleLogger._log."""
        timestamp: str = EpochTimestamp.now().to_string()
        print(f"[{timestamp}] {level.value}: {msg}", file=sys.stderr)
        if args:
            print(" ".join(str(arg) for arg in args), file=sys.stderr)
        if kwargs:
            for key, value in kwargs.items():
                print(f"{key}={value}", file=sys.stderr)

    def verbose(self, msg: object, *args, **kwargs) -> None:
        """Log a verbose message."""
        self._log(VERBOSE, msg, *args, **kwargs)

    def debug(self, msg: object, *args, **kwargs) -> None:
        """Log a debug message."""
        self._log(DEBUG, msg, *args, **kwargs)

    def info(self, msg: object, *args, **kwargs) -> None:
        """Log an info message."""
        self._log(INFO, msg, *args, **kwargs)

    def warning(self, msg: object, *args, **kwargs) -> None:
        """Log a warning message."""
        self._log(WARNING, msg, *args, **kwargs)

    def error(self, msg: object, *args, **kwargs) -> None:
        """Log an error message."""
        self._log(ERROR, msg, *args, **kwargs)

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()


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
