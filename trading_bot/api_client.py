from typing import Dict, Any
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException, BinanceRequestException
from trading_bot.config import API_KEY, API_SECRET, USE_TESTNET, ENVIRONMENT
from trading_bot.logging_config import get_logger

logger = get_logger(__name__)


class APIError(Exception):
    """Custom exception for API-related errors."""
    pass


class BinanceFuturesClient:
    """
    Manages communication with Binance Futures API.
    Handles order placement and response parsing.

    SAFETY: This client is configured for TESTNET by default.
    Production trading requires explicit ENVIRONMENT=production configuration.
    """

    def __init__(self):
        """Initialize Binance Futures API client with testnet or production configuration."""
        # Log environment
        env_msg = f"Initializing Binance Futures client with {ENVIRONMENT.upper()} environment"
        if ENVIRONMENT == "production":
            logger.warning(
                "🚨 PRODUCTION MODE ENABLED - REAL TRADES WILL BE EXECUTED 🚨")
        else:
            logger.info(f"✓ {env_msg} (testnet - safe to test)")

        # Initialize client with appropriate settings
        self.client = Client(
            api_key=API_KEY,
            api_secret=API_SECRET,
            testnet=USE_TESTNET
        )
        logger.info(
            f"Binance Futures client initialized with {'testnet' if USE_TESTNET else 'production'} endpoint")

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float = None,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """
        Place an order on Binance Futures Testnet.

        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            order_type: MARKET or LIMIT
            quantity: Order quantity
            price: Order price (required for LIMIT orders)
            time_in_force: Time in force (GTC, IOC, etc.)

        Returns:
            Order response from API

        Raises:
            APIError: If order placement fails
        """
        try:
            # Build order parameters
            params = {
                "symbol": symbol,
                "side": side.upper(),
                "type": order_type.upper(),
                "quantity": quantity,
            }

            # Add price for limit orders
            if order_type.upper() == "LIMIT":
                params["price"] = price
                params["timeInForce"] = time_in_force

            # Log request details
            logger.debug(f"Placing order with parameters: {params}")
            logger.info(
                f"Submitting {order_type} {side} order: {quantity} {symbol} @ {price or 'market price'}"
            )

            # Execute order using futures endpoint
            response = self.client.futures_create_order(**params)

            # Log successful response
            logger.info(
                f"Order placed successfully. Order ID: {response.get('orderId')}")

            return response

        except (BinanceAPIException, BinanceOrderException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException) as e:
            error_msg = f"Binance API Error ({e.status_code}): {e.message}"
            logger.error(error_msg, exc_info=True)
            raise APIError(error_msg) from e

        except BinanceRequestException as e:
            error_msg = f"Binance Request Error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise APIError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error during order placement: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise APIError(error_msg) from e

    def get_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Retrieve order details from API.

        Args:
            symbol: Trading pair
            order_id: Order ID

        Returns:
            Order details

        Raises:
            APIError: If request fails
        """
        try:
            logger.debug(
                f"Fetching order details: {symbol} order_id={order_id}")
            response = self.client.futures_get_order(
                symbol=symbol, orderId=order_id)
            logger.debug(
                f"Order details retrieved: {json.dumps(response, indent=2, default=str)}")
            return response

        except Exception as e:
            error_msg = f"Error retrieving order {order_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise APIError(error_msg) from e

    def get_account_info(self) -> Dict[str, Any]:
        """
        Retrieve account information.

        Returns:
            Account information

        Raises:
            APIError: If request fails
        """
        try:
            logger.debug("Fetching account information")
            response = self.client.futures_account()
            logger.debug(
                f"Account info retrieved: {json.dumps(response, indent=2, default=str)}")
            return response

        except Exception as e:
            error_msg = f"Error retrieving account information: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise APIError(error_msg) from e
