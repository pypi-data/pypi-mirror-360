###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
# https://microsoft.github.io/pyright/#/builtins
# This file is only used for the Python extension on VScode
import builtins


# We just create a new definition for Undefined
Undefined: builtins.Undefined # pylint: disable=redefined-builtin, no-member
