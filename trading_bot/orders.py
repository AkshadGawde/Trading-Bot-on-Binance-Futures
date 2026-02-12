"""
Order execution layer for managing order flow logic.
Orchestrates validation, API calls, and response handling.
"""

from typing import Dict, Any
from trading_bot.api_client import BinanceFuturesClient, APIError
from trading_bot.validation import InputValidator, ValidationError
from trading_bot.logging_config import get_logger

logger = get_logger(__name__)


class OrderExecutor:
    """
    Manages the complete order execution workflow.
    Coordinates validation, API interaction, and result handling.
    """

    def __init__(self):
        """Initialize order executor with API client."""
        self.api_client = BinanceFuturesClient()

    def execute_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: str = None
    ) -> Dict[str, Any]:
        """
        Execute a complete order workflow: validate, summarize, place, report.

        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: Order side (BUY/SELL)
            order_type: Order type (MARKET/LIMIT)
            quantity: Order quantity
            price: Order price (required for LIMIT)

        Returns:
            Order result dictionary with status and details

        Raises:
            ValidationError: If validation fails
            APIError: If order placement fails
        """
        # Step 1: Validate all inputs
        try:
            InputValidator.validate_all(
                symbol, side, order_type, quantity, price)
        except ValidationError as e:
            logger.error(f"Validation failed: {str(e)}")
            raise

        # Step 2: Generate order summary
        summary = self._generate_order_summary(
            symbol, side, order_type, quantity, price)
        self._print_order_summary(summary)

        # Step 3: Prepare parameters
        qty_float = float(quantity)
        price_float = float(price) if price else None

        # Step 4: Execute order
        try:
            response = self.api_client.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=qty_float,
                price=price_float
            )
        except APIError as e:
            logger.error(f"Order execution failed: {str(e)}")
            raise

        # Step 5: Parse and return result
        result = self._parse_order_response(response)
        return result

    def _generate_order_summary(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: str
    ) -> Dict[str, str]:
        """
        Generate a summary of order details for display.

        Args:
            symbol: Trading pair
            side: Order side
            order_type: Order type
            quantity: Order quantity
            price: Order price

        Returns:
            Dictionary with formatted order summary
        """
        summary = {
            "symbol": symbol,
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": quantity,
        }

        if order_type.upper() == "LIMIT":
            summary["price"] = price
        else:
            summary["price"] = "Market Price"

        return summary

    @staticmethod
    def _print_order_summary(summary: Dict[str, str]) -> None:
        """
        Print formatted order summary to console.

        Args:
            summary: Order summary dictionary
        """
        print("\n" + "="*60)
        print("ORDER SUMMARY")
        print("="*60)
        for key, value in summary.items():
            print(f"{key.upper():.<20} {value}")
        print("="*60 + "\n")

        logger.info(f"Order summary displayed: {summary}")

    @staticmethod
    def _parse_order_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse API response and extract relevant order details.

        Args:
            response: Raw API response

        Returns:
            Parsed order result
        """
        result = {
            "success": True,
            "orderId": response.get("orderId"),
            "symbol": response.get("symbol"),
            "side": response.get("side"),
            "type": response.get("type"),
            "quantity": response.get("origQty"),
            "price": response.get("price"),
            "status": response.get("status"),
            "executedQuantity": response.get("executedQty"),
            "timestamp": response.get("updateTime"),
        }

        # Print success message
        print("\n" + "✓ "*30)
        print(f"Order placed successfully!")
        print(f"Order ID: {result['orderId']}")
        print(f"Status: {result['status']}")
        print(
            f"Executed Quantity: {result['executedQuantity']} {result['symbol']}")
        print("✓ "*30 + "\n")

        logger.info(
            f"Order execution completed: Order ID {result['orderId']}, Status: {result['status']}")
        return result
