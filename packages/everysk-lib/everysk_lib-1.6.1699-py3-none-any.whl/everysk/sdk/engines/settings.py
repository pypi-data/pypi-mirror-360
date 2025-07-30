###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.fields import TupleField, IntField, ListField


ENGINES_EXPRESSION_DEFAULT_DATA_TYPES = TupleField(default=('cpp_var', 'str_var'), readonly=True)
ENGINES_CACHE_EXECUTION_EXPIRATION_TIME = IntField(default=14400, readonly=True)
ENGINES_MARKET_DATA_TICKER_TYPES = ListField(default=('everysk_symbol', 'everysk_id', None), readonly=True)
