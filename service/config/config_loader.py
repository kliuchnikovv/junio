import os
import yaml
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class AppConfig:
    name: str = "langgraph-agent"
    version: str = "1.0.0"
    debug: bool = True
    port: int = 3000


@dataclass
class ModelConfig:
    provider: str = "google"
    name: str = "gemini-2.0-flash"
    api_key_env: str = "GOOGLE_API_KEY"
    parameters: Dict[str, Any] = field(default_factory=lambda: {
        "temperature": 0.7,
        "max_tokens": 1000
    })


@dataclass
class PostgresConfig:
    host: str = "localhost"
    port: int = 5432
    database: str = "langgraph"
    user: str = "postgres"
    password_env: str = "POSTGRES_PASSWORD"
    connection_string_env: str = "POSTGRES_CONNECTION_STRING"
    pool_size: int = 10
    max_overflow: int = 20


@dataclass
class CheckpointConfig:
    type: str = "auto"  # auto, memory, postgres
    postgres: PostgresConfig = field(default_factory=PostgresConfig)


@dataclass
class APIConfig:
    endpoints: Dict[str, str] = field(default_factory=lambda: {
        "message": "/message",
        "health": "/health"
    })
    cors: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": False,
        "origins": ["*"]
    })


@dataclass
class ToolsConfig:
    enabled: list = field(default_factory=list)
    # Dynamic tool configurations will be added here


@dataclass
class LoggingConfig:
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None


@dataclass
class GraphNodeConfig:
    enabled: bool = True
    log_messages: bool = False
    log_completion: bool = False
    timeout: int = 30


@dataclass
class GraphConfig:
    nodes: Dict[str, GraphNodeConfig] = field(default_factory=lambda: {
        "start": GraphNodeConfig(enabled=True, log_messages=True),
        "agent": GraphNodeConfig(enabled=True, timeout=30),
        "end": GraphNodeConfig(enabled=True, log_completion=True)
    })


