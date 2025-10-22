#!/usr/bin/env python3
"""
Quick launcher for Zefoy Bot
Usage: python run.py
"""

import sys

from zefoy_bot.main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")
        sys.exit(1)
