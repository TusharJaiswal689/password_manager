import secrets
import string

def pass_generator(x, s, n):
    letters = [secrets.choice(string.ascii_letters) for _ in range(x)]
    special_chars = [secrets.choice(string.digits) for _ in range(n)]
    numbers = [secrets.choice("!@#$%^&*()_+=-[]{}|;:,.<>?") for _ in range(s)]
    password_list=(letters + special_chars + numbers)
    secrets.SystemRandom().shuffle(password_list)
    password = "".join(password_list)
    return "".join(password)
