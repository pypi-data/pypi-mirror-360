"""
captcha_utils.py

This module provides a function to validate Google reCAPTCHA responses,
supporting both v2 and v3 reCAPTCHA verification.

Key functionality:
- Validate user response tokens with Google's reCAPTCHA verification API
- Supports optional parameters like site key and user IP for enhanced validation
- Returns detailed validation result including success status, timestamp, score, and action

Dependencies:
- requests>=2.31.0
- Python 3.8+

Author: Paavan Boddeda
Organization: ennVee TechnoGroup
"""


import requests 

def validate_captcha(
    secret_key: str,
    user_response: str,
    site_key: str = None,
    remote_ip: str = None
) -> dict:
    """
    Validate Google reCAPTCHA response
    
    Mandatory Parameters:
    - secret_key: Google reCAPTCHA secret key
    - user_response: User's response token
    
    Optional Parameters:
    - site_key: Site key for verification (v2 optional)
    - remote_ip: User's IP address for enhanced validation
    
    Returns: Validation result with score/action
    """
    if not secret_key or not user_response:
        # raise CaptchaError("Missing mandatory captcha parameters")
        return {"status": "error", "message": "Missing mandatory captcha parameters"}
    
    api_url = "https://www.google.com/recaptcha/api/siteverify"
    payload = {
        "secret": secret_key,
        "response": user_response
    }
    
    if remote_ip:
        payload["remoteip"] = remote_ip
    
    try:
        response = requests.post(api_url, data=payload, timeout=10)
        result = response.json()
        
        if not result.get("success"):
            return {"status": "error", "message": "Captcha validation failed"}
        
        return {
            "success": True,
            "timestamp": result.get("challenge_ts"),
            "hostname": result.get("hostname"),
            "score": result.get("score", 1.0),  # v3 returns score
            "action": result.get("action")       # v3 returns action
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}