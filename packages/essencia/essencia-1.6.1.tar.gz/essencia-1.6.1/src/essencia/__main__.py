"""Main entry point for Essencia application."""

import asyncio
import sys

from essencia.core.config import Config
from essencia.ui.app import EssenciaApp


def main():
    """Main function."""
    # Load configuration
    config = Config.from_env()
    
    # Create and run application
    app = EssenciaApp(config)
    app.run()


if __name__ == "__main__":
    main()