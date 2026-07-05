from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import secrets
import string

def generate_secure_password(length: int, num_symbols: int, num_digits: int) -> str:
    """Generates a random password string."""
    letters = [secrets.choice(string.ascii_letters) for _ in range(length)]
    symbols = [secrets.choice("!@#$%^&*()_+=-[]{}|;:,.<>?") for _ in range(num_symbols)]
    digits = [secrets.choice(string.digits) for _ in range(num_digits)]
    
    password_list = letters + digits + symbols
    secrets.SystemRandom().shuffle(password_list)
    return "".join(password_list)

class CryptoVault:
    def __init__(self):
        # The key stays hidden in this class instance while the app is running
        self.key = None

    def derive_key(self, master_password: str, salt: bytes):
        """Derives the AES key from the master password and salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=600_000, # Updated to modern OWASP standards
        )
        self.key = kdf.derive(master_password.encode('utf-8'))

    def encrypt(self, plaintext: str, iv: bytes) -> bytes:
        """Encrypts a string using the derived key."""
        if not self.key:
            raise ValueError("Vault is locked. Derive key first.")
        
        cipher = AESGCM(self.key)
        return cipher.encrypt(iv, plaintext.encode('utf-8'), None)

    def decrypt(self, ciphertext: bytes, iv: bytes) -> str:
        """Decrypts bytes back into a string."""
        if not self.key:
            raise ValueError("Vault is locked. Derive key first.")
        
        cipher = AESGCM(self.key)
        decrypted_bytes = cipher.decrypt(iv, ciphertext, None)
        return decrypted_bytes.decode('utf-8')
     