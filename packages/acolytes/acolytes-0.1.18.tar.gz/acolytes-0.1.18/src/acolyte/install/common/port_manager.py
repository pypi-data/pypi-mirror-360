#!/usr/bin/env python3
"""
Port management for multi-project support
Automatically finds available ports in ACOLYTE range
"""

import socket
from typing import Tuple, Optional


class PortManager:
    """Manages port allocation for ACOLYTE projects"""

    # ACOLYTE port ranges
    WEAVIATE_BASE = 42080
    OLLAMA_BASE = 42434
    BACKEND_BASE = 42000

    # Maximum offset to try
    MAX_OFFSET = 100

    @staticmethod
    def is_port_available(port: int) -> bool:
        """Check if a port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", port))
                return True
        except OSError:
            return False

    @classmethod
    def find_next_available(cls, base_port: int, max_attempts: int = 100) -> Optional[int]:
        """
        Find next available port starting from base_port

        Args:
            base_port: Starting port number
            max_attempts: Maximum ports to try

        Returns:
            Available port number or None if all are taken
        """
        for offset in range(max_attempts):
            port = base_port + offset
            if port > 65535:  # Max valid port
                return None

            if cls.is_port_available(port):
                return port

        return None

    @classmethod
    def find_available_ports(cls) -> Tuple[int, int, int]:
        """
        Find available ports for all ACOLYTE services

        Returns:
            Tuple of (weaviate_port, ollama_port, backend_port)

        Raises:
            RuntimeError: If cannot find available ports
        """
        # Find Weaviate port
        weaviate_port = cls.find_next_available(cls.WEAVIATE_BASE)
        if not weaviate_port:
            raise RuntimeError(f"Cannot find available port starting from {cls.WEAVIATE_BASE}")

        # Find Ollama port
        ollama_port = cls.find_next_available(cls.OLLAMA_BASE)
        if not ollama_port:
            raise RuntimeError(f"Cannot find available port starting from {cls.OLLAMA_BASE}")

        # Find Backend port
        backend_port = cls.find_next_available(cls.BACKEND_BASE)
        if not backend_port:
            raise RuntimeError(f"Cannot find available port starting from {cls.BACKEND_BASE}")

        return weaviate_port, ollama_port, backend_port

    @classmethod
    def get_or_suggest_port(cls, preferred_port: int, max_attempts: int = 100) -> int:
        """
        Return the preferred port if available, otherwise the next available one.
        Raises RuntimeError if none found.
        """
        port = cls.find_next_available(preferred_port, max_attempts)
        if port is None:
            raise RuntimeError(f"No available port found starting from {preferred_port}")
        return port

    @classmethod
    def get_service_ports(cls, preferred_ports: dict[str, int] = {}) -> dict:
        """
        Get available ports for all services, using preferred values if possible.
        Returns a dict: {'weaviate': int, 'ollama': int, 'backend': int}
        """
        return {
            "weaviate": cls.get_or_suggest_port(preferred_ports.get("weaviate", cls.WEAVIATE_BASE)),
            "ollama": cls.get_or_suggest_port(preferred_ports.get("ollama", cls.OLLAMA_BASE)),
            "backend": cls.get_or_suggest_port(preferred_ports.get("backend", cls.BACKEND_BASE)),
        }

    @classmethod
    def suggest_ports(cls, preferred_ports: dict[str, int]) -> dict:
        """
        [DEPRECATED] Use get_service_ports instead.
        Suggest available ports based on preferences.
        """
        # For backward compatibility, delegate to new method
        return cls.get_service_ports(preferred_ports)

    @classmethod
    def bind_port_with_retry(cls, port: int, max_attempts: int = 3) -> int:
        """
        [DEPRECATED] Use get_or_suggest_port instead.
        Try to bind a port for Docker Compose, retrying with the next available port if needed.
        """
        return cls.get_or_suggest_port(port, max_attempts)
