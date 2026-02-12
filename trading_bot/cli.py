import sys
import argparse
from typing import Optional, Dict, Any
from trading_bot.orders import OrderExecutor
from trading_bot.validation import ValidationError, InputValidator
from trading_bot.api_client import APIError, BinanceFuturesClient
from trading_bot.logging_config import get_logger
from trading_bot.config import ENVIRONMENT

logger = get_logger(__name__)


class TradingBotCLI:
    """
    CLI interface for trading bot.
    Manages argument parsing and command execution.
    Supports both traditional command-line arguments and interactive mode.
    """

    def __init__(self):
        """Initialize CLI with argument parser."""
        self.executor = OrderExecutor()

    def run(self, args=None):
        """
        Main entry point for CLI execution.

        Args:
            args: Command-line arguments (defaults to sys.argv[1:])
        """
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)

        # Route to appropriate command
        if hasattr(parsed_args, 'func'):
            parsed_args.func(parsed_args)
        else:
            parser.print_help()

    def _create_parser(self) -> argparse.ArgumentParser:
        """
        Create and configure argument parser.

        Returns:
            Configured ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            description=f"Binance Futures Trading Bot - {ENVIRONMENT.upper()} Mode",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Interactive order mode (guided prompts)
  python -m trading_bot place-order-interactive
  
  # Check connection and account info
  python -m trading_bot health-check
  
  # Place a MARKET BUY order for 1 BTC
  python -m trading_bot place-order --symbol BTCUSDT --side BUY --type MARKET --quantity 1

  # Place a LIMIT SELL order for 10 ETH at price 2000
  python -m trading_bot place-order --symbol ETHUSDT --side SELL --type LIMIT --quantity 10 --price 2000
  
  # Get account info
  python -m trading_bot account-info
            """
        )

        # Create subparsers for different commands
        subparsers = parser.add_subparsers(
            dest='command', help='Available commands')

        # Health check command
        health_parser = subparsers.add_parser(
            'health-check', help='Check bot connection and testnet status')
        health_parser.set_defaults(func=self._health_check)

        # Account info command
        account_parser = subparsers.add_parser(
            'account-info', help='Get account information and balance')
        account_parser.set_defaults(func=self._account_info)

        # Place order command
        order_parser = subparsers.add_parser(
            'place-order', help='Place a new order')
        order_parser.add_argument(
            '--interactive',
            action='store_true',
            help='Use interactive guided mode with prompts (optional arguments)'
        )
        order_parser.add_argument(
            '--symbol',
            required=False,
            help='Trading pair symbol (e.g., BTCUSDT, ETHUSDT)'
        )
        order_parser.add_argument(
            '--side',
            required=False,
            choices=['BUY', 'SELL'],
            help='Order side: BUY or SELL'
        )
        order_parser.add_argument(
            '--type',
            dest='order_type',
            required=False,
            choices=['MARKET', 'LIMIT'],
            help='Order type: MARKET or LIMIT'
        )
        order_parser.add_argument(
            '--quantity',
            required=False,
            help='Order quantity (positive number)'
        )
        order_parser.add_argument(
            '--price',
            default=None,
            help='Order price (required for LIMIT orders)'
        )
        order_parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging output'
        )
        order_parser.set_defaults(func=self._execute_order)

        return parser

    def _health_check(self, args):
        """
        Health check to verify connection and account status.

        Args:
            args: Parsed command-line arguments
        """
        logger.info(
            f"Running health check on {ENVIRONMENT.upper()} environment...")

        try:
            client = BinanceFuturesClient()
            account_info = client.get_account_info()

            # Extract useful info
            total_wallet_balance = float(
                account_info.get('totalWalletBalance', 0))
            total_unrealized_profit = float(
                account_info.get('totalUnrealizedProfit', 0))

            print("\n" + "=" * 60)
            print(f"✓ Connected to {ENVIRONMENT.upper()} environment")
            print("=" * 60)
            print(f"Total Wallet Balance: {total_wallet_balance:.2f} USDT")
            print(
                f"Unrealized Profit/Loss: {total_unrealized_profit:.2f} USDT")
            print(f"Open Positions: {account_info.get('positions', [])}")
            print("=" * 60)
            print("✓ Health check passed!\n")
            logger.info("Health check completed successfully")
            sys.exit(0)

        except Exception as e:
            error_msg = f"❌ Health check failed: {str(e)}"
            print(f"\n{error_msg}\n")
            logger.error(f"Health check error: {str(e)}", exc_info=True)
            sys.exit(1)

    def _account_info(self, args):
        """
        Get and display account information.

        Args:
            args: Parsed command-line arguments
        """
        logger.info("Fetching account information...")

        try:
            client = BinanceFuturesClient()
            account_info = client.get_account_info()

            print("\n" + "=" * 60)
            print(f"Account Information ({ENVIRONMENT.upper()})")
            print("=" * 60)
            print(
                f"Total Wallet Balance: {account_info.get('totalWalletBalance', 0)} USDT")
            print(
                f"Available Balance: {account_info.get('availableBalance', 0)} USDT")
            print(
                f"Total Unrealized Profit: {account_info.get('totalUnrealizedProfit', 0)} USDT")
            print("=" * 60 + "\n")
            logger.info("Account info retrieved successfully")
            sys.exit(0)

        except Exception as e:
            error_msg = f"❌ Failed to fetch account info: {str(e)}"
            print(f"\n{error_msg}\n")
            logger.error(f"Account info error: {str(e)}", exc_info=True)
            sys.exit(1)

    def _execute_order(self, args):
        """
        Execute order either through traditional arguments or interactive mode.

        Args:
            args: Parsed command-line arguments
        """
        try:
            # Check if interactive mode is enabled
            if getattr(args, 'interactive', False):
                self._execute_order_interactive_mode(args)
            else:
                self._execute_order_traditional_mode(args)

        except ValidationError as e:
            error_msg = f"❌ Validation Error: {str(e)}"
            print(f"\n{error_msg}\n")
            logger.error(f"Validation error: {str(e)}")
            sys.exit(1)

        except APIError as e:
            error_msg = f"❌ API Error: {str(e)}"
            print(f"\n{error_msg}\n")
            logger.error(f"API error: {str(e)}")
            sys.exit(1)

        except Exception as e:
            error_msg = f"❌ Unexpected Error: {str(e)}"
            print(f"\n{error_msg}\n")
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            sys.exit(1)

    def _execute_order_traditional_mode(self, args):
        """
        Execute order using traditional command-line arguments.

        Args:
            args: Parsed command-line arguments
        """
        # Validate that all required arguments are provided
        if not args.symbol or not args.side or not args.order_type or not args.quantity:
            print(
                "\n❌ Error: --symbol, --side, --type, and --quantity are required for traditional mode\n")
            print("Use --interactive flag for guided mode:")
            print("  python -m trading_bot place-order --interactive\n")
            logger.error("Missing required arguments in traditional mode")
            sys.exit(1)

        logger.info(
            f"Executing order: symbol={args.symbol}, side={args.side}, "
            f"type={args.order_type}, qty={args.quantity}, price={args.price}"
        )

        result = self.executor.execute_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price
        )

        sys.exit(0)

    def _execute_order_interactive_mode(self, args):
        """
        Execute order using interactive guided mode with prompts and confirmation.

        Args:
            args: Parsed command-line arguments
        """
        logger.info("Starting interactive order mode")

        # Gather order details through interactive prompts
        order_params = self._prompt_for_order_details()

        # Validate inputs using existing validation layer
        InputValidator.validate_all(
            symbol=order_params['symbol'],
            side=order_params['side'],
            order_type=order_params['order_type'],
            quantity=order_params['quantity'],
            price=order_params['price']
        )

        # Display order summary for confirmation
        self._display_order_summary(order_params)

        # Ask for confirmation before execution
        if not self._confirm_order_execution():
            print("\n⚠️  Order cancelled by user.\n")
            logger.info("Order cancelled at user confirmation step")
            sys.exit(0)

        # Execute the order using existing order executor
        logger.info(
            f"Executing interactive order: symbol={order_params['symbol']}, "
            f"side={order_params['side']}, type={order_params['order_type']}, "
            f"qty={order_params['quantity']}, price={order_params['price']}"
        )

        result = self.executor.execute_order(
            symbol=order_params['symbol'],
            side=order_params['side'],
            order_type=order_params['order_type'],
            quantity=order_params['quantity'],
            price=order_params['price']
        )

        sys.exit(0)

    def _prompt_for_order_details(self) -> Dict[str, Optional[str]]:
        """
        Interactively prompt user for order details step-by-step.

        Returns:
            Dictionary with symbol, side, order_type, quantity, and price
        """
        self._print_section_header("ORDER ENTRY")

        # Prompt for symbol
        symbol = self._prompt_for_input(
            "Enter Symbol (e.g., BTCUSDT): ",
            validate_fn=lambda x: self._validate_and_normalize_symbol(x)
        )

        # Prompt for side
        side = self._prompt_for_choice(
            "Select Order Side:",
            ["BUY", "SELL"]
        )

        # Prompt for order type
        order_type = self._prompt_for_choice(
            "Select Order Type:",
            ["MARKET", "LIMIT"]
        )

        # Prompt for quantity
        quantity = self._prompt_for_input(
            "Enter Quantity: ",
            validate_fn=lambda x: self._validate_numeric_input(x, "Quantity")
        )

        # Prompt for price (only if LIMIT order)
        price = None
        if order_type.upper() == "LIMIT":
            price = self._prompt_for_input(
                "Enter Price: ",
                validate_fn=lambda x: self._validate_numeric_input(x, "Price")
            )

        return {
            'symbol': symbol,
            'side': side,
            'order_type': order_type,
            'quantity': quantity,
            'price': price
        }

    def _prompt_for_input(
        self,
        prompt: str,
        validate_fn=None
    ) -> str:
        """
        Prompt user for input with optional validation.

        Args:
            prompt: Display prompt message
            validate_fn: Optional validation function that raises ValueError on invalid input

        Returns:
            User input after validation
        """
        while True:
            try:
                user_input = input(prompt).strip()
                if not user_input:
                    print("❌ Input cannot be empty. Please try again.")
                    continue

                if validate_fn:
                    return validate_fn(user_input)
                return user_input

            except ValueError as e:
                print(f"❌ {str(e)} Please try again.")
                continue

    def _prompt_for_choice(self, prompt: str, options: list) -> str:
        """
        Prompt user to select from a list of options.

        Args:
            prompt: Display prompt message
            options: List of available options

        Returns:
            Selected option
        """
        print(f"\n{prompt}")
        for idx, option in enumerate(options, 1):
            print(f"  {idx}. {option}")

        while True:
            try:
                choice = input("Enter choice (number): ").strip()
                choice_idx = int(choice) - 1

                if 0 <= choice_idx < len(options):
                    return options[choice_idx]
                else:
                    print(
                        f"❌ Invalid choice. Please enter a number between 1 and {len(options)}.")
                    continue
            except ValueError:
                print(f"❌ Please enter a valid number.")
                continue

    def _validate_and_normalize_symbol(self, symbol: str) -> str:
        """
        Validate and normalize symbol format.

        Args:
            symbol: User input for symbol

        Raises:
            ValueError: If symbol format is invalid

        Returns:
            Normalized symbol
        """
        symbol_upper = symbol.upper().strip()
        if not symbol_upper.endswith("USDT"):
            raise ValueError(
                f"Symbol must end with 'USDT' (e.g., BTCUSDT). Got: {symbol}")

        if not symbol_upper[:-4].isalpha():
            raise ValueError(
                f"Symbol format invalid: {symbol}")

        return symbol_upper

    def _validate_numeric_input(self, value: str, field_name: str) -> str:
        """
        Validate numeric input.

        Args:
            value: User input
            field_name: Name of field being validated (for error message)

        Raises:
            ValueError: If input is not a valid positive number

        Returns:
            Validated numeric string
        """
        try:
            num = float(value)
            if num <= 0:
                raise ValueError(
                    f"{field_name} must be positive, got: {num}")
            return str(num)
        except ValueError as e:
            if "positive" in str(e):
                raise
            raise ValueError(
                f"{field_name} must be numeric, got: '{value}'")

    def _display_order_summary(self, order_params: Dict[str, Optional[str]]) -> None:
        """
        Display formatted order summary for user review.

        Args:
            order_params: Dictionary with order parameters
        """
        self._print_section_header("ORDER SUMMARY")

        print(f"Symbol:       {order_params['symbol']}")
        print(f"Side:         {order_params['side']}")
        print(f"Type:         {order_params['order_type']}")
        print(f"Quantity:     {order_params['quantity']}")

        if order_params['order_type'].upper() == "LIMIT":
            print(f"Price:        {order_params['price']}")
        else:
            print(f"Price:        Market Price")

        self._print_section_footer()

    def _confirm_order_execution(self) -> bool:
        """
        Ask user to confirm order execution.

        Returns:
            True if user confirms, False otherwise
        """
        while True:
            confirmation = input(
                "Confirm order execution? (y/n): ").strip().lower()
            if confirmation in ['y', 'yes']:
                return True
            elif confirmation in ['n', 'no']:
                return False
            else:
                print("❌ Please enter 'y' or 'n'.")

    def _print_section_header(self, title: str) -> None:
        """
        Print a formatted section header.

        Args:
            title: Section title
        """
        print("\n" + "=" * 60)
        print(f"{title:^60}")
        print("=" * 60)

    def _print_section_footer(self) -> None:
        """Print a formatted section footer."""
        print("=" * 60 + "\n")


def main():
    """Main entry point for CLI."""
    cli = TradingBotCLI()
    cli.run()


if __name__ == "__main__":
    main()
