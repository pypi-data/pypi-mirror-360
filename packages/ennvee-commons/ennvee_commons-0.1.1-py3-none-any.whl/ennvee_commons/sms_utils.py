"""
sms_utils.py

This module provides utility functions for sending OTP (One-Time Password)
messages via SMS using Twilio, as well as generating random OTPs.

Dependencies:
- twilio>=8.0.0
- Python 3.8+

Author: Paavan Boddeda
Organization: ennVee TechnoGroup
"""

import random
from twilio.rest import Client


def generate_otp(length: int = 6) -> str:
    """
    Generate a numeric OTP (One-Time Password) of the given length.

    Args:
        length (int): Length of the OTP to generate (default is 6).

    Returns:
        str: A numeric OTP as a string.

    Example:
        >>> generate_otp(4)
        '4821'
    """
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def send_otp(
    mobile_number: str,
    twilio_sid: str,
    twilio_token: str,
    twilio_number: str,
    sender_name: str = "App"
) -> tuple[str, str]:
    """
    Send an OTP via SMS using Twilio.

    Args:
        mobile_number (str): The recipient's phone number (E.164 format, e.g., "+14155552671").
        twilio_sid (str): Twilio Account SID.
        twilio_token (str): Twilio Auth Token.
        twilio_number (str): Twilio registered phone number used to send the SMS.
        sender_name (str, optional): Name to include in the message body (default is "App").

    Returns:
        tuple: A tuple containing:
            - message SID (str): Twilio message identifier.
            - otp (str): The OTP sent to the user.

    Raises:
        Exception: If Twilio credentials are missing or message sending fails.

    Example:
        >>> sid, otp = send_otp("+14155552671", "ACxxxx", "auth_token", "+14155550123")
    """
    if not all([twilio_sid, twilio_token, twilio_number]):
        raise Exception("Missing Twilio credentials")

    client = Client(twilio_sid, twilio_token)
    otp = generate_otp()

    message = client.messages.create(
        body=f"Your OTP for {sender_name} is: {otp}",
        from_=twilio_number,
        to=mobile_number
    )

    return message.sid, otp
