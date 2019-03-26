"""Test Auth Module."""
import datetime

import pytest

import jwt

from ejabberd_external_auth_jwt.auth import jwt_auth


@pytest.fixture
def conf_empty():
    """empty config used for tests."""
    return {}


@pytest.fixture
def conf_simple():
    """simple config used for tests.

    only mandatory elements
    """
    return {"jwt_secret": "SECRET"}


@pytest.fixture
def conf_simple2():
    """simple config used for tests.

    only mandatory elements
    """
    return {"jwt_secret": "SECRET", "user_claim": "jid"}


@pytest.fixture
def conf_full():
    """complete config used for tests.
    """
    return {
        "jwt_secret": "SECRET",
        "user_claim": "jid",
        "jwt_secret_old": "OLDSECRET",
        "jwt_algorithm": "HS256",
        "issuer": "https://www.myapplication.com",
        "audience": "https://www.myapplication.com",
        "jwt_expiration": 86400,
        "leeway": 10,
    }


@pytest.fixture
def payload_simple():
    """simple jwt payload"""
    return {"sub": "user@domain.ext"}


@pytest.fixture
def payload_simple2():
    """simple jwt payload"""
    return {"jid": "user@domain.ext"}


@pytest.fixture(scope="function")
def payload_full():
    """full jwt payload"""
    return {
        "iss": "https://www.myapplication.com",
        "aud": "https://www.myapplication.com",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=10),
        "iat": datetime.datetime.utcnow(),
        "nbf": datetime.datetime.utcnow(),
        "jid": "user@domain.ext",
    }


def test_auth_empty_nok_1(conf_empty, payload_simple):
    """simple auth test, mandatory secret not given."""
    jwt_token = jwt.encode(payload_simple, "", "HS256").decode("utf-8")
    assert jwt_auth("user@domain.ext", jwt_token, conf_empty) is False


def test_auth_empty_nok_1(conf_empty, payload_simple):
    """simple auth test, mandatory secret not given."""
    jwt_token = jwt.encode(payload_simple, "SECRET", "HS256").decode("utf-8")
    assert jwt_auth("user@domain.ext", jwt_token, conf_empty) is False


def test_auth_simple_ok_1(conf_simple, payload_simple):
    """simple auth test."""
    jwt_token = jwt.encode(payload_simple, "SECRET", "HS256").decode("utf-8")
    assert jwt_auth("user@domain.ext", jwt_token, conf_simple) is True


def test_auth_simple_nok_1(conf_simple, payload_simple):
    """simple auth test nok because login does not match."""
    jwt_token = jwt.encode(payload_simple, "SECRET", "HS256").decode("utf-8")
    assert jwt_auth("user2@domain.ext", jwt_token, conf_simple) is False


def test_auth_simple_nok_2(conf_simple, payload_simple):
    """simple auth test nok because bad secret."""
    jwt_token = jwt.encode(payload_simple, "BADSECRET", "HS256").decode("utf-8")
    assert jwt_auth("user@domain.ext", jwt_token, conf_simple) is False


def test_auth_simple2_ok_1(conf_simple2, payload_simple2):
    """simple auth test."""
    jwt_token = jwt.encode(payload_simple2, "SECRET", "HS256").decode("utf-8")
    assert jwt_auth("user@domain.ext", jwt_token, conf_simple2) is True


def test_auth_simple2_nok_1(conf_simple2, payload_simple2):
    """simple auth test nok because login does not match."""
    jwt_token = jwt.encode(payload_simple2, "SECRET", "HS256").decode("utf-8")
    assert jwt_auth("user2@domain.ext", jwt_token, conf_simple2) is False


def test_auth_simple2_nok_2(conf_simple2, payload_simple2):
    """simple auth test nok because login does not match."""
    jwt_token = jwt.encode(payload_simple2, "BADSECRET", "HS256").decode("utf-8")
    assert jwt_auth("user@domain.ext", jwt_token, conf_simple2) is False


def test_auth_simple2_nok_3(conf_simple2, payload_simple):
    """simple auth test nok because bad user claim."""
    jwt_token = jwt.encode(payload_simple, "SECRET", "HS256").decode("utf-8")
    assert jwt_auth("user@domain.ext", jwt_token, conf_simple2) is False


def test_auth_full_ok_1(conf_full, payload_full):
    """full auth test with all controls enabled in conf."""
    jwt_token = jwt.encode(payload_full, "SECRET", "HS256").decode("utf-8")
    assert jwt_auth("user@domain.ext", jwt_token, conf_full) is True


def test_auth_full_ok_2(conf_full, payload_full):
    """full auth test with all controls enabled in conf, encoded with old secret"""
    jwt_token = jwt.encode(payload_full, "OLDSECRET", "HS256").decode("utf-8")
    assert jwt_auth("user@domain.ext", jwt_token, conf_full) is True


def test_auth_full_nok_iss_1(conf_full, payload_full):
    """full auth test with all controls enabled in conf, bad iss"""
    payload_full["iss"] = "bad_iss"
    jwt_token = jwt.encode(payload_full, "SECRET", "HS256").decode("utf-8")
    assert jwt_auth("user@domain.ext", jwt_token, conf_full) is False


def test_auth_full_nok_aud_1(conf_full, payload_full):
    """full auth test with all controls enabled in conf, bad aud"""
    payload_full["aud"] = "bad_aud"
    jwt_token = jwt.encode(payload_full, "SECRET", "HS256").decode("utf-8")
    assert jwt_auth("user@domain.ext", jwt_token, conf_full) is False


def test_auth_full_nok_exp_1(conf_full, payload_full):
    """full auth test with all controls enabled in conf, expired"""
    payload_full["exp"] = datetime.datetime.utcnow() - datetime.timedelta(seconds=11)
    jwt_token = jwt.encode(payload_full, "SECRET", "HS256").decode("utf-8")
    assert jwt_auth("user@domain.ext", jwt_token, conf_full) is False


def test_auth_full_nok_iat_1(conf_full, payload_full):
    """full auth test with all controls enabled in conf, in the future"""
    payload_full["iat"] = datetime.datetime.utcnow() + datetime.timedelta(seconds=11)
    jwt_token = jwt.encode(payload_full, "SECRET", "HS256").decode("utf-8")
    assert jwt_auth("user@domain.ext", jwt_token, conf_full) is False


def test_auth_full_nok_nbf_1(conf_full, payload_full):
    """full auth test with all controls enabled in conf, not yet active"""
    payload_full["nbf"] = datetime.datetime.utcnow() + datetime.timedelta(seconds=11)
    jwt_token = jwt.encode(payload_full, "SECRET", "HS256").decode("utf-8")
    assert jwt_auth("user@domain.ext", jwt_token, conf_full) is False
