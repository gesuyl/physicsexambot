def remove_control_chars(s):
    escapes = ''.join([chr(char) for char in range(1, 32)])
    translator = str.maketrans('', '', escapes)
    return s.translate(translator)


def admin_check(username, reader): return str(username) in reader.admins


def access_check(username, reader): return str(username) in reader.users.keys 
