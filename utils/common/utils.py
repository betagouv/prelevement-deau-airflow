import base64


def decode64(code: str) -> str:
    encoded_string = code
    decoded_bytes = base64.b64decode(encoded_string)
    decoded_string = decoded_bytes.decode("utf-8")
    return decoded_string


def encode64(code: str) -> str:
    message_bytes = code.encode("utf-8")
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode("utf-8")
    return base64_message


def get_file_extension(file_name: str) -> str:
    if "." not in file_name:
        return file_name
    return file_name.split(".")[-1]


def dataframe_to_sqlalchemy_objects(df, model):
    objects = []
    for _, row in df.iterrows():
        obj = model(**row.to_dict())
        objects.append(obj)
    return objects


def open_file(path: str) -> str:
    with open(path) as f:
        return f.read()
