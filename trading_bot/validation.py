"""
Validation layer for input verification and sanity checks.
Ensures all user inputs meet requirements before order execution.
"""

import re
from typing import Tuple
from trading_bot.config import ALLOWED_ORDER_SIDES, ALLOWED_ORDER_TYPES
from trading_bot.logging_config import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


class InputValidator:
    """Validates all trading inputs according to specification."""

    # Binance symbol format: uppercase letters followed by underscore and uppercase
    SYMBOL_PATTERN = re.compile(r"^[A-Z]+USDT$")

    @staticmethod
    def validate_symbol(symbol: str) -> None:
        """
        Validate trading symbol format.

        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)

        Raises:
            ValidationError: If symbol is invalid
        """
        if not symbol:
            raise ValidationError("Symbol cannot be empty")

        if not isinstance(symbol, str):
            raise ValidationError("Symbol must be a string")

        if not InputValidator.SYMBOL_PATTERN.match(symbol):
            raise ValidationError(
                f"Invalid symbol format: '{symbol}'. "
                "Expected format: XXXUSDT (e.g., BTCUSDT, ETHUSDT)"
            )

        logger.debug(f"Symbol validation passed: {symbol}")

    @staticmethod
    def validate_side(side: str) -> None:
        """
        Validate order side (BUY or SELL).

        Args:
            side: Order side

        Raises:
            ValidationError: If side is invalid
        """
        if not side:
            raise ValidationError("Side cannot be empty")

        if not isinstance(side, str):
            raise ValidationError("Side must be a string")

        side_upper = side.upper()
        if side_upper not in ALLOWED_ORDER_SIDES:
            raise ValidationError(
                f"Invalid side: '{side}'. Allowed values: {', '.join(ALLOWED_ORDER_SIDES)}"
            )

        logger.debug(f"Side validation passed: {side_upper}")

    @staticmethod
    def validate_order_type(order_type: str) -> None:
        """
        Validate order type (MARKET or LIMIT).

        Args:
            order_type: Order type

        Raises:
            ValidationError: If order type is invalid
        """
        if not order_type:
            raise ValidationError("Order type cannot be empty")

        if not isinstance(order_type, str):
            raise ValidationError("Order type must be a string")

        order_type_upper = order_type.upper()
        if order_type_upper not in ALLOWED_ORDER_TYPES:
            raise ValidationError(
                f"Invalid order type: '{order_type}'. "
                f"Allowed values: {', '.join(ALLOWED_ORDER_TYPES)}"
            )

        logger.debug(f"Order type validation passed: {order_type_upper}")

    @staticmethod
    def validate_quantity(quantity: str) -> None:
        """
        Validate order quantity is positive numeric value.

        Args:
            quantity: Order quantity as string

        Raises:
            ValidationError: If quantity is invalid
        """
        if not quantity:
            raise ValidationError("Quantity cannot be empty")

        try:
            qty_float = float(quantity)
        except ValueError:
            raise ValidationError(
                f"Quantity must be numeric, got: '{quantity}'")

        if qty_float <= 0:
            raise ValidationError(
                f"Quantity must be positive, got: {qty_float}")

        logger.debug(f"Quantity validation passed: {qty_float}")

    @staticmethod
    def validate_price(price: str, order_type: str) -> None:
        """
        Validate price based on order type.
        Price is required for LIMIT orders, forbidden for MARKET orders.

        Args:
            price: Order price as string (or None for market orders)
            order_type: Order type (MARKET or LIMIT)

        Raises:
            ValidationError: If price validation fails
        """
        order_type_upper = order_type.upper()

        if order_type_upper == "LIMIT":
            if not price:
                raise ValidationError("Price is required for LIMIT orders")

            try:
                price_float = float(price)
            except ValueError:
                raise ValidationError(f"Price must be numeric, got: '{price}'")

            if price_float <= 0:
                raise ValidationError(
                    f"Price must be positive, got: {price_float}")

            logger.debug(
                f"Price validation passed for LIMIT order: {price_float}")

        elif order_type_upper == "MARKET":
            if price:
                logger.warning("Price ignored for MARKET orders")

    @staticmethod
    def validate_all(
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: str = None
    ) -> None:
        """
        Validate all input parameters together.

        Args:
            symbol: Trading pair symbol
            side: Order side (BUY/SELL)
            order_type: Order type (MARKET/LIMIT)
            quantity: Order quantity
            price: Order price (optional, required for LIMIT)

        Raises:
            ValidationError: If any validation fails
        """
        InputValidator.validate_symbol(symbol)
        InputValidator.validate_side(side)
        InputValidator.validate_order_type(order_type)
        InputValidator.validate_quantity(quantity)
        InputValidator.validate_price(price, order_type)

        logger.info(
            f"All validations passed: symbol={symbol}, side={side}, "
            f"type={order_type}, qty={quantity}, price={price}"
        )
