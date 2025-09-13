import requests

from notifier import Notifier

class SMSNotifier(Notifier):
    """Send SMS notifications using a configured API."""

    def __init__(self, api_key: str = "", url: str = "https://api.semaphore.co/api/v4/priority") -> None:
        self.api_key = api_key
        self.url = url

    def send(self, to_phone_number: str, message: str) -> None:
        print("PHONE NUMBER", to_phone_number)
        print("MESSAGE", message)

        payload = {
            "apikey": self.api_key,
            "number": to_phone_number,
            "message": message,
        }

        try:
            response = requests.post(self.url, data=payload)

            if response.status_code == 200:
                print("SEND MESSAGE SUCCESS")
                print(response.json())
            else:
                print(response.text)
                print("ERROR SENDING MESSAGE")
                print("STATUS CODE", response.status_code)
        except requests.exceptions.RequestException as req_exc:
            print("Request Exception:", req_exc)
        except Exception as e:
            print("Failed to send message", e)
