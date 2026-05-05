"""Main entry point for SAS RAG Assistant"""

import argparse
import sys
from pathlib import Path

from src.core.logger import setup_logging, get_logger
from src.core.config import get_config

logger = get_logger(__name__)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="SAS RAG Assistant - RAG-powered SAS code reuse system"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # API command
    api_parser = subparsers.add_parser("api", help="Run FastAPI server")
    api_parser.add_argument("--host", default="0.0.0.0")
    api_parser.add_argument("--port", type=int, default=8000)
    api_parser.add_argument("--reload", action="store_true")
    
    # Web command
    web_parser = subparsers.add_parser("web", help="Run Streamlit web UI")
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest corpus")
    ingest_parser.add_argument("--corpus-path", help="Path to corpus")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    if args.command == "api":
        import uvicorn
        uvicorn.run(
            "src.api.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
        )
    elif args.command == "web":
        import subprocess
        subprocess.run(["streamlit", "run", "src/web/streamlit_app.py"])
    elif args.command == "ingest":
        from src.cli.cli import ingest
        ingest(args.corpus_path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
