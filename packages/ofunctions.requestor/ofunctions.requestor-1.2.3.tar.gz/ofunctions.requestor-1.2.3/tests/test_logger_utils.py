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

__intname__ = "tests.ofunctions.logger_utils"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2020-2024 Orsiris de Jong"
__licence__ = "BSD 3 Clause"
__build__ = "2022052301"

import logging

from ofunctions.logger_utils import *
from ofunctions.file_utils import get_writable_random_file


def test_worst_logged_level():
    """
    Extrapolate which was worst loglevel called
    """
    logger = logger_get_logger(console=True, debug=True)
    """
    logger.debug('Something logged')
    called_loglevel = logging.DEBUG
    worst_loglevel = get_worst_logger_level(logger)
    assert worst_loglevel == called_loglevel, "Wrong log level caught ({} != {})".format(worst_loglevel, called_loglevel)
    """
    logger.info("Something logged")
    called_loglevel = logging.INFO
    worst_loglevel = get_worst_logger_level(logger)
    assert (
        worst_loglevel == called_loglevel
    ), "Wrong log level caught ({} != {})".format(worst_loglevel, called_loglevel)
    logger.warning("Something logged")
    called_loglevel = logging.WARNING
    worst_loglevel = get_worst_logger_level(logger)
    assert (
        worst_loglevel == called_loglevel
    ), "Wrong log level caught ({} != {})".format(worst_loglevel, called_loglevel)
    logger.error("Something logged")
    called_loglevel = logging.ERROR
    worst_loglevel = get_worst_logger_level(logger)
    assert (
        worst_loglevel == called_loglevel
    ), "Wrong log level caught ({} != {})".format(worst_loglevel, called_loglevel)
    logger.critical("Something logged")
    called_loglevel = logging.CRITICAL
    worst_loglevel = get_worst_logger_level(logger)
    assert (
        worst_loglevel == called_loglevel
    ), "Wrong log level caught ({} != {})".format(worst_loglevel, called_loglevel)

    # back to a info level call, we should still have CRITICAL as worst level
    logger.info("Something logged")
    called_loglevel = logging.CRITICAL
    worst_loglevel = get_worst_logger_level(logger)
    assert (
        worst_loglevel == called_loglevel
    ), "Wrong log level caught ({} != {})".format(worst_loglevel, called_loglevel)


def test_logger_ger_logger():
    """
    Should be tested on Python 2.7
    """
    logger = logger_get_logger(log_file=get_writable_random_file())
    logger.info("Café unicode accent")


def test_logger_nonwritable_logger():
    logger = logger_get_logger(log_file="/abc/def/nonexistent/filepath")
    logger.info("Café unicode accent")


def test_logger_exception():
    logger = logger_get_logger(console=True)
    try:
        # Log some unicode character which should throw an unhandled UnicodedecodeError exception in Python 2.7
        raise Exception("jörn")
    except Exception as exc:
        logger.exception(exc)


if __name__ == "__main__":
    print("Example code for %s, %s" % (__intname__, __build__))
    test_worst_logged_level()
    test_logger_ger_logger()
    test_logger_exception()
