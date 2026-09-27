import importlib


def test_config_loads_with_valid_environment(monkeypatch):
    monkeypatch.setenv(
        "SECRET_KEY",
        "a" * 32
    )
    monkeypatch.setenv(
        "ALGORITHM",
        "HS256"
    )
    monkeypatch.setenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "30"
    )

    import app.core.config as config

    importlib.reload(config)

    assert config.SECRET_KEY == "a" * 32
    assert config.ALGORITHM == "HS256"
    assert config.ACCESS_TOKEN_EXPIRE_MINUTES == 30


def test_config_rejects_short_secret_key(monkeypatch):
    monkeypatch.setenv(
        "SECRET_KEY",
        "short"
    )
    monkeypatch.setenv(
        "ALGORITHM",
        "HS256"
    )
    monkeypatch.setenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "30"
    )

    import app.core.config as config

    try:
        importlib.reload(config)
    except RuntimeError as exc:
        assert str(exc) == (
            "SECRET_KEY must be at least 32 characters long"
        )
    else:
        raise AssertionError(
            "Expected RuntimeError for short SECRET_KEY"
        )


def test_config_rejects_invalid_algorithm(monkeypatch):
    monkeypatch.setenv(
        "SECRET_KEY",
        "a" * 32
    )
    monkeypatch.setenv(
        "ALGORITHM",
        "none"
    )
    monkeypatch.setenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "30"
    )

    import app.core.config as config

    try:
        importlib.reload(config)
    except RuntimeError as exc:
        assert str(exc) == "Unsupported JWT algorithm"
    else:
        raise AssertionError(
            "Expected RuntimeError for unsupported algorithm"
        )


def test_config_rejects_invalid_expiration(monkeypatch):
    monkeypatch.setenv(
        "SECRET_KEY",
        "a" * 32
    )
    monkeypatch.setenv(
        "ALGORITHM",
        "HS256"
    )
    monkeypatch.setenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "0"
    )

    import app.core.config as config

    try:
        importlib.reload(config)
    except RuntimeError as exc:
        assert str(exc) == (
            "ACCESS_TOKEN_EXPIRE_MINUTES must be greater than 0"
        )
    else:
        raise AssertionError(
            "Expected RuntimeError for invalid expiration"
        )