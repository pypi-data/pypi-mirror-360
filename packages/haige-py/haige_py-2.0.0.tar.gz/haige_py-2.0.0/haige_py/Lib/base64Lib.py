import base64


def file_to_base64(file_path):
    with open(file_path, 'rb') as file:
        file_content = file.read()
        base64_content = base64.b64encode(file_content)
        return base64_content.decode('utf-8')


def base64_to_file(base64_str, output_path):
    file_content = base64.b64decode(base64_str.encode('utf-8'))
    with open(output_path, 'wb') as file:
        file.write(file_content)


def base64_to_bytes(base64_str):
    return base64.b64decode(base64_str)
