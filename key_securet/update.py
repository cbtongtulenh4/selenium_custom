import winreg as reg
import os
import subprocess
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.backends import default_backend

# ----------- PC Info Functions ------------

def get_wmic_value(command):
    try:
        result = subprocess.check_output(command, shell=True)
        lines = [x.strip() for x in result.decode().split('\n') if x.strip()]
        return lines[1] if len(lines) > 1 else ""
    except Exception as e:
        print(f"[ERROR] get_wmic_value({command}): {e}")
        return ""

def get_bios_serial_number():
    return get_wmic_value('wmic bios get serialnumber')

def get_system_uuid():
    return get_wmic_value('wmic csproduct get UUID')

def get_cpu_serial_number():
    return get_wmic_value('wmic cpu get ProcessorId')

def get_disk_serial_number():
    return get_wmic_value('wmic diskdrive get serialnumber')

def load_pc_info():
    return f"{get_bios_serial_number()}|{get_system_uuid()}|{get_cpu_serial_number()}|{get_disk_serial_number()}"

# ----------- Encryption Functions ------------

def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt(message, password, hex_format=False):
    salt = os.urandom(16)
    key = derive_key(password + "_abz", salt)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(message.encode()) + padder.finalize()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    result = salt + iv + ciphertext
    return result.hex().encode() if hex_format else result

def decrypt(ciphertext, password, hex_format=False):
    if hex_format:
        if isinstance(ciphertext, str):
            ciphertext = bytes.fromhex(ciphertext.replace('-', '').replace('{', '').replace('}', ''))
        else:
            ciphertext = bytes.fromhex(ciphertext.decode().replace('-', '').replace('{', '').replace('}', ''))
    salt = ciphertext[:16]
    iv = ciphertext[16:32]
    encrypted_message = ciphertext[32:]
    key = derive_key(password + "_abz", salt)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_message = decryptor.update(encrypted_message) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    message = unpadder.update(padded_message) + unpadder.finalize()
    return message.decode()

# ----------- Registry Functions ------------

def create_encrypted_registry_key(base, path, key_name, value_name, real_text, pass_text):
    try:
        # Điều hướng đến key
        current_key = base
        for part in path.split('\\'):
            try:
                current_key = reg.OpenKey(current_key, part, 0, reg.KEY_WRITE)
            except FileNotFoundError:
                current_key = reg.CreateKey(current_key, part)

        new_key = reg.CreateKey(current_key, key_name)
        encrypted_bytes = encrypt(real_text, pass_text + "_hp", hex_format=False)
        reg.SetValueEx(new_key, value_name, 0, reg.REG_BINARY, encrypted_bytes)
        reg.CloseKey(new_key)
        reg.CloseKey(current_key)
    except Exception as e:
        print(f"[ERROR] create_encrypted_registry_key: {e}")

def delete_registry_key(base, path, key_name=None, value_name=None):
    try:
        current_key = base
        for part in path.split('\\'):
            current_key = reg.OpenKey(current_key, part, 0, reg.KEY_WRITE)

        if key_name and value_name:
            # Xoá value
            key = reg.OpenKey(current_key, key_name, 0, reg.KEY_WRITE)
            reg.DeleteValue(key, value_name)
            reg.CloseKey(key)
        elif key_name:
            # Xoá key
            reg.DeleteKey(current_key, key_name)
        else:
            print("Chưa chỉ định key_name hoặc value_name để xóa.")
        reg.CloseKey(current_key)
    except Exception as e:
        print(f"[ERROR] delete_registry_key: {e}")

def get_encrypted_registry_value(base, path, key_name, value_name, pass_text):
    decrypted_text = None
    try:
        current_key = base
        for part in path.split('\\'):
            current_key = reg.OpenKey(current_key, part, 0, reg.KEY_READ)

        final_key = reg.OpenKey(current_key, key_name, 0, reg.KEY_READ)
        encrypted_bytes, regtype = reg.QueryValueEx(final_key, value_name)
        decrypted_text = decrypt(encrypted_bytes, pass_text + "_hp", hex_format=False)
        reg.CloseKey(final_key)
        reg.CloseKey(current_key)
    except Exception as e:
        print(f"[ERROR] get_encrypted_registry_value: {e}")
    return decrypted_text

# ----------- Optional: Format Functions (giữ lại nếu cần) ------------

def format_byte_string(byte_string):
    hex_string = byte_string.hex()
    n = len(hex_string) // 4
    formatted_string = '-'.join([hex_string[i:i + n] for i in range(0, len(hex_string), n)])
    formatted_string = '{' + formatted_string + '}'
    return formatted_string

def hex_to_bytes(formatted_hex_string):
    hex_string = formatted_hex_string.replace('-', '').replace('{', '').replace('}', '')
    byte_string = bytes.fromhex(hex_string)
    return byte_string

if __name__ == "__main__":
    key_base = reg.HKEY_CURRENT_USER
    key_path = "Software\\TestEncrypted"
    key_name = "SubKey"
    value_name = "MySecret"
    real_text = "Hello World, this is a secret!"
    password = "supersecure"

    print("PC Info:", load_pc_info())

    # Tạo key
    create_encrypted_registry_key(key_base, key_path, key_name, value_name, real_text, password)

    # Lấy giá trị
    value = get_encrypted_registry_value(key_base, key_path, key_name, value_name, password)
    print("Decrypted Registry Value:", value)

    # Xoá value (nếu muốn)
    # delete_registry_key(key_base, key_path, key_name, value_name)
