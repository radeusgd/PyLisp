import pytest

from pylisp.environment import empty_environment
from pylisp.errors import LispError


def test_update():
    env = empty_environment()
    env.update("ABC", 42)
    assert env.lookup("ABC") == 42


def test_forward_ref():
    env = empty_environment()
    env.allocate_forward_reference("ref")
    with pytest.raises(LispError):
        env.lookup("ref")
    env.fill_forward_reference("ref", 42)
    assert env.lookup("ref") == 42


def test_fork_not_affected():
    env = empty_environment()
    env.update("ABC", 44)
    env2 = env.fork()
    env.update("ABC", 13)  # overwrite in old env
    assert env2.lookup("ABC") == 44


def test_fork_forward_ref():
    env = empty_environment()
    env.allocate_forward_reference("ref")
    env2 = env.fork()
    env.fill_forward_reference("ref", 23)
    assert env2.lookup("ref") == 23
