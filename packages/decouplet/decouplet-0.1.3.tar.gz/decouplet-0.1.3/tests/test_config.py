import os
import tempfile

import decouple


def test_decouplet_config_reads_secret(monkeypatch):
    with tempfile.TemporaryDirectory() as tempdir:
        secret_path = os.path.join(tempdir, "my_secret")

        with open(secret_path, "w", encoding="utf-8") as f:
            f.write("top_secret")

        monkeypatch.setenv("SECRETS_PATH", tempdir)

        from decouplet import config

        assert config("MY_SECRET") == "top_secret"


def test_decouplet_config_reads_env(monkeypatch):
    monkeypatch.setenv("MY_ENV_VAR", "env_value")

    from decouplet import config

    assert config("MY_ENV_VAR") == "env_value"


def test_decouplet_config_reads_both(monkeypatch):
    with tempfile.TemporaryDirectory() as tempdir:
        secret_path = os.path.join(tempdir, "my_secret")

        with open(secret_path, "w", encoding="utf-8") as f:
            f.write("top_secret")

        monkeypatch.setenv("SECRETS_PATH", tempdir)
        monkeypatch.setenv("MY_SECRET", "env_value")

        from decouplet import config

        assert config("MY_SECRET") == "env_value"


def test_decouplet_config_raises_key_error(monkeypatch):
    with tempfile.TemporaryDirectory() as tempdir:
        monkeypatch.setenv("SECRETS_PATH", tempdir)

        from decouplet import config

        try:
            config("NON_EXISTENT_KEY")
        except decouple.UndefinedValueError as e:
            assert str(e) == "NON_EXISTENT_KEY not found. Declare it as envvar or define a default value."


def test_decouplet_config_raises_key_error_for_env(monkeypatch):
    monkeypatch.setenv("MY_ENV_VAR", "env_value")

    from decouplet import config

    try:
        config("NON_EXISTENT_ENV_VAR")
    except decouple.UndefinedValueError as e:
        assert str(e) == "NON_EXISTENT_ENV_VAR not found. Declare it as envvar or define a default value."


def test_decouplet_default_secrets_value_non_exist(monkeypatch):
    monkeypatch.setenv("SECRETS_PATH", "/non/existent/path")

    from decouplet import config

    assert config("DEFAULT_SECRET", default="default_value") == "default_value"


def test_decouplet_default_secrets_value_exist(monkeypatch):
    with tempfile.TemporaryDirectory() as tempdir:
        secret_path = os.path.join(tempdir, "my_secret")

        with open(secret_path, "w", encoding="utf-8") as f:
            f.write("top_secret")

        monkeypatch.setenv("SECRETS_PATH", tempdir)

        from decouplet import config

        assert config("MY_SECRET", default="default_value") == "top_secret"


def test_decouplet_default_env_value_non_exist(monkeypatch):
    monkeypatch.setenv("MY_ENV_VAR", "env_value")

    from decouplet import config

    assert config("NON_EXISTENT_ENV_VAR", default="default_value") == "default_value"


def test_decouplet_default_env_value_exist(monkeypatch):
    monkeypatch.setenv("MY_ENV_VAR", "env_value")

    from decouplet import config

    assert config("MY_ENV_VAR", default="default_value") == "env_value"


def test_decouplet_cast_to_bool_env_value(monkeypatch):
    monkeypatch.setenv("MY_BOOL_ENV_VAR", "True")

    from decouplet import config

    assert config("MY_BOOL_ENV_VAR", cast=bool) is True


def test_decouplet_cast_to_str_env_value(monkeypatch):
    monkeypatch.setenv("MY_STR_ENV_VAR", "42")

    from decouplet import config

    assert config("MY_STR_ENV_VAR", cast=str) == "42"


def test_decouplet_cast_to_int_env_value(monkeypatch):
    monkeypatch.setenv("MY_INT_ENV_VAR", "42")

    from decouplet import config

    assert config("MY_INT_ENV_VAR", cast=int) == 42
