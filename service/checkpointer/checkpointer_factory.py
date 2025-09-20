import os
import logging
from langgraph.checkpoint.memory import MemorySaver

try:
    from langgraph.checkpoint.postgres import PostgresSaver
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


class CheckpointerFactory:
    """Factory class for creating appropriate checkpointer instances"""

    @staticmethod
    def create(debug_mode):
        if debug_mode:
            logging.info("Using MemorySaver (DEBUG mode)")
            return MemorySaver()
        else:
            logging.info("Using PostgresSaver (NON DEBUG mode)")
            return CheckpointerFactory._create_postgres_saver()

    @staticmethod
    def _create_postgres_saver():
        """Create PostgresSaver or fallback to MemorySaver"""
        if not POSTGRES_AVAILABLE:
            logging.warning("PostgresSaver not available, falling back to MemorySaver")
            return MemorySaver()

        # Production mode - use PostgreSQL
        connection_string = os.getenv('POSTGRES_CONNECTION_STRING')
        if not connection_string:
            connection_string = CheckpointerFactory._build_connection_string()

        if not connection_string:
            logging.warning("PostgreSQL configuration incomplete, falling back to MemorySaver")
            return MemorySaver()

        try:
            logging.info("Using PostgresSaver (production mode)")
            return PostgresSaver.from_conn_string(connection_string) # type: ignore
        except Exception as e:
            logging.error(f"Failed to connect to PostgreSQL: {e}, falling back to MemorySaver")
            return MemorySaver()

    @staticmethod
    def _build_connection_string():
        """Build PostgreSQL connection string from individual environment variables"""
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        db = os.getenv('POSTGRES_DB', 'langgraph')
        user = os.getenv('POSTGRES_USER', 'postgres')
        password = os.getenv('POSTGRES_PASSWORD')

        if not password:
            logging.warning("POSTGRES_PASSWORD not provided")
            return None

        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

    @staticmethod
    def is_postgres_available():
        """Check if PostgresSaver is available"""
        return POSTGRES_AVAILABLE

    @staticmethod
    def get_checkpointer_type():
        """Get the type of checkpointer that would be created"""
        debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'

        if debug_mode:
            return "MemorySaver"
        elif POSTGRES_AVAILABLE and CheckpointerFactory._build_connection_string():
            return "PostgresSaver"
        else:
            return "MemorySaver (fallback)"
