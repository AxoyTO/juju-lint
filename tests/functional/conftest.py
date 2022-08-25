"""Pytest configuration file for juju-lint tests."""
import os
import shutil
from subprocess import check_call, check_output
from textwrap import dedent
import logging

import pytest


def pytest_configure(config):
    """Pytest configuration."""
    config.addinivalue_line(
        "markers",
        "smoke: mark test as a smoke test"
    )
    config.addinivalue_line(
        "markers",
        "cloud: mark test as a cloud test"
    )


@pytest.fixture(scope="session", autouse=True)
def install_package():
    """Install the package to the system and cleanup afterwards.

    Depending on the environment variable JUJULINT_TEST_SNAP,
    it will install the snap or the python package.
    """
    jujulint_test_snap = os.environ.get("JUJULINT_TEST_SNAP", None)
    if jujulint_test_snap:
        logging.info(f"Installing {jujulint_test_snap}")
        assert os.path.isfile(jujulint_test_snap)
        assert check_call(f"sudo snap install --dangerous --classic {jujulint_test_snap}".split()) == 0
        assert check_output("which juju-lint".split()).decode().strip() == os.path.join(
            "/snap/bin/juju-lint"
        )
    else:
        logging.warning("Installing python package")
        assert check_call("python3 -m pip install .".split()) == 0
        assert check_output("which juju-lint".split()).decode().strip() == os.path.join(
            os.getcwd(), ".tox/func/bin/juju-lint"
        )

    yield jujulint_test_snap

    if jujulint_test_snap:
        logging.info("Removing snap package juju-lint")
        check_call("sudo snap remove juju-lint".split())
    else:
        logging.info("Uninstalling python package jujulint")
        check_call("python3 -m pip uninstall --yes jujulint".split())


@pytest.fixture
def basedir():
    """Return the basedir for the installation.

    This will ease testing the rules files that we ship
    with the juju-lint snap.
    """
    if os.environ.get("JUJULINT_TEST_SNAP", None):
        basedir = "/snap/juju-lint/current/"
    else:
        basedir = os.getcwd()
    yield basedir


@pytest.fixture
def rules_file(basedir):
    """Return the rules file for testing."""
    yield os.path.join(basedir, "contrib/fcb-yoga-focal.yaml")


@pytest.fixture
def manual_file():
    """Return the bundle file for testing."""
    yield os.path.join(
        os.path.dirname(__file__),
        "resources/fcb-yoga-focal-bundle.yaml"
    )


@pytest.fixture
def lint_rules_yaml(basedir, rules_file):
    """Return the default lint-rules.yaml file and cleanup."""
    lint_rules_yaml_file = os.path.join(
        os.getcwd(),
        "lint-rules.yaml"
    )
    shutil.copy(rules_file, lint_rules_yaml_file)

    includes_dir = os.path.join(os.getcwd(), "includes")
    os.symlink(
        os.path.join(basedir, "contrib/includes"),
        includes_dir
    )
    yield lint_rules_yaml_file
    os.unlink(lint_rules_yaml_file)
    os.unlink(includes_dir)


@pytest.fixture
def local_cloud():
    """Prepare the local configuration file for juju-lint.

    If there's an existing configuration directory, back it up
    first and then recover.
    """
    local_cloud_name = "test"
    backup = False
    local_config_dir = os.path.join(
        os.path.expanduser("~"), ".config/juju-lint"
    )
    local_config_file = os.path.join(local_config_dir, "config.yaml")
    if os.path.isdir(local_config_dir):
        logging.info("Backing up existing config directory")
        shutil.move(
            local_config_dir,
            local_config_dir + ".bak"
        )
        backup = True
    os.makedirs(local_config_dir)
    with open(local_config_file, "w") as config_yaml:
        config_yaml_str = f"""\
            clouds:
              {local_cloud_name}:
                type: openstack
            """
        config_yaml.write(dedent(config_yaml_str))

    yield local_cloud_name

    shutil.rmtree(local_config_dir)
    if backup:
        logging.info("Restoring backup")
        shutil.move(
            local_config_dir + ".bak",
            local_config_dir
        )
