import pytest

from discord_voicebot import util


def _clear_env(monkeypatch):
    for var in [
        "_VOICEBOT_TOKEN_CLI",
        "DISCORD_TOKEN",
        "_VOICEBOT_PING_URL_CLI",
        "VOICEBOT_PING_URL",
        "_VOICEBOT_PING_INTERVAL_CLI",
        "VOICEBOT_PING_INTERVAL",
        "XDG_CONFIG_HOME",
    ]:
        monkeypatch.delenv(var, raising=False)


def test_intents_enables_members_and_voice_states():
    intents = util.intents()
    assert intents.members
    assert intents.voice_states


def test_find_token_cli_env(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("_VOICEBOT_TOKEN_CLI", "cli-token")
    assert util.find_token() == "cli-token"


def test_find_token_plain_env(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("DISCORD_TOKEN", "env-token")
    assert util.find_token() == "env-token"


def test_find_token_dotenv_cwd(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    monkeypatch.chdir(tmp_path)
    tmp_path.joinpath(".env").write_text("DISCORD_TOKEN=file-token")
    with pytest.raises(RuntimeError):
        util.find_token()


def test_find_token_dotenv_xdg(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    config_home = tmp_path / "config"
    env_dir = config_home / "voicebot"
    env_dir.mkdir(parents=True)
    env_dir.joinpath(".env").write_text("DISCORD_TOKEN=xdg-token")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_home))
    monkeypatch.chdir(tmp_path)
    assert util.find_token() == "xdg-token"


def test_find_token_xdg_overrides_cwd(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    config_home = tmp_path / "config"
    env_dir = config_home / "voicebot"
    env_dir.mkdir(parents=True)
    env_dir.joinpath(".env").write_text("DISCORD_TOKEN=xdg-token")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_home))
    monkeypatch.chdir(tmp_path)
    tmp_path.joinpath(".env").write_text("DISCORD_TOKEN=file-token")
    assert util.find_token() == "xdg-token"


def test_find_token_not_found(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(RuntimeError):
        util.find_token()


def test_find_ping_url_from_cli(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("_VOICEBOT_PING_URL_CLI", "http://cli")
    assert util.find_ping_url() == "http://cli"


def test_find_ping_url_from_env(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("VOICEBOT_PING_URL", "http://env")
    assert util.find_ping_url() == "http://env"


def test_find_ping_interval_from_cli(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("_VOICEBOT_PING_INTERVAL_CLI", "42")
    assert util.find_ping_interval() == 42


def test_find_ping_interval_from_env(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("VOICEBOT_PING_INTERVAL", "99")
    assert util.find_ping_interval() == 99
