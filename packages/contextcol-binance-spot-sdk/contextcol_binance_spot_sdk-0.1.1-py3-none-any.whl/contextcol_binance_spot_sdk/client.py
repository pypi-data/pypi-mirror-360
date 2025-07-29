"""
Main ContextCol SDK client
"""

import logging
from typing import Dict, Any, Optional
from .config import Config
from .binance_client import BinanceClient
from .contextcol_api import ContextcolAPI

logger = logging.getLogger(__name__)


class ContextcolClient:
    """Main Contextcol SDK client"""

    def __init__(self, config: Optional[Config] = None, **kwargs):
        """
        Initialize Contextcol client

        Args:
            config: Configuration object (optional)
            **kwargs: Configuration parameters (will be used to create Config if config is None)
        """
        if config is None:
            if kwargs:
                config = Config(**kwargs)
            else:
                config = Config.from_env()

        logger.info(f"Config: {config}")

        self.config = config
        self._binance_client = None
        self._contextcol_api = None

        # Initialize logger
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    @property
    def binance(self) -> BinanceClient:
        """Get Binance client (lazy initialization)"""
        if self._binance_client is None:
            self._binance_client = BinanceClient(self.config)
        return self._binance_client

    @property
    def contextcol(self) -> ContextcolAPI:
        """Get ContextCol API client (lazy initialization)"""
        if self._contextcol_api is None:
            self._contextcol_api = ContextcolAPI(self.config)
        return self._contextcol_api

    def validate_configuration(self) -> Dict[str, Any]:
        """Validate all configuration and connections"""
        result = {
            "binance_connection": False,
            "contextcol_connection": False,
            "errors": [],
        }

        # Test Binance connection
        try:
            self.binance.account.get_account_info()
            result["binance_connection"] = True
        except Exception as e:
            result["errors"].append(f"Binance connection failed: {str(e)}")

        # Test ContextCol connection
        # try:
        #     self.contextcol.validate_api_key()
        #     result["contextcol_connection"] = True
        # except Exception as e:
        #     result["errors"].append(f"ContextCol connection failed: {str(e)}")

        return result

    def close(self):
        """Close all connections"""
        if self._contextcol_api:
            self._contextcol_api.close()
        logger.info("ContextCol client closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
