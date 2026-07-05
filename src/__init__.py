from crypto import generate_secure_password, CryptoVault
import getpass
import secrets

try:
    master = getpass.getpass("Enter your master password: ")
    x = int(input("Enter the total length of the password: "))
    s = int(input("Enter the number of special characters: "))
    n = int(input("Enter the number of numeric characters: "))
    
    if s + n > x:
        print("The sum of special and numeric characters cannot exceed the total length.")
    else:
        x -= (s + n)
        
        # 1. Generate the raw password
        raw_password = generate_secure_password(x, s, n)
        print(f"Generated Raw Password: {raw_password}")

        # 2. Setup the Vault
        vault = CryptoVault()
        my_salt = secrets.token_bytes(16)
        my_iv = secrets.token_bytes(12)

        # 3. Unlock vault and Encrypt
        vault.derive_key(master, my_salt)
        ciphertext = vault.encrypt(raw_password, my_iv)
        print(f"Encrypted Ciphertext (Bytes): {ciphertext}")

        # 4. Decrypt
        deciphertext = vault.decrypt(ciphertext, my_iv)
        print(f"Deciphered text: {deciphertext}")

except ValueError:
    print("Please enter valid integers.")