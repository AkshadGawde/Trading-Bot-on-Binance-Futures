# Binance Futures Trading Bot

A CLI-based Python trading bot for executing **MARKET** and **LIMIT** orders on **Binance Futures Testnet (USDT-M)**.  
This project demonstrates clean architecture, input validation, structured logging, and safe API interaction.

---

## Features

- MARKET and LIMIT order execution
- BUY and SELL support
- Command-line interface (CLI)
- Input validation before API execution
- Structured logging of requests and responses
- Graceful error handling
- Testnet-only execution (no real funds)

---

## Quick Setup

### Prerequisites

- Python 3.8+
- Binance Futures Testnet account

---

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

---

### 2. Configure API Credentials

```bash
cp .env.example .env
```

Edit `.env` and add your Binance Futures Testnet credentials:

```
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
```

Create testnet credentials at:

https://testnet.binancefuture.com/

---

### 3. Verify Installation

```bash
python -m trading_bot --help
```

---

## Usage

### Place a MARKET Order

```bash
python -m trading_bot place-order   --symbol BTCUSDT   --side BUY   --type MARKET   --quantity 0.01
```

---

### Place a LIMIT Order

```bash
python -m trading_bot place-order   --symbol ETHUSDT   --side SELL   --type LIMIT   --quantity 0.5   --price 2000
```

---

### Health Check

```bash
python -m trading_bot health-check
```

---

## Project Structure

```
trading_bot/
├── api_client.py        # Binance API communication
├── orders.py            # Order execution logic
├── validation.py        # Input validation
├── logging_config.py    # Logging setup
├── cli.py               # CLI interface
└── __main__.py          # Entry point
```

---

## Logging

- Logs are written to the `logs/` directory
- Includes order requests, responses, and errors
- Designed for debugging and traceability

---

## Notes

- Uses **Binance Futures Testnet** only
- No real funds are used
- API credentials must not be committed to the repository

---

## Assumptions

- User has valid Binance Futures Testnet API credentials
- USDT-M futures contracts are used
- Network connectivity to Binance Testnet is available

---

## Purpose

This project was built as a technical assignment to demonstrate:

- API integration with external systems
- Modular Python application design
- Input validation and safe execution
- Logging and error handling practices
