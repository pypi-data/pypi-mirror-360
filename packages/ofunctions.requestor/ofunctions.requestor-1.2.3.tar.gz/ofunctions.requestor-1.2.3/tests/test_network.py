#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of ofunctions module

"""
Versioning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionality
    Patch version: Backwards compatible bug fixes
"""


__intname__ = "tests.ofunctions.network"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2020-2024 Orsiris de Jong"
__licence__ = "BSD 3 Clause"
__build__ = "2023122801"


# Use logging so we se actual output of probe_mtu
import os
from ofunctions.network import *


def running_on_github_actions():
    """
    This is set in github actions workflow with
          env:
        RUNNING_ON_GITHUB_ACTIONS: true
    """
    return os.environ.get("RUNNING_ON_GITHUB_ACTIONS").lower() == "true"


def test_ping():
    # ping does not work on GH
    if running_on_github_actions():
        return None

    result = ping()
    print("Ping multiple default hosts result: %s" % result)
    assert result is True, (
        "Cannot ping. This test may fail if the host" "does not have internet indeed."
    )

    result = ping("example.not.existing")
    print("Ping to not existing host result: %s" % result)
    assert result is False, "Should not be able to ping non existing host"

    result = ping(mtu=1300, do_not_fragment=True)
    print("Ping to default hosts MTU 1300: %s" % result)
    assert result is True, "WAN should probably have more than MTU 1400"

    result = ping(mtu=1600, do_not_fragment=True)
    print("Ping to default hosts MTU 1600: %s" % result)
    assert result is False, "WAN should probably not have more than MTU 1500"

    result = ping("::1")
    print("Ping IPv6 localhost: %s" % result)
    assert result is True, "Localhost IPv6 address should be pingable"

    result = ping("::1", do_not_fragment=True)
    print("Ping IPv6 localhost with no fragment bit should not work")
    assert (
        result is False
    ), "Localhost IPv6 address should not be pingable when do_not_fragment=True"

    result = ping(["example.not.existing", "127.0.0.1"], all_targets_must_succeed=True)
    print(
        "Ping multiple hosts of which one is not working with all_targets_must_succeed=True result: %s"
        % result
    )
    assert (
        result is False
    ), "At least one failing host should make all_targets_must_succeed=True ping fail"

    result = ping(["127.0.0.1", "127.0.0.1"], all_targets_must_succeed=True)
    print("Ping multiple hosts with all_targets_must_succeed=True result: %s" % result)
    assert (
        result is True
    ), "all_targets_must_succeed=True ping with working hosts should always work"

    result = ping(
        ["example.not.existing", "example.not.existing"], all_targets_must_succeed=True
    )
    print(
        "Ping multiple hosts not working hots with all_targets_must_succeed=True result: %s"
        % result
    )
    assert (
        result is False
    ), "Failing hosts should make all_targets_must_succeed=True ping fail"


def test_test_http_internet():
    # Hopefully these addresses don't exist
    result = check_http_internet(
        ["http://example.not.existing"], ["http://192.168.90.256"]
    )
    print("HTTP result: %s" % result)
    assert result is False, "Bogus http check should give negative result"

    # This one should give positive result too
    result = check_http_internet(
        ["http://www.google.com", "http://example.not.existing"]
    )
    print("HTTP result: %s" % result)
    assert result is True, (
        "At least one good result should trigger positive result. This test may fail if the host"
        "does not have internet indeed."
    )

    # This one should give negative result
    # Hopefully these addresses don't exist
    result = check_http_internet(
        ["http://example.not.existing"],
        ["http://192.168.90.256"],
        all_targets_must_succeed=True,
    )
    print("HTTP result: %s" % result)
    assert result is False, "Bogus http check should give negative result"

    # This one should give negative result too
    result = check_http_internet(
        ["http://www.google.com", "http://example.not.existing"],
        ["http://1.1.1.1", "http://192.168.90.256"],
        all_targets_must_succeed=True,
    )
    print("HTTP result: %s" % result)
    assert result is False, (
        "With all_targets_must_succeed=True, this test should fail."
        "This test may fail if the host does not have internet indeed."
    )

    # Make sure http://1.1.1.1 or http://1.0.0.1 (or whatever you want to test) works, at least one of those two
    result = check_http_internet(ip_servers=["http://1.1.1.1", "http://1.0.0.1"])
    print("HTTP result: %s" % result)
    assert result is True, (
        "Cannot check http internet. This test may fail if the host"
        "does not have internet indeed."
    )


def test_get_public_ip():
    result = get_public_ip()
    print("Public IP: {}".format(result))
    assert result is not None, "Cannot get public IP"


def test_probe_mtu():
    # ping does not work on GH
    if running_on_github_actions():
        return None

    result = probe_mtu("127.0.0.1", min=1400, max=9000)
    print("Localhost MTU: %s" % result)
    assert (
        9000 <= result <= 65500
    ), "Localhost MTU should be somewhere between 9000 and 65500, is: {}".format(result)

    result = probe_mtu("1.1.1.1")
    print("Internet MTU: %s" % result)
    assert 1492 < result < 1501, "Internet MTU should be 1492<=mtu<=1500"

    # Should return a ValueError
    try:
        probe_mtu("1.2.3.4.5.6.7.8.")
    except ValueError:
        assert True, "Non IP entry cannot be probed, obviously"
    else:
        assert False, "Non IP entry was probed !"

    # Should return a ValueError
    try:
        probe_mtu("127.0.0.1", min=2)
    except ValueError:
        assert True, "MTU should not be lower than 28"
    else:
        assert False, "MTU lower than 28 did not raise an exception"

    # Should return a ValueError
    try:
        probe_mtu("127.0.0.1", method="TCP")
    except ValueError:
        assert True, "Unknown method"
    else:
        assert False, "Unknown MTU probe method did not raise an exception"


if __name__ == "__main__":
    print("Example code for %s, %s" % (__intname__, __build__))
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    test_ping()
    test_test_http_internet()
    test_get_public_ip()
    test_probe_mtu()
