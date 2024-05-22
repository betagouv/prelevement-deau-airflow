import base64


def decode64(code: str):
    encoded_string = code
    decoded_bytes = base64.b64decode(encoded_string)
    decoded_string = decoded_bytes.decode('utf-8')
    return decoded_string
