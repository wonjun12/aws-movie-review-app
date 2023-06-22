from passlib.hash import pbkdf2_sha256

from config import Setting

def password_hash_change(origin_password):
    password = pbkdf2_sha256.hash(origin_password + Setting.SALT)
    return password

def check_password(original_password, hashed_password):
    check = pbkdf2_sha256.verify(original_password+Setting.SALT, hashed_password)
    return check