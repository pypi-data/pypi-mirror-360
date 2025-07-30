import json
import decimal
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os


encryption_key = os.environ.get('ENCRYPTION_KEY')
if not encryption_key:
    raise ValueError("No encryption key set")
# Trim the key to 32 bytes if it is longer
if len(encryption_key) < 32:
    raise ValueError("ENCRYPTION_KEY must be at least 32 bytes long")
if len(encryption_key) > 32:
    encryption_key = encryption_key[:32]

key = encryption_key.encode('utf-8')

# Custom JSON encoder for Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def encrypt_data(data):
    try:
        # Convert the data to a JSON string with custom encoding
        data = json.dumps(data, cls=DecimalEncoder).encode('utf-8')

        # Pad the data to be compatible with AES block size
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()

        # Generate a random IV (initialization vector)
        iv = os.urandom(16)

        # Create a Cipher object to handle encryption
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Encrypt the data
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # Combine the IV and ciphertext and encode as base64 for storage or transmission
        encrypted_data = base64.b64encode(iv + ciphertext).decode('utf-8')
        
        return encrypted_data
    except Exception as e:
        raise ValueError(f"Encryption failed: {str(e)}")


def decrypt_data(encrypted_data):
    try:
        encrypted_data = base64.b64decode(encrypted_data)
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        decrypted_padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
        
        return decrypted_data
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")

def get_encrypted_password(username, password):
    return encrypt_data(password + username)
