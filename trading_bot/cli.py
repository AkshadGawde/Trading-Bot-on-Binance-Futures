import sys
import argparse
from trading_bot.orders import OrderExecutor
from trading_bot.validation import ValidationError
from trading_bot.api_client import APIError, BinanceFuturesClient
from trading_bot.logging_config import get_logger
from trading_bot.config import ENVIRONMENT

logger = get_logger(__name__)


class TradingBotCLI:
    """
    CLI interface for trading bot.
    Manages argument parsing and command execution.
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
            '--symbol',
            required=True,
            help='Trading pair symbol (e.g., BTCUSDT, ETHUSDT)'
        )
        order_parser.add_argument(
            '--side',
            required=True,
            choices=['BUY', 'SELL'],
            help='Order side: BUY or SELL'
        )
        order_parser.add_argument(
            '--type',
            dest='order_type',
            required=True,
            choices=['MARKET', 'LIMIT'],
            help='Order type: MARKET or LIMIT'
        )
        order_parser.add_argument(
            '--quantity',
            required=True,
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
        Execute order based on CLI arguments.

        Args:
            args: Parsed command-line arguments
        """
        logger.info(
            f"Executing order: symbol={args.symbol}, side={args.side}, "
            f"type={args.order_type}, qty={args.quantity}, price={args.price}"
        )

        try:
            result = self.executor.execute_order(
                symbol=args.symbol,
                side=args.side,
                order_type=args.order_type,
                quantity=args.quantity,
                price=args.price
            )

            sys.exit(0)

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


def main():
    """Main entry point for CLI."""
    cli = TradingBotCLI()
    cli.run()


if __name__ == "__main__":
    main()
