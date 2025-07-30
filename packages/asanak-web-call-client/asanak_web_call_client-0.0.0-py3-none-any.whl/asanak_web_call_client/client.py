import requests
import logging

class AsanakWebCallClient:
    BAD_REQUEST_ERROR = "bad request error."

    def __init__(self, username, password, base_url="https://callapi.asanak.com", logger=None):
        self.username = username
        self.password = password
        self.base_url = base_url.rstrip('/')
        self.logger = logger or logging.getLogger(__name__)

    def upload_new_voice(self, file_path):
        url = f"{self.base_url}/v1/upload/voice"
        files = {
            'username': (None, self.username),
            'password': (None, self.password),
            'file': open(file_path, 'rb')
        }
        response = requests.post(url, files=files)
        return self._process_response(response)

    def call_by_voice(self, voice_id, destination):
        return self._send_request('/v1/call/voice-file', {
            'voice_id': voice_id,
            'destination': destination,
        })

    def call_by_otp(self, code, destination):
        return self._send_request('/v1/call/otp', {
            'code': code,
            'destination': destination,
        })

    def call_status(self, call_ids):
        if isinstance(call_ids, list):
            call_ids = ','.join(call_ids)
        return self._send_request('/v1/report/callstatus', {
            'call_ids': call_ids,
        })

    def credit(self):
        return self._send_request('/v1/report/credit', {})

    def _send_request(self, endpoint, payload):
        url = f"{self.base_url}{endpoint}"
        payload.update({
            'username': self.username,
            'password': self.password
        })
        response = requests.post(url, json=payload, headers={'Accept': 'application/json'})
        return self._process_response(response)

    def _process_response(self, response):
        if self.logger:
            self.logger.info("Response", extra={'status_code': response.status_code, 'body': response.text})

        data = response.json()

        if not data.get('success'):
            raise RuntimeError(data.get('error', self.BAD_REQUEST_ERROR))

        return data
