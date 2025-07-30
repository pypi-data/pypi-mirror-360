from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from re import match as re_match
from typing import ClassVar
from string import ascii_uppercase, digits

from .base_option_symbol import BaseOptionSymbol
from .option_properties import OptionProperties


class DasOption(BaseOptionSymbol):
    NUMCHAR: ClassVar[str] = f'{digits}{ascii_uppercase}'

    @staticmethod
    def decimal_to_base(number: int, base: int) -> str:
        if number < base:
            return DasOption.NUMCHAR[number]
        return DasOption.decimal_to_base(number // base, base) \
            + DasOption.NUMCHAR[number % base]

    @staticmethod
    def starting_year() -> int:
        return (date.today().year - 10)//20 * 20 + 10

    @staticmethod
    def decode_date(symbolic_date: str) -> date:
        if len(symbolic_date) != 3:
            raise ValueError('Invalid date format')

        year = DasOption.starting_year() + int(symbolic_date[0], 20)
        month = int(symbolic_date[1], 16)
        day = int(symbolic_date[2], 32)

        return date(year, month, day)

    @staticmethod
    def decode_notation(symbol: str) -> OptionProperties:
        """
        +AAPL*C3I150.US -> (AAPL, US, -1, 150, 2022-03-18, C3I)
        """
        match = re_match(
            r'^\+(\D+(\d+)?)([*^])([A-Z0-9]{3})(\d+(\.\d*)?)(\.\w*)?$',
            symbol
        )

        if not match:
            raise ValueError(f'Invalid DAS option symbol: {symbol}')

        return OptionProperties(
            match.group(1),                                # ticker
            match.group(7)[1:] if match.group(7) else '',  # location
            1 if match.group(3) == '^' else -1,            # right
            Decimal(match.group(5)),                       # strike
            DasOption.decode_date(match.group(4)),         # expiration
            match.group(4)                                 # symbolic exp.
        )

    @staticmethod
    def encode_date(conventional_date: str | date | datetime) -> str:
        if isinstance(conventional_date, str):
            conventional_date = date.fromisoformat(conventional_date)

        year = DasOption.decimal_to_base(
            conventional_date.year - DasOption.starting_year(),
            20
        )
        month = DasOption.decimal_to_base(
            conventional_date.month,
            16
        )
        day = DasOption.decimal_to_base(
            conventional_date.day,
            32
        )

        return f'{year}{month}{day}'
