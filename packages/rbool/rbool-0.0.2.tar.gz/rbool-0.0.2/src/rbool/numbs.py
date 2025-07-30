"""
This file contains the default functions and constant mathematical values
that are used as base for the entire package.

All the mathematical functions that are not implemented, like `sin` and `cos`
are the same from the standard `math` python's package.
The standard rational number is a instance from `fractions` standard package.

Other libraries offer other options to handle numerical numbers.
To do such, you need to overwrite these base functions and hence the
package will use your numerical type.
Example of use are:
* `numpy` offers `numpy.float64` instead of float
* `mpmath` offers the `mpmath.mpf` of arbitrary precision of float
* `sympy` offers `sympy.core.numbers.Rational` instead of `fractions.Fraction`
"""

from __future__ import annotations

import math
from fractions import Fraction
from numbers import Integral, Rational, Real
from typing import Any

NEGINF = -math.inf
POSINF = math.inf


class To:
    """
    Class to store static methods that checks objects,
    like being real, rationals, floats, integers, etc
    """

    @staticmethod
    def real(number: Any) -> Real:
        """
        Converts the number to a real number.

        Parameters
        ----------
        number : Any
            Number to be converted to a real number

        Returns
        -------
        Real
            The converted real number

        Examples
        --------
        >>> real(-1)
        -1
        >>> real(0)
        0
        >>> real(1)
        1
        >>> real(1.5)
        1.5
        >>> real(float("inf"))
        inf
        >>> real("inf")
        inf
        """
        if isinstance(number, Real):
            return number
        return float(number)

    @staticmethod
    def finite(number: Any) -> Real:
        """
        Converts the number to an finite number.

        Parameters
        ----------
        number : Any
            Number to be converted to an integer

        Returns
        -------
        Real
            The converted number in integer

        Raises
        ------
        ValueError
            If the number is not finite

        Examples
        --------
        >>> finite(-1)
        -1
        >>> finite(0)
        0
        >>> finite(1)
        1
        >>> finite(1.5)
        1.5
        """
        number = To.real(number)
        if not Is.finite(number):
            raise ValueError(f"{number} is not finite")
        return number

    @staticmethod
    def integer(number: Any) -> Integral:
        """
        Converts the number to an integer.

        Parameters
        ----------
        number : Real
            Number to be converted to an integer

        Returns
        -------
        int
            The converted number in integer

        Examples
        --------
        >>> integer(-1)
        -1
        >>> integer(0)
        0
        >>> integer(1)
        1
        """
        if isinstance(number, Integral):
            return number
        return int(number)

    @staticmethod
    def rational(numerator: Real, denominator: Real) -> Real:
        """
        Divide two rational numbers and return the result as a fraction.
        If any input is not integer/rational, performs standard division.

        Parameters
        ----------
        numerator : int or rational or float
            The numerator number
        denominator : int or rational or float
            The divisor number

        Returns
        -------
        Real
            A Fraction instance if inputs are integers/rational,
            otherwise a float

        Raises
        ------
        ZeroDivisionError
            If denominator is zero
        TypeError
            If inputs are not numeric types

        Notes
        -----
        This function preserves exact rational representation when inputs are
        integers or rational numbers. For example:


        Examples
        --------
        >>> rational(1, 2)
        Fraction(1, 2)
        >>> rational(12, 9)
        Fraction(4, 3)
        >>> rational(22, 7)
        Fraction(22, 7)
        """
        numerator = To.real(numerator)
        denominator = To.real(denominator)
        if not Is.rational(numerator) or not Is.rational(denominator):
            return numerator / denominator
        return Fraction(numerator, denominator)


class Is:
    """
    Class to store static methods that checks objects,
    like being real, rationals, floats, integers, etc
    """

    instance = isinstance

    @staticmethod
    def real(value: object) -> bool:
        """
        Check if a number is a real number.

        Parameters
        ----------
        value : object
            The object to check for being a number

        Returns
        -------
        bool
            True if the number is a number, False otherwise

        Examples
        --------
        >>> isreal(float("inf"))
        True
        >>> isreal(0)
        True
        >>> isreal("asd")
        False
        """
        return Is.instance(
            value,
            Real,
        )

    @staticmethod
    def finite(number: Real) -> bool:
        """
        Check if a number is finite.

        Parameters
        ----------
        number : Real
            The number to check for being finite

        Returns
        -------
        bool
            True if the number is finite, False otherwise

        Examples
        --------
        >>> isfinite(float("inf"))
        False
        >>> isfinite(0)
        True
        """
        return Is.real(number) and math.isfinite(number)

    @staticmethod
    def infinity(number: Real) -> bool:
        """
        Check if a number is negative or positive infinity.

        Parameters
        ----------
        number : Real
            The number to check for being infinity

        Returns
        -------
        bool
            True if the number is infinity, False otherwise

        Examples
        --------
        >>> isinfinity(-float("inf"))
        True
        >>> isinfinity(float("inf"))
        True
        >>> isinfinity(0)
        False
        """
        return Is.real(number) and math.isinf(number)

    @staticmethod
    def integer(number: Real) -> bool:
        """
        Check if a number is integer.

        Parameters
        ----------
        number : Real
            The number to check for being an integer

        Returns
        -------
        bool
            True if the number is rational, False otherwise

        Examples
        --------
        >>> is_rational(1)
        True
        >>> is_rational(1.2)
        False
        """
        return Is.instance(number, Integral)

    @staticmethod
    def rational(number: Real) -> bool:
        """
        Check if a number is integer or rational.

        Parameters
        ----------
        number : Real
            The number to check for rationality

        Returns
        -------
        bool
            True if the number is rational, False otherwise

        Examples
        --------
        >>> isrational(1)
        True
        >>> isrational(Fraction(1, 2))
        True
        >>> isrational(0.5)
        """
        return Is.real(number) and Is.instance(number, Rational)
