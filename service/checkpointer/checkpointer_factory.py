import logging
from langgraph.checkpoint.memory import MemorySaver
from service.config import Config

try:
    from langgraph.checkpoint.postgres import PostgresSaver
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


class CheckpointerFactory:
    """Factory class for creating appropriate checkpointer instances"""

    @staticmethod
    def create(config: Config):
        """Create checkpointer based on configuration"""
        checkpoint_type = config.checkpoint.type

        if checkpoint_type == "auto":
            # Auto mode: use debug flag to decide
            if config.app.debug:
                logging.info("Using MemorySaver (DEBUG mode)")
                return MemorySaver()
            else:
                logging.info("Using PostgresSaver (production mode)")
                return CheckpointerFactory._create_postgres_saver(config)
        elif checkpoint_type == "memory":
            logging.info("Using MemorySaver (configured)")
            return MemorySaver()
        elif checkpoint_type == "postgres":
            logging.info("Using PostgresSaver (configured)")
            return CheckpointerFactory._create_postgres_saver(config)
        else:
            logging.warning(f"Unknown checkpoint type: {checkpoint_type}, falling back to MemorySaver")
            return MemorySaver()

    @staticmethod
    def _create_postgres_saver(config: Config):
        """Create PostgresSaver or fallback to MemorySaver"""
        if not POSTGRES_AVAILABLE:
            logging.warning("PostgresSaver not available, falling back to MemorySaver")
            return MemorySaver()

        # Get connection string from config
        from service.config import ConfigLoader
        config_loader = ConfigLoader()
        config_loader.load()  # Ensure config is loaded
        connection_string = config_loader.get_postgres_connection_string()

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
    def is_postgres_available():
        """Check if PostgresSaver is available"""
        return POSTGRES_AVAILABLE

    @staticmethod
    def get_checkpointer_type(config: Config):
        """Get the type of checkpointer that would be created"""
        checkpoint_type = config.checkpoint.type

        if checkpoint_type == "auto":
            if config.app.debug:
                return "MemorySaver (debug)"
            elif POSTGRES_AVAILABLE:
                from service.config import ConfigLoader
                config_loader = ConfigLoader()
                config_loader.load()  # Ensure config is loaded
                if config_loader.get_postgres_connection_string():
                    return "PostgresSaver (auto)"
                else:
                    return "MemorySaver (fallback)"
            else:
                return "MemorySaver (postgres unavailable)"
        elif checkpoint_type == "memory":
            return "MemorySaver (configured)"
        elif checkpoint_type == "postgres":
            if POSTGRES_AVAILABLE:
                return "PostgresSaver (configured)"
            else:
                return "MemorySaver (postgres unavailable)"
        else:
            return "MemorySaver (unknown type)"
