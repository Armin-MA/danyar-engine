import pytest
from dataclasses import FrozenInstanceError
from src.config.app_config import AppConfig, Neo4jConfig, LLMConfig


class TestAppConfig:
    def test_default_values_clean_env(self, monkeypatch):
        # Clear environment variables
        for key in ["APP_ENV", "ENV", "DEBUG", "APP_DEBUG", "SERVER_HOST", "HOST",
                    "SERVER_PORT", "PORT", "NEO4J_URI", "NEO4J_USERNAME", "NEO4J_USER",
                    "NEO4J_PASSWORD", "NEO4J_DATABASE", "NEO4J_DB", "FRONTIER_MODEL",
                    "LLM_FRONTIER_MODEL", "SLM_MODEL", "LLM_SLM_MODEL", "GEMINI_API_KEY", "LLM_API_KEY"]:
            monkeypatch.delenv(key, raising=False)

        config = AppConfig.from_env(strict=False)

        assert config.env == "development"
        assert config.debug is True
        assert config.server_host == "127.0.0.1"
        assert config.server_port == 8000
        assert config.neo4j.uri == "bolt://localhost:7687"
        assert config.neo4j.username == "neo4j"
        assert config.neo4j.password == ""
        assert config.neo4j.database == "neo4j"
        assert config.llm.frontier_model == "gemini-1.5-pro"
        assert config.llm.slm_model == "gemini-1.5-flash"
        assert config.llm.api_key == ""

    def test_custom_environment_variables(self, monkeypatch):
        monkeypatch.setenv("APP_ENV", "testing")
        monkeypatch.setenv("DEBUG", "false")
        monkeypatch.setenv("SERVER_HOST", "0.0.0.0")
        monkeypatch.setenv("SERVER_PORT", "9000")
        monkeypatch.setenv("NEO4J_URI", "neo4j+s://demo.databases.neo4j.io")
        monkeypatch.setenv("NEO4J_USERNAME", "admin")
        monkeypatch.setenv("NEO4J_PASSWORD", "secret_pass")
        monkeypatch.setenv("NEO4J_DATABASE", "danyar_db")
        monkeypatch.setenv("FRONTIER_MODEL", "gemini-2.0-pro")
        monkeypatch.setenv("SLM_MODEL", "gemini-2.0-flash")
        monkeypatch.setenv("GEMINI_API_KEY", "custom_key_123")

        config = AppConfig.from_env(strict=True)

        assert config.env == "testing"
        assert config.debug is False
        assert config.server_host == "0.0.0.0"
        assert config.server_port == 9000
        assert config.neo4j.uri == "neo4j+s://demo.databases.neo4j.io"
        assert config.neo4j.username == "admin"
        assert config.neo4j.password == "secret_pass"
        assert config.neo4j.database == "danyar_db"
        assert config.llm.frontier_model == "gemini-2.0-pro"
        assert config.llm.slm_model == "gemini-2.0-flash"
        assert config.llm.api_key == "custom_key_123"

    def test_strict_mode_missing_credentials_raises_error(self, monkeypatch):
        monkeypatch.setenv("APP_ENV", "development")
        monkeypatch.delenv("NEO4J_PASSWORD", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        with pytest.raises(ValueError, match="Missing required configuration credentials in strict/production mode"):
            AppConfig.from_env(strict=True)

    def test_production_mode_enforces_strictness(self, monkeypatch):
        monkeypatch.setenv("APP_ENV", "production")
        monkeypatch.delenv("NEO4J_PASSWORD", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        with pytest.raises(ValueError, match="Missing required configuration credentials in strict/production mode"):
            AppConfig.from_env(strict=False)

    def test_invalid_environment_raises_error(self, monkeypatch):
        monkeypatch.setenv("APP_ENV", "invalid_env_name")
        with pytest.raises(ValueError, match="Invalid environment: 'invalid_env_name'"):
            AppConfig.from_env(strict=False)

    def test_invalid_port_raises_error(self, monkeypatch):
        monkeypatch.setenv("SERVER_PORT", "not_a_number")
        with pytest.raises(ValueError, match="Invalid server port"):
            AppConfig.from_env(strict=False)

    def test_immutability(self):
        config = AppConfig()
        with pytest.raises(FrozenInstanceError):
            config.debug = False  # type: ignore
