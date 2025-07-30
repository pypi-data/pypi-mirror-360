import re
import json
import requests
from urllib.parse import quote

class WhatsAppSender:
    def __init__(self, instance_id, access_token, base_url="https://chat.laxicon.in"):
        self.instance_id = instance_id
        self.whatsapp_access_token = access_token
        self.whatsapp_url = base_url

    def get_whatsapp_url(self):
        url = self.whatsapp_url or """https://chat.laxicon.in"""
        url += "/api/send?"
        url += "instance_id=" + str(self.instance_id)
        url += "&access_token=" + str(self.whatsapp_access_token)
        return url


    def send_to_whatsapp(self, data: dict):
        """
        data = {
            "number": "911234567890",
            "message": "Hello there!",
            "filename": "image.jpg",         # Optional
            "media_url": "https://..."       # Optional
        }
        """
        url = self.get_whatsapp_url()
        number = data.get("number", "")
        text = data.get("message", "")
        filename = data.get("filename", "")
        media_url = data.get("media_url", None)

        # Clean phone number
        number = re.sub(r'\D', '', number.strip().replace("+", ""))

        # Encode media URL if present
        encode_media_url = ''
        if media_url:
            url_parts = media_url.split("/")
            encoded_url = quote(url_parts[0], safe='')  # e.g., https
            encoded_url += "/" + "/".join(quote(part, safe='') for part in url_parts[1:])
            encode_media_url = encoded_url

        # Build full URL
        url += "&number=" + str(number)
        url += "&message=" + text
        url += "&type=" + ("media" if media_url else "text")
        if media_url:
            url += "&media_url=" + encode_media_url
            url += "&filename=" + filename

        # Send request
        headers = {'Content-Type': 'application/json'}
        res = requests.post(url, headers=headers)

        if res.status_code == 200:
            print("MESSAGE SENT")
            response_data = json.loads(res.text)
            if isinstance(response_data, dict) and response_data.get('status') == 'success':
                return True
        return False





            
    