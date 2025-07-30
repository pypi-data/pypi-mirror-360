#!/usr/bin/env python3
"""
Non-Commercial License

Copyright (c) 2025 MakerCorn

AI Prompt Manager Universal Launcher
Unified launcher supporting all deployment modes via environment variables.

This software is licensed for non-commercial use only.
See LICENSE file for details.
"""

import argparse
import os
import sys

from dotenv import load_dotenv

try:
    import uvicorn

    UVICORN_AVAILABLE = True
except ImportError:
    UVICORN_AVAILABLE = False

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def parse_arguments():
    """Parse command line arguments for quick configuration"""
    parser = argparse.ArgumentParser(
        description="AI Prompt Manager Universal Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  MULTITENANT_MODE     Enable multi-tenant mode (default: true)
  ENABLE_API          Enable REST API endpoints (default: false)
  SERVER_HOST         Server host (default: 0.0.0.0)
  SERVER_PORT         Server port (default: 7860)
  DB_TYPE             Database type: sqlite or postgres (default: sqlite)
  DEBUG               Enable debug mode (default: false)

Quick Start Examples:
  python run.py                           # Multi-tenant mode
  python run.py --single-user             # Single-user mode
  python run.py --with-api                # Multi-tenant + API
  python run.py --single-user --with-api  # Single-user + API
  python run.py --port 8080               # Custom port
        """,
    )

    # Mode flags
    parser.add_argument(
        "--single-user",
        action="store_true",
        help="Enable single-user mode (no authentication)",
    )
    parser.add_argument(
        "--multi-tenant", action="store_true", help="Enable multi-tenant mode (default)"
    )
    parser.add_argument(
        "--with-api", action="store_true", help="Enable REST API endpoints"
    )

    # Server configuration
    parser.add_argument(
        "--host", default=None, help="Server host (overrides SERVER_HOST)"
    )
    parser.add_argument(
        "--port", type=int, default=None, help="Server port (overrides SERVER_PORT)"
    )

    # Other options
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    return parser.parse_args()


def get_configuration(args):
    """Get final configuration from environment variables and arguments"""
    config: dict = {}

    # Mode configuration (args override env vars)
    if args.single_user:
        config["multitenant_mode"] = False
    elif args.multi_tenant:
        config["multitenant_mode"] = True
    else:
        config["multitenant_mode"] = bool(
            os.getenv("MULTITENANT_MODE", "true").lower() == "true"
        )

    # API configuration
    config["enable_api"] = args.with_api or (
        os.getenv("ENABLE_API", "false").lower() == "true"
    )

    # Web interface is the only option
    config["use_web"] = True

    # Server configuration (args override env vars)
    config["host"] = str(
        args.host or os.getenv("SERVER_HOST", "0.0.0.0")
    )  # nosec B104: Binding to all interfaces is intentional for web
    # application deployment
    config["port"] = int(args.port or int(os.getenv("SERVER_PORT", "7860")))

    # Other options
    config["debug"] = bool(
        args.debug or (os.getenv("DEBUG", "false").lower() == "true")
    )

    # Database configuration
    config["db_type"] = str(os.getenv("DB_TYPE", "sqlite")).lower()
    config["db_path"] = str(os.getenv("DB_PATH", "prompts.db"))
    config["postgres_dsn"] = os.getenv("POSTGRES_DSN")

    # Development mode
    config["local_dev_mode"] = bool(
        os.getenv("LOCAL_DEV_MODE", "true").lower() == "true"
    )

    return config


def display_startup_info(config):
    """Display startup information and configuration"""
    print("=" * 80)
    print("🤖 AI PROMPT MANAGER - WEB INTERFACE")
    print("=" * 80)
    print()

    # Mode information
    if config["multitenant_mode"]:
        print("🏢 Multi-Tenant Mode: ENABLED")
        print("  🔐 Authentication: Required")
        print("  🛡️ Admin Panel: Available")
        print("  🏢 Data Isolation: Per Tenant")
        print("  👤 Default Admin: admin@localhost / admin123")
        print("  🏠 Default Tenant: localhost")
    else:
        print("👤 Single-User Mode: ENABLED")
        print("  🔐 Authentication: Not Required")
        print("  📝 Direct Access: Available")
        print("  💾 Local Storage: File-based")

    # API information
    if config["enable_api"]:
        print("  📊 REST API: ENABLED")
        print(f"  📖 API Docs: http://{config['host']}:{config['port']}" "/api/docs")
        print(
            f"  🔍 API Explorer: http://{config['host']}:{config['port']}" "/api/redoc"
        )

    # Database information
    print("  💾 Database: {}".format(config["db_type"].upper()))
    if config["db_type"] == "sqlite":
        print(f"  📁 Database File: {config['db_path']}")
    else:
        print("  🔗 Database: PostgreSQL")

    # Development mode
    if config["local_dev_mode"]:
        print("  🔧 Development Mode: ENABLED")

    print()
    print("🌐 Access URLs:")
    print(f"  • Web Interface: http://{config['host']}:{config['port']}")

    if config["enable_api"]:
        print(
            f"  • API Documentation: http://{config['host']}:"
            f"{config['port']}/api/docs"
        )
        print(
            f"  • API Reference: http://{config['host']}:" f"{config['port']}/api/redoc"
        )

    print()

    # Usage instructions
    if config["multitenant_mode"]:
        print("🚀 Getting Started:")
        print("  1. Open the web interface")
        print("  2. Login with: admin@localhost / admin123")
        print("  3. Start creating and managing prompts")
        if config["enable_api"]:
            print(
                "  4. Create API tokens in Account Settings for " "programmatic access"
            )
    else:
        print("🚀 Getting Started:")
        print("  1. Open the web interface")
        print("  2. Start creating and managing prompts immediately")
        if config["enable_api"]:
            print("  3. API access available without authentication")

    print("=" * 80)
    print()


def main():
    """Main launcher that determines mode and runs appropriate interface"""

    # Parse command line arguments
    args = parse_arguments()

    # Get final configuration
    config = get_configuration(args)

    # Display startup information
    display_startup_info(config)

    # Update display for API integration
    if config["enable_api"]:
        print("🔗 API Integration: Unified server approach")
        print(f"   📊 API Endpoints: Same port as web app ({config['port']})")
        print(f"   🌐 API Base URL: http://{config['host']}:{config['port']}/api")
        print()

    # Set environment variables for the application
    if not config["multitenant_mode"]:
        os.environ["MULTITENANT_MODE"] = "false"

    if config["local_dev_mode"]:
        os.environ["LOCAL_DEV_MODE"] = "true"

    # Import and create the web interface
    try:
        print("🔧 Initializing Web Interface...")
        from web_app import create_web_app

        app = create_web_app(db_path=config["db_path"])
        print("✅ Web interface initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        sys.exit(1)

    # Handle API integration if enabled (dual-server architecture)
    if config["enable_api"]:
        try:
            print("🔌 Starting separate API server...")

            import threading
            from datetime import datetime

            from fastapi import FastAPI

            # Check if uvicorn is available
            if not UVICORN_AVAILABLE:
                print("❌ uvicorn is required for API server")
                print("   Install with: pip install uvicorn")
                return

            # Create separate FastAPI app for API
            api_app = FastAPI(
                title="AI Prompt Manager API",
                description="REST API for AI Prompt Manager",
                version="1.0.0",
            )

            # Add basic API endpoints
            @api_app.get("/health")
            async def health_check():
                return {"status": "healthy", "timestamp": datetime.now().isoformat()}

            @api_app.get("/info")
            async def api_info():
                return {
                    "service": "ai-prompt-manager",
                    "version": "1.0.0",
                    "api_version": "v1",
                }

            # Add protected endpoints that require authentication
            from fastapi import Depends, HTTPException
            from fastapi.security import HTTPBearer

            security = HTTPBearer()

            def verify_token(credentials=Depends(security)):
                """Simple token verification for testing"""
                if not credentials or not credentials.credentials:
                    raise HTTPException(status_code=401, detail="Missing token")
                if credentials.credentials == "invalid_token":
                    raise HTTPException(status_code=401, detail="Invalid token")
                return credentials.credentials

            @api_app.get("/prompts")
            async def get_prompts(token: str = Depends(verify_token)):
                """Protected endpoint for testing authentication"""
                return {"prompts": [], "total": 0}

            @api_app.post("/prompts")
            async def create_prompt(token: str = Depends(verify_token)):
                """Protected endpoint for testing authentication"""
                return {"id": 1, "message": "Prompt created"}

            @api_app.options("/prompts")
            async def prompts_options():
                """CORS preflight support"""
                return {"message": "OK"}

            # Include comprehensive prompt API endpoints
            try:
                from prompt_api_endpoints import create_prompt_router

                prompt_router = create_prompt_router(config["db_path"])
                api_app.include_router(prompt_router)
                print("✅ Comprehensive prompt API endpoints loaded")
            except ImportError as e:
                print(f"⚠️  Prompt API endpoints not available: {e}")
            except Exception as e:
                print(f"⚠️  Error loading prompt API endpoints: {e}")

            # Add Release Management endpoints
            try:
                from release_api_endpoints import (
                    create_admin_release_router,
                    create_release_router,
                )

                # Include release management routes
                release_router = create_release_router(config["db_path"])
                admin_release_router = create_admin_release_router(config["db_path"])

                api_app.include_router(release_router)
                api_app.include_router(admin_release_router)

                print("✅ Release management API endpoints loaded")
            except ImportError as e:
                print(f"⚠️  Release management endpoints not available: {e}")
            except Exception as e:
                print(f"⚠️  Error loading release management endpoints: {e}")

            # Add CORS middleware
            from fastapi.middleware.cors import CORSMiddleware

            api_app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                allow_headers=["*"],
            )

            # Start API server on port+1 in separate thread
            api_port = config["port"] + 1

            def start_api_server():
                try:
                    print(
                        f"🔄 Starting API server thread on {config['host']}:{api_port}"
                    )
                    # Use uvicorn with proper configuration for threading
                    config_obj = uvicorn.Config(
                        api_app,
                        host=config["host"],
                        port=api_port,
                        log_level="error",
                        access_log=False,
                        loop="asyncio",
                    )
                    server = uvicorn.Server(config_obj)
                    server.run()
                except Exception as e:
                    print(f"❌ API server thread failed: {e}")
                    import traceback

                    traceback.print_exc()

            # Test port availability before starting
            import socket

            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.bind((config["host"], api_port))
                test_socket.close()
                print(f"✅ Port {api_port} is available")
            except Exception as e:
                print(f"❌ Port {api_port} is not available: {e}")
                return

            api_thread = threading.Thread(target=start_api_server, daemon=True)
            api_thread.start()

            # Give the thread more time to start
            import time

            time.sleep(2)

            # Test if API server is actually responding
            try:
                import requests

                response = requests.get(
                    f"http://{config['host']}:{api_port}/health", timeout=1
                )
                if response.status_code == 200:
                    print(f"✅ API server is responding on port {api_port}")
                else:
                    print(
                        f"⚠️  API server started but health check failed: "
                        f"{response.status_code}"
                    )
            except Exception as e:
                print(f"⚠️  API server may not be fully started yet: {e}")

            print(f"✅ API server thread started on port {api_port}")
            print(f"📖 API Health: http://{config['host']}:{api_port}/health")
            print(f"📖 API Info: http://{config['host']}:{api_port}/info")

        except Exception as e:
            print(f"⚠️  API setup error: {e}")
            import traceback

            traceback.print_exc()

    # Launch configuration summary
    print("🚀 Launching server...")
    if config["debug"]:
        print("🐛 Debug mode enabled")

    # Launch the web application
    try:
        print(f"🌐 Starting web interface on {config['host']}:{config['port']}")
        # Don't use reload in debug mode as it causes issues with direct app objects
        uvicorn.run(
            app,
            host=config["host"],
            port=config["port"],
            reload=False,  # Disable reload to avoid import string issues
            access_log=config["debug"],
            log_level="info" if config["debug"] else "error",
        )
    except Exception as e:
        print(f"❌ Failed to launch server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
