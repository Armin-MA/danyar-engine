import os
from dataclasses import dataclass, field
from typing import Literal

from src.config.neo4j_config import Neo4jConfig
from src.config.llm_config import LLMConfig

ValidEnv = Literal["development", "production", "testing"]
VALID_ENVS: set[str] = {"development", "production", "testing"}


@dataclass(frozen=True)
class AppConfig:
    """Master application configuration with immutable sub-configs."""

    env: ValidEnv = "development"
    neo4j: Neo4jConfig = field(default_factory=Neo4jConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    debug: bool = True
    server_host: str = "127.0.0.1"
    server_port: int = 8000

    @classmethod
    def from_env(cls, strict: bool = False) -> "AppConfig":
        """Read and validate environment variables to construct an AppConfig instance.

        Args:
            strict: If True, asserts required credentials even in development.
                   In production (env == 'production'), strict validation is always enforced.

        Raises:
            ValueError: If env is invalid, port is not an integer, or required credentials
                        (NEO4J_PASSWORD, GEMINI_API_KEY) are missing in strict/production mode.
        """
        env_raw = os.getenv("APP_ENV", os.getenv("ENV", "development")).strip().lower()
        if env_raw not in VALID_ENVS:
            raise ValueError(
                f"Invalid environment: '{env_raw}'. Must be one of {sorted(VALID_ENVS)}."
            )
        env: ValidEnv = env_raw  # type: ignore

        # Debug flag handling
        debug_env = os.getenv("DEBUG", os.getenv("APP_DEBUG"))
        if debug_env is not None:
            debug = debug_env.strip().lower() in ("true", "1", "yes", "t", "on")
        else:
            debug = (env == "development")

        # Server network settings
        server_host = os.getenv("SERVER_HOST", os.getenv("HOST", "127.0.0.1")).strip()
        port_raw = os.getenv("SERVER_PORT", os.getenv("PORT", "8000")).strip()
        try:
            server_port = int(port_raw)
        except ValueError:
            raise ValueError(f"Invalid server port: '{port_raw}'. Must be an integer.")

        # Neo4j settings
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687").strip()
        neo4j_user = os.getenv("NEO4J_USERNAME", os.getenv("NEO4J_USER", "neo4j")).strip()
        neo4j_password = os.getenv("NEO4J_PASSWORD", "")
        neo4j_database = os.getenv("NEO4J_DATABASE", os.getenv("NEO4J_DB", "neo4j")).strip()

        # LLM settings
        frontier_model = os.getenv(
            "FRONTIER_MODEL", os.getenv("LLM_FRONTIER_MODEL", "gemini-1.5-pro")
        ).strip()
        slm_model = os.getenv(
            "SLM_MODEL", os.getenv("LLM_SLM_MODEL", "gemini-1.5-flash")
        ).strip()
        gemini_api_key = os.getenv("GEMINI_API_KEY", os.getenv("LLM_API_KEY", "")).strip()

        # Strict / Production credential assertions
        is_strict = strict or (env == "production")
        if is_strict:
            missing_creds: list[str] = []
            if not neo4j_password or not neo4j_password.strip():
                missing_creds.append("NEO4J_PASSWORD")
            if not gemini_api_key or not gemini_api_key.strip():
                missing_creds.append("GEMINI_API_KEY")

            if missing_creds:
                raise ValueError(
                    f"Missing required configuration credentials in strict/production mode: {', '.join(missing_creds)}"
                )

        neo4j_config = Neo4jConfig(
            uri=neo4j_uri,
            username=neo4j_user,
            password=neo4j_password,
            database=neo4j_database,
        )

        llm_config = LLMConfig(
            frontier_model=frontier_model,
            slm_model=slm_model,
            api_key=gemini_api_key,
        )

        return cls(
            env=env,
            neo4j=neo4j_config,
            llm=llm_config,
            debug=debug,
            server_host=server_host,
            server_port=server_port,
        )


__all__ = ["AppConfig", "Neo4jConfig", "LLMConfig", "ValidEnv"]
