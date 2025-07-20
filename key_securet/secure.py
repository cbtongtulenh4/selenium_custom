import winreg as reg
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os
import subprocess


def get_bios_serial_number():
    try:
        result = subprocess.check_output('wmic bios get serialnumber', shell=True)
        serial = result.decode().split('\n')[1].strip()
        return serial
    except Exception as e:
        return ""

def get_system_uuid():
    try:
        result = subprocess.check_output('wmic csproduct get UUID', shell=True)
        uuid = result.decode().split('\n')[1].strip()
        return uuid
    except Exception as e:
        return ""

def get_cpu_serial_number():
    try:
        result = subprocess.check_output('wmic cpu get ProcessorId', shell=True)
        cpu_id = result.decode().split('\n')[1].strip()
        return cpu_id
    except Exception as e:
        return ""

def get_disk_serial_number():
    try:
        result = subprocess.check_output('wmic diskdrive get serialnumber', shell=True)
        disk_serial = result.decode().split('\n')[1].strip()
        return disk_serial
    except Exception as e:
        return ""

def load_pc_info():
    return f"{get_bios_serial_number()}|{get_system_uuid()}|{get_cpu_serial_number()}|{get_disk_serial_number()}"

def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt(message, password, hex=True):
    salt = os.urandom(16)
    key = derive_key(password+"_abz", salt)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(message.encode()) + padder.finalize()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    rs = salt + iv + ciphertext
    if hex:
        rs = format_byte_string(rs)
    return rs

def decrypt(ciphertext, password, hex=True):
    if hex:
        ciphertext = hex_to_bytes(ciphertext)
    salt = ciphertext[:16]
    iv = ciphertext[16:32]
    encrypted_message = ciphertext[32:]
    key = derive_key(password+"_abz", salt)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_message = decryptor.update(encrypted_message) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    message = unpadder.update(padded_message) + unpadder.finalize()
    return message.decode()

def format_byte_string(byte_string):
    hex_string = byte_string.hex()
    n = len(hex_string) // 4
    formatted_string = '-'.join([hex_string[i:i+n] for i in range(0, len(hex_string), n)])
    formatted_string = '{' + formatted_string + '}'
    return formatted_string

def hex_to_bytes(formatted_hex_string):
    hex_string = formatted_hex_string.replace('-', '').replace('{', '').replace('}', '')
    byte_string = bytes.fromhex(hex_string)
    return byte_string

def create_encrypted_registry_key(base, path, key_name, value_name, real_text, pass_text):
    try:
        current_key = base
        for part in path.split('\\'):
            try:
                current_key = reg.OpenKey(current_key, part, 0, reg.KEY_WRITE)
            except FileNotFoundError:
                current_key = reg.CreateKey(current_key, part)

        new_key = reg.CreateKey(current_key, key_name)
        
        reg.SetValueEx(new_key, value_name, 0, reg.REG_SZ, encrypt(real_text, pass_text+"_hp"))
        reg.CloseKey(new_key)
        reg.CloseKey(current_key)
    except:
        pass

def delete_registry_key(base, path, key_name, value_name):
    try:
        current_key = base
        for part in path.split('\\'):
            try:
                current_key = reg.OpenKey(current_key, part, 0, reg.KEY_WRITE)
            except FileNotFoundError:
                current_key = reg.CreateKey(current_key, part)

        key = reg.OpenKey(base, path, key_name, reg.KEY_WRITE)
        reg.DeleteKey(key, value_name)
        reg.CloseKey(key)
    except:
        pass

def get_encrypted_registry_value(base, path, key_name, value_name, pass_text):
    decrypted_text = None
    try:
        current_key = base
        for part in path.split('\\'):
            current_key = reg.OpenKey(current_key, part, 0, reg.KEY_READ)
        
        final_key = reg.OpenKey(current_key, key_name, 0, reg.KEY_READ)
        encrypted_text, _ = reg.QueryValueEx(final_key, value_name)
        decrypted_text = decrypt(encrypted_text, pass_text+"_hp")
        
        reg.CloseKey(final_key)
        reg.CloseKey(current_key)
    except:
        pass
    finally:
        try:
            reg.CloseKey(final_key)
        except:
            pass
        try:
            reg.CloseKey(current_key)
        except:
            pass
    return decrypted_text