###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from typing import Tuple

from everysk.config import settings
from everysk.sdk.base import BaseSDK


###############################################################################
#   Expression Class Implementation
###############################################################################
class Expression(BaseSDK):

    def get_tokens(self, expression: str, data_types: Tuple[str] = settings.ENGINES_EXPRESSION_DEFAULT_DATA_TYPES) -> frozenset:
        """
        Get the tokens of an expression. In other words, extract the
        elements used in the expression.

        Args:
            expression (str): The expression to get the tokens of.
            data_types (Tuple[str], optional): The data types to use for tokenization. Default is settings.ENGINES_EXPRESSION_DEFAULT_DATA_TYPES.

        Returns:
            frozenset: The tokens of the expression.

        Example:
            >>> expression = Expression()
            >>> expression.get_tokens('a + b')
            {'a', 'b'}
        """
        return self.get_response(self_obj=self ,params={'expression': expression, 'data_types': data_types})

    def solve(self, expression: str, user_args: dict):
        """
        Solve an expression with user arguments. Each key inside
        the `user_args` dictionary will be used as a value to solve
        the `expression` operation.

        Args:
            expression (str): The expression to solve.
            user_args (dict): The user arguments to use for solving.

        Returns:
            Any: The result of the expression.

        Example:
            >>> expression = Expression()
            >>> expression.solve('a + b', {'a': 1, 'b': 2})
            3
        """
        return self.get_response(self_obj=self, params={'expression': expression, 'user_args': user_args})
