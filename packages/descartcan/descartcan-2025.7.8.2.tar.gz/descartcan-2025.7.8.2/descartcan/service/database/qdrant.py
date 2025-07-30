# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/6/28 15:47
# Author     ：Maxwell
# Description：
"""

from descartcan.config import config
from qdrant_client import AsyncQdrantClient


def get_qdrant_client() -> AsyncQdrantClient | None:
    if config.QDRANT_HOST and config.QDRANT_HOST:
        client = AsyncQdrantClient(
            port=config.QDRANT_HTTP_PORT, grpc_port=config.QDRANT_GRPC_PORT,
            api_key=config.QDRANT_API_KEY, host=config.QDRANT_HOST
        )
        return client
    return None
