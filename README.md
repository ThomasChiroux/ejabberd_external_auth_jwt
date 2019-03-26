# ejabberd_external_auth_jwt

A simple library to use with ejabberd as auth script.

This auth script will authorise used based on given JWT token

MAKE SURE SCRIPT FILES, CONFIG FILES AND LOG FILE ARE ACCESSIBLE FOR ejabberd USER!

## installation

* clone the repo

* create a venv using

  pipenv install

  or using your favorite ways

* run ./make_release from the repo root to build a wheel package

* copy the wheel file into your ejabberd installation and run

  pip3 install ejabberd_external_auth_jwt-X.X.X-py3-none-any.whl

## configuration

* put a config file in your ejabberd installation (example in conf/)
* use env to tell to auth program where is the config file:

  ex:

    EJABBERD_EXTERNAL_AUTH_JWT_CONFIG_PATH=/home/ejabberd/conf/ejabberd_external_auth_jwt.yml

### ejabberd configuration

  example ejabberd config for external auth:

  host_config:
  "ejabberd":
    auth_method: [external]
    extauth_program: "ejabberd_external_auth_jwt"
    extauth_instances: 1
    auth_use_cache: false

### module configuration

 see example config file in ./conf/

## development and tests

 run:

 $ pytest .
