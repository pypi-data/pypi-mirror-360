import os
import base64
import mimetypes
import requests

def email_service(
    client_id: str,
    tenant_id: str,
    client_secret: str,
    from_address: str,
    to_address: list[str],
    body: str,
    subject: str = "",
    attachments: list[str] = None,
    cc: list[str] = None,
    bcc: list[str] = None,
    content_type: str = "HTML",
    save_to_sent_items: bool = False
) -> dict:
    """
    Send email using Microsoft Graph API
    
    Mandatory Parameters:
    - client_id: Azure AD application ID
    - tenant_id: Azure AD tenant ID
    - client_secret: Application secret
    - from_address: Sender's email (must be registered in Azure AD)
    - to_address: List of recipient emails
    - body: Email content body
    
    Optional Parameters:
    - subject: Email subject (default: empty)
    - attachments: List of file paths
    - cc: List of CC emails
    - bcc: List of BCC emails
    - content_type: 'HTML' or 'Text' (default: 'HTML')
    - save_to_sent_items: Save copy in sent folder (default: False)
    
    Returns: Dict with operation status
    """
    # Validate mandatory fields
    if not all([client_id, tenant_id, client_secret, from_address, to_address, body]):
        return {"status": "error", "message": "Missing mandatory parameters"}
    
    # Get access token
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials'
    }
    
    try:
        token_r = requests.post(token_url, data=token_data)
        token_r.raise_for_status()
        access_token = token_r.json()['access_token']
    except Exception as e:
        return {"status": "error", "message": str(e)}

    # Build email message
    message = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": content_type,
                "content": body
            },
            "toRecipients": [{"emailAddress": {"address": addr}} for addr in to_address],
            "attachments": []
        },
        "saveToSentItems": save_to_sent_items
    }
    
    # Add optional fields
    if cc:
        message["message"]["ccRecipients"] = [{"emailAddress": {"address": addr}} for addr in cc]
    if bcc:
        message["message"]["bccRecipients"] = [{"emailAddress": {"address": addr}} for addr in bcc]
    
    # Process attachments
    if attachments:
        for file_path in attachments:
            if not os.path.isfile(file_path):
                # raise EmailServiceError(f"Attachment not found: {file_path}")
                return {"status": "error", "message": f"Attachment not found: {file_path}"}
            
            with open(file_path, "rb") as f:
                file_data = f.read()
            
            file_name = os.path.basename(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or "application/octet-stream"
            
            message["message"]["attachments"].append({
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": file_name,
                "contentType": mime_type,
                "contentBytes": base64.b64encode(file_data).decode("utf-8")
            })

    # Send email
    send_url = f"https://graph.microsoft.com/v1.0/users/{from_address}/sendMail"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(send_url, headers=headers, json={"message": message["message"]})
        response.raise_for_status()
        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    

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
    
    
def add11(a, b):
    return a + b

def sub11(a, b):
    return a - b