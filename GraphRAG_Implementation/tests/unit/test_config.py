import pytest

from fsm_graphrag.config import load_settings


def test_load_settings_requires_credentials(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    for key in ("NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"):
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(ValueError, match="NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD"):
        load_settings()


def test_load_settings_uses_environment(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
    monkeypatch.setenv("NEO4J_USER", "neo4j")
    monkeypatch.setenv("NEO4J_PASSWORD", "local-test-secret")
    monkeypatch.setenv("NEO4J_DATABASE", "neo4j")
    monkeypatch.setenv("LOG_LEVEL", "debug")

    settings = load_settings()

    assert settings.neo4j_uri == "bolt://localhost:7687"
    assert settings.neo4j_user == "neo4j"
    assert settings.neo4j_password == "local-test-secret"
    assert settings.neo4j_database == "neo4j"
    assert settings.log_level == "DEBUG"
    assert settings.llm_base_url == "https://api.openai.com/v1"
    assert settings.llm_api_key is None
    assert settings.llm_model is None
    assert settings.llm_temperature == 0
    assert settings.neo4j_query_timeout_seconds == 5


def test_load_settings_reads_generic_llm_configuration(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NEO4J_URI", "bolt://localhost:7687")
    monkeypatch.setenv("NEO4J_USER", "neo4j")
    monkeypatch.setenv("NEO4J_PASSWORD", "local-test-secret")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://example.test/v1/")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_TEMPERATURE", "0.2")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "42")
    monkeypatch.setenv("NEO4J_QUERY_TIMEOUT_SECONDS", "8")

    settings = load_settings()

    assert settings.llm_api_key == "test-key"
    assert settings.llm_base_url == "https://example.test/v1"
    assert settings.llm_model == "test-model"
    assert settings.llm_temperature == 0.2
    assert settings.llm_timeout_seconds == 42
    assert settings.neo4j_query_timeout_seconds == 8
