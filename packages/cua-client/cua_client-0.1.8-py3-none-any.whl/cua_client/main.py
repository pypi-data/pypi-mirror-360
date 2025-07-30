# Configure logging with enhanced formatting and colors -> must be before any other imports
from cua_client.logging_config import setup_logging
setup_logging(level="DEBUG")  # You can change this to DEBUG for more verbose output

import logging
logger = logging.getLogger(__name__)

import argparse
import asyncio
import os
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError
from cua_client.remote_function_client import RemoteFunctionClient, RemoteFunctionRouter
from cua_client.computer_use import ComputerUseFunction


class ClientConfig(BaseModel):
    """Configuration model for the remote function client"""
    remote_function_url: str = Field(description="WebSocket server URL")
    agent_id: int = Field(description="The agent ID")
    secret_key: str = Field(description="The VM secret key")
    
    class Config:
        # Allow extra fields in case we add more config options later
        extra = "ignore"


def load_config() -> ClientConfig:
    """Load configuration from environment variables"""
    try:
        # Get values from environment variables
        secret_key = os.getenv("SECRET_KEY")
        remote_function_url = os.getenv("REMOTE_FUNCTION_URL")
        agent_id = os.getenv("AGENT_ID")
        
        if not remote_function_url:
            logger.error("REMOTE_FUNCTION_URL environment variable is required")
            raise ValueError("REMOTE_FUNCTION_URL environment variable is required")
        
        if not secret_key:
            logger.error("SECRET_KEY environment variable is required")
            raise ValueError("SECRET_KEY environment variable is required")
        
        if not agent_id:
            logger.error("AGENT_ID environment variable is required")
            raise ValueError("AGENT_ID environment variable is required")
        
        try:
            agent_id = int(agent_id)
        except ValueError:
            logger.error("AGENT_ID must be a valid integer")
            raise ValueError("AGENT_ID must be a valid integer")
        
        
        config = ClientConfig(
            secret_key=secret_key,
            remote_function_url=remote_function_url,
            agent_id=agent_id
        )
        logger.info(f"Loaded config from environment variables: secret_key=*****, remote_function_url={config.remote_function_url}, agent_id={config.agent_id}")
        return config
        
    except ValidationError as e:
        logger.error(f"Config validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise

# Create routers for different function categories
basic_router = RemoteFunctionRouter(tags=["basic"])

# Basic functions router (no prefix)
@basic_router.function("print")
def print_function(message: str = "Hello from client!") -> str:
    """Example function that prints a message and returns success"""
    logger.info(f"Print function called: {message}")
    return "Print executed successfully"


async def main():
    """Main function to run the remote function client"""
    
    # Load configuration from environment variables
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return
    
    logger.info(f"Starting Remote Function Client")
    logger.info(f"Remote Function URL: {config.remote_function_url}")
    logger.info(f"Agent ID: {config.agent_id}")
    logger.info(f"Secret Key: *****")
    logger.info("-" * 50)
    
    # Create and configure the client
    client = RemoteFunctionClient(config.remote_function_url, config.agent_id, config.secret_key)
    client.include_router(basic_router)
    client.register_function("computer_use", ComputerUseFunction())
    
    # Display all registered functions
    function_names = client.get_registered_function_names()
    logger.info(f"Available functions ({len(function_names)}):")
    for func_name in sorted(function_names):
        logger.info(f"  - {func_name}")
    
    logger.info("\nPress Ctrl+C to exit")
    logger.info("-" * 50)
    
    try:
        # Run the client
        await client.run()
    except KeyboardInterrupt:
        logger.info("\nClient interrupted by user")
    except Exception as e:
        logger.error(f"Client error: {e}")
    finally:
        logger.info("Client shutting down...")


def cli():
    """CLI entry point for the cua-client package"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nClient interrupted by user")
    except Exception as e:
        logger.error(f"Client error: {e}")


if __name__ == "__main__":
    cli()