import logging
import os
import pathlib
import sys
import struct

import yaml

from ejabberd_external_auth_jwt.auth import jwt_auth

CONFIG_PATH = os.environ["EJABBERD_EXTERNAL_AUTH_JWT_CONFIG_PATH"]


def load_config(fname: pathlib.Path) -> dict:
    """Load configuration file.

    :param fname: config file name

    :return: dictionnary representing the config
    """
    with open(fname, "rt") as file_handle:
        data = yaml.load(file_handle, Loader=yaml.FullLoader)
    # TODO: add config validation
    return data


def from_ejabberd() -> list:
    """Get data from ejabberd stdin."""
    input_length = sys.stdin.buffer.read(2)
    # sys.stderr.write("type input: %s, value: %s" % (type(input_length), input_length))
    (size,) = struct.unpack(">h", input_length)
    return sys.stdin.read(size).split(":")


def to_ejabberd(result: bool) -> None:
    """Send result to ejabberd."""
    answer = 0
    if result:
        answer = 1
    token = struct.pack(">hh", 2, answer)
    sys.stdout.buffer.write(token)
    sys.stdout.flush()


def isuser(username: str, server: str) -> bool:
    """Always returns true, because no jwt is given.

    There is no way to determine if a user exists or not here.
    """
    return True


def main_sync():
    """main sync loop."""
    logging.info("Starting ejabberd_external_auth_jwt in sync mode")
    # loading conf
    conf = load_config(CONFIG_PATH)

    while True:
        data = from_ejabberd()
        sys.stderr.write("### AUTH based on data: %s" % data)
        success = False
        if data[0] == "auth":
            success = jwt_auth(
                login="%s@%s" % (data[1], data[2]), token=data[3], conf=conf
            )
        elif data[0] == "isuser":
            success = isuser(data[1], data[2])
        to_ejabberd(success)