@dataclass
class Config:
    app: AppConfig = field(default_factory=AppConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    checkpoint: CheckpointConfig = field(default_factory=CheckpointConfig)
    api: APIConfig = field(default_factory=APIConfig)
    tools: ToolsConfig = field(default_factory=ToolsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    graph: GraphConfig = field(default_factory=GraphConfig)


class ConfigLoader:
    """Configuration loader with environment variable override support"""

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self._config: Optional[Config] = None

    def load(self) -> Config:
        """Load configuration from YAML file with environment overrides"""
        if self._config is not None:
            return self._config

        # Load from YAML file
        config_data = self._load_yaml()

        # Create config object
        self._config = self._create_config(config_data)

        # Apply environment variable overrides
        self._apply_env_overrides()

        logging.info(f"Configuration loaded from {self.config_path}")
        return self._config

    def _load_yaml(self) -> Dict[str, Any]:
        """Load YAML configuration file"""
        if not os.path.exists(self.config_path):
            logging.warning(f"Config file {self.config_path} not found, using defaults")
            return {}

        try:
            with open(self.config_path, 'r') as file:
                return yaml.safe_load(file) or {}
        except Exception as e:
            logging.error(f"Error loading config file {self.config_path}: {e}")
            return {}

    def _create_config(self, data: Dict[str, Any]) -> Config:
        """Create Config object from loaded data"""
        config = Config()

        # Load app config
        if 'app' in data:
            app_data = data['app']
            config.app = AppConfig(
                name=app_data.get('name', config.app.name),
                version=app_data.get('version', config.app.version),
                debug=app_data.get('debug', config.app.debug),
                port=app_data.get('port', config.app.port)
            )

        # Load model config
        if 'model' in data:
            model_data = data['model']
            config.model = ModelConfig(
                provider=model_data.get('provider', config.model.provider),
                name=model_data.get('name', config.model.name),
                api_key_env=model_data.get('api_key_env', config.model.api_key_env),
                parameters=model_data.get('parameters', config.model.parameters)
            )

        # Load checkpoint config
        if 'checkpoint' in data:
            checkpoint_data = data['checkpoint']
            postgres_data = checkpoint_data.get('postgres', {})

            config.checkpoint = CheckpointConfig(
                type=checkpoint_data.get('type', config.checkpoint.type),
                postgres=PostgresConfig(
                    host=postgres_data.get('host', config.checkpoint.postgres.host),
                    port=postgres_data.get('port', config.checkpoint.postgres.port),
                    database=postgres_data.get('database', config.checkpoint.postgres.database),
                    user=postgres_data.get('user', config.checkpoint.postgres.user),
                    password_env=postgres_data.get('password_env', config.checkpoint.postgres.password_env),
                    connection_string_env=postgres_data.get('connection_string_env', config.checkpoint.postgres.connection_string_env),
                    pool_size=postgres_data.get('pool_size', config.checkpoint.postgres.pool_size),
                    max_overflow=postgres_data.get('max_overflow', config.checkpoint.postgres.max_overflow)
                )
            )

        # Load API config
        if 'api' in data:
            api_data = data['api']
            config.api = APIConfig(
                endpoints=api_data.get('endpoints', config.api.endpoints),
                cors=api_data.get('cors', config.api.cors)
            )

        # Load tools config
        if 'tools' in data:
            tools_data = data['tools']
            config.tools = ToolsConfig(
                enabled=tools_data.get('enabled', config.tools.enabled)
            )

        # Load logging config
        if 'logging' in data:
            logging_data = data['logging']
            config.logging = LoggingConfig(
                level=logging_data.get('level', config.logging.level),
                format=logging_data.get('format', config.logging.format),
                file=logging_data.get('file', config.logging.file)
            )

        # Load graph config
        if 'graph' in data:
            graph_data = data['graph']
            nodes_data = graph_data.get('nodes', {})

            nodes = {}
            for node_name, node_data in nodes_data.items():
                nodes[node_name] = GraphNodeConfig(
                    enabled=node_data.get('enabled', True),
                    log_messages=node_data.get('log_messages', False),
                    log_completion=node_data.get('log_completion', False),
                    timeout=node_data.get('timeout', 30)
                )

            config.graph = GraphConfig(nodes=nodes)

        return config

    def _apply_env_overrides(self):
        """Apply environment variable overrides"""
        if self._config is None:
            return

        # Override app settings
        debug_env = os.getenv('DEBUG')
        if debug_env is not None:
            self._config.app.debug = debug_env.lower() == 'true'

        port_env = os.getenv('PORT')
        if port_env is not None:
            try:
                self._config.app.port = int(port_env)
            except ValueError:
                logging.warning(f"Invalid PORT value: {port_env}")

        # Override postgres settings from environment
        postgres_host = os.getenv('POSTGRES_HOST')
        if postgres_host:
            self._config.checkpoint.postgres.host = postgres_host

        postgres_port = os.getenv('POSTGRES_PORT')
        if postgres_port:
            try:
                self._config.checkpoint.postgres.port = int(postgres_port)
            except ValueError:
                logging.warning(f"Invalid POSTGRES_PORT value: {postgres_port}")

        postgres_db = os.getenv('POSTGRES_DB')
        if postgres_db:
            self._config.checkpoint.postgres.database = postgres_db

        postgres_user = os.getenv('POSTGRES_USER')
        if postgres_user:
            self._config.checkpoint.postgres.user = postgres_user

    def get_api_key(self) -> str:
        """Get the API key from environment"""
        if self._config is None:
            raise ValueError("Configuration not loaded")

        api_key = os.getenv(self._config.model.api_key_env)
        if not api_key:
            raise ValueError(f"{self._config.model.api_key_env} environment variable is required")
        return api_key

    def get_postgres_password(self) -> Optional[str]:
        """Get PostgreSQL password from environment"""
        if self._config is None:
            return None
        return os.getenv(self._config.checkpoint.postgres.password_env)

    def get_postgres_connection_string(self) -> Optional[str]:
        """Get PostgreSQL connection string from environment or build it"""
        if self._config is None:
            return None

        # Check for direct connection string
        conn_str = os.getenv(self._config.checkpoint.postgres.connection_string_env)
        if conn_str:
            return conn_str

        # Build from components
        password = self.get_postgres_password()
        if not password:
            return None

        postgres = self._config.checkpoint.postgres
        return f"postgresql://{postgres.user}:{password}@{postgres.host}:{postgres.port}/{postgres.database}"

    @property
    def config(self) -> Config:
        """Get the loaded configuration"""
        if self._config is None:
            return self.load()
        return self._config
