"""
Modified from flask.testsuite.config by whtsky

    flask.testsuite.config
    ~~~~~~~~~~~~~~~~~~~~~~

    Configuration and instances.

    :copyright: (c) 2011 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""


import os

from waterspout.config import Config

TEST_KEY = 'foo'
SECRET_KEY = 'devkey'


def common(config):
    assert config['secret_key'] == 'devkey'
    assert config['test_key'] == 'foo'
    assert 'ConfigTestCase' not in config


def test_config_from_file():
    config = Config()
    config.from_pyfile(__file__.rsplit('.', 1)[0] + '.py')
    common(config)


def test_config_from_object():
    config = Config()
    config.from_object(__name__)
    common(config)


def test_config_from_class():
    class Base(object):
        TEST_KEY = 'foo'

    class Test(Base):
        SECRET_KEY = 'devkey'
    config = Config()
    config.from_object(Test)
    common(config)


def test_config_from_envvar():
    env = os.environ
    try:
        os.environ = {}
        config = Config()
        try:
            config.from_envvar('FOO_SETTINGS')
        except RuntimeError as e:
            assert "'FOO_SETTINGS' is not set" in str(e)
        else:
            raise

        assert not config.from_envvar('FOO_SETTINGS', silent=True)

        os.environ = {'FOO_SETTINGS': __file__.rsplit('.', 1)[0] + '.py'}
        assert config.from_envvar('FOO_SETTINGS')
        common(config)
    finally:
        os.environ = env


def test_from_envvar_missing():
    env = os.environ
    config = Config()
    try:
        os.environ = {'FOO_SETTINGS': 'missing.cfg'}
        try:
            config.from_envvar('FOO_SETTINGS')
        except IOError as e:
            msg = str(e)
            assert msg.startswith('[Errno 2] Unable to load configuration '
                                  'file (No such file or directory):')
            assert msg.endswith("missing.cfg'")
        else:
            raise
        assert not config.from_envvar('FOO_SETTINGS', silent=True)
    finally:
        os.environ = env


def test_repr():
    config = Config()
    assert str(config).startswith('<Config')
