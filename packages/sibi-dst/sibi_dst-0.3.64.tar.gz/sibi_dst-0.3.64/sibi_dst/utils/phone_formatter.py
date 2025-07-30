import re
from enum import Enum
from typing import Optional, Union, Callable

class CountryCode(Enum):
    """Enum for supported country codes, including phone number length and formatting rules."""

    USA = ("1", 10, lambda number: f"({number[:3]}) {number[3:6]}-{number[6:]}")
    UK = ("44", 10, lambda number: f"{number[:2]} {number[2:6]} {number[6:]}")
    FRANCE = ("33", 9, lambda number: f"{number[:1]} {number[1:3]} {number[3:5]} {number[5:]}")
    SPAIN = ("34", 9, lambda number: f"{number[:2]} {number[2:5]} {number[5:]}")
    DEFAULT = ("506", 8, lambda number: f"{number[:4]}-{number[4:]}")

    def __init__(self, code: str, length: int, formatter: Callable[[str], str]):
        """
        Initialize a CountryCode enum member.

        :param code: The country code.
        :type code: str
        :param length: The expected length of the phone number (excluding the country code).
        :type length: int
        :param formatter: A function to format the phone number.
        :type formatter: Callable[[str], str]
        """
        self.code = code
        self.length = length
        self.formatter = formatter

    @property
    def value(self) -> str:
        """
        Get the country code value.

        :return: The country code.
        :rtype: str
        """
        return self.code

    def validate_length(self, number: str) -> bool:
        """
        Validate the length of the phone number for this country.

        :param number: The phone number part to validate.
        :type number: str
        :return: True if the number length is valid, False otherwise.
        :rtype: bool
        """
        return len(number) == self.length

    def format_number(self, number: str) -> str:
        """
        Format the phone number according to this country's rules.

        :param number: The phone number part to format.
        :type number: str
        :return: The formatted number.
        :rtype: str
        """
        return self.formatter(number)

class PhoneNumberFormatter:
    """
    A utility class for validating and formatting phone numbers based on country-specific rules.

    The class supports phone numbers for the UK, USA, France, and Spain. It detects the country code
    from the input or uses a default country code if missing. Phone numbers are formatted according
    to country-specific rules.
    """

    def __init__(self, default_country_code: CountryCode = CountryCode.DEFAULT):
        """
        Initialize the PhoneNumberFormatter with a default country code.

        :param default_country_code: The default country code to use if missing.
        :type default_country_code: CountryCode
        """
        self.default_country_code = default_country_code

    def format_phone_number(self, phone_number: Union[str, int, float]) -> Optional[str]:
        """
        Validate and format a phone number according to country-specific rules.

        If the input is numeric (e.g., an integer or float), it will be converted to a string.
        If the country code is missing, the default country code will be used. The phone number
        will be formatted according to the detected country's rules.

        :param phone_number: The phone number to validate and format. Can be a string, integer, or float.
        :type phone_number: Union[str, int, float]
        :return: The formatted phone number, or None if the input is invalid.
        :rtype: Optional[str]
        """
        # Convert numeric input to string
        if isinstance(phone_number, (int, float)):
            phone_number = str(int(phone_number))  # Convert to integer first to remove decimal points

        # Remove all non-digit characters
        digits = re.sub(r"\D", "", phone_number)

        # Validate the length of the phone number
        if not digits or len(digits) < 7:  # Minimum length for a valid phone number
            return None

        # Detect the country code
        country_code, number = self._detect_country_code(digits)

        # Validate the number length for the detected country
        if not country_code.validate_length(number):
            return None

        # Format the phone number based on the country code
        formatted_number = country_code.format_number(number)

        return f"+{country_code.value} {formatted_number}"

    def _detect_country_code(self, digits: str) -> tuple[CountryCode, str]:
        """
        Detect the country code from the input digits.

        :param digits: The phone number digits (without non-digit characters).
        :type digits: str
        :return: A tuple containing the detected country code and the remaining number.
        :rtype: tuple[CountryCode, str]
        """
        for country_code in CountryCode:
            if digits.startswith(country_code.value):
                return country_code, digits[len(country_code.value):]
        return self.default_country_code, digits