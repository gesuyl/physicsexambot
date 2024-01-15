def remove_control_chars(s) -> str:
    escapes = ''.join([chr(char) for char in range(1, 32)])
    translator = str.maketrans('', '', escapes)
    return s.translate(translator)


def admin_check(username, reader) -> bool:
    return str(username) in reader.admins


def access_check(username, reader) -> bool:
    return str(username) in reader.users.keys
