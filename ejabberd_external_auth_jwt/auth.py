"""JWT auth
"""
import datetime
import json
import logging

import jwt


def jwt_auth(login: str, token: str, conf: dict) -> bool:
    """authenticate login against the given jwt token

    The token must be valid.
    Auth can be validated against 2 secrets: the current one and the old-one
    This enable the possibility to change secrets more easyly, and more often.
    aud and issuer are also checked if provided in config
    exp, iat and nbf dates are also checked.

    :param login: user login
    :param token: jwt token
    :param conf: configuration loaded from config file

    :return: the result of the login: False is not valided, True if ok.

    In order to keep the loop active, this function never raises anything
    And catch all uncatched exception and send False if exception.
    """
    _leeway = 10  # some time margin for checking token availability
    try:
        try:
            payload = jwt.decode(
                token,
                conf.get("jwt_secret"),
                issuer=conf.get("issuer"),
                audience=conf.get("audience"),
                leeway=datetime.timedelta(seconds=conf.get("leeway", _leeway)),
                algorithms=[conf.get("jwt_algorithm", "HS256")],
            )
        except jwt.DecodeError:
            # first decode is not working, try the second one
            logging.info("Current jwt_secret is not working, try the old one")
            payload = jwt.decode(
                token,
                conf.get("jwt_secret_old"),
                issuer=conf.get("issuer"),
                audience=conf.get("audience"),
                leeway=datetime.timedelta(seconds=conf.get("leeway", _leeway)),
                algorithms=[conf.get("jwt_algorithm", "HS256")],
            )

        if conf.get("jwt_expiration") is not None:
            # server side expiration is set, iat is now mandatory
            if payload.get("iat") is None:
                return False  # iat mandatory if server-side expiration is on
            # server-side check expiration with iat
            # (in addition to exp key, we added here a server-side expiration
            # check based on iat key: this is an added security and add the
            # possibility to expire all keys by updating this value in config,
            # just in case)
            now = datetime.datetime.utcnow() + datetime.timedelta(
                seconds=conf.get("leeway", _leeway)
            )
            if datetime.datetime.utcfromtimestamp(payload.get("iat")) > now:
                logging.warning("Wrong auth for %s: iat claim is in the future", login)
                return False
            if now > datetime.datetime.utcfromtimestamp(
                payload.get("iat")
            ) + datetime.timedelta(seconds=conf.get("jwt_expiration")):
                logging.warning(
                    "Wrong auth for %s: Expired (because of server-side expiration)",
                    login,
                )
                return False
        if payload.get("aud") is not None and payload.get("aud") != conf.get(
            "audience"
        ):
            logging.warning("Wrong auth for %s: Wrong audience", login)
            return False

        # Here the jwt seems correct, now check if the user is correct
        if payload.get(conf.get("user_claim", "sub")) == login:
            return True
        else:
            logging.warning("Wrong auth for %s: Wrong user", login)
            return False
    except jwt.ExpiredSignatureError:
        logging.warning("Wrong auth for %s: Expired", login)
        return False
    except jwt.exceptions.InvalidIssuedAtError:
        logging.warning("Wrong auth for %s: iat claim is in the future", login)
        return False
    except jwt.InvalidIssuerError:
        logging.warning("Wrong auth for %s: Invalid Issuer", login)
        return False
    except jwt.InvalidAudienceError:
        logging.warning("Wrong auth for %s: Invalid Audience", login)
        return False
    except jwt.DecodeError:
        logging.warning("Wrong auth for %s: Wrong credentials", login)
        return False
    except KeyError as exc:  # most certainly a missing payload
        logging.warning(
            "Wrong auth for %s: Wrong credentials: missing %s in the payload",
            login,
            exc,
        )
        return False
    except Exception as exc:  # catch all
        logging.error(
            "Wrong auth for %s: Unhandled Exception: %s:%s",
            login,
            exc.__class__.__name__,
            exc,
        )
        return False

    logging.error("Wrong auth for %s: Returned False", login)
    return False  # we should never reach this one
