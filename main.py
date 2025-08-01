from tool import mcp
import logging
import sys

# Logger Setup mit erweiterter Konfiguration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("Starting MCP server...")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise