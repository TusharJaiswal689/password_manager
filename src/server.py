import secrets
import tkinter as tk
from tkinter import simpledialog, messagebox

from mcp.server.fastmcp import FastMCP

from crypto import CryptoVault , generate_secure_password
from db import DatabaseManager
from clipboard import copy_and_secure_clear
from schema import CreatePasswordSchema, GetPasswordSchema

mcp =FastMCP("Local Password Manager")
db = DatabaseManager()
vault = CryptoVault()

def prompt_for_master_password() -> str:
    root = tk.Tk()
    root.withdraw() # Hides the main background window
    
    # Loop so they can try again if they fail the strength check
    while True: 
        # Prompt the user
        master = simpledialog.askstring("Vault Lock", "Enter Master Password (Min 12 chars):", show="*")
        
        # 1. Did they hit cancel?
        if master is None:
            root.destroy() # Cleans up tkinter completely
            raise ValueError("Authentication cancelled by user.")
            
        # 2. Is the password too weak?
        if len(master) < 12:
            # Pop up a native OS error message!
            messagebox.showerror(
                "Weak Password", 
                "Your Master Password is the only thing protecting your vault.\n\nIt must be at least 12 characters long. Please try again."
            )
            continue # This pushes them back to the start of the while loop
            
        # 3. If it passes all checks, return it
        root.destroy() 
        return master

async def ensure_vault_unlocked():
    # 1. Ensure database is connected on the correct event loop
    if db.pool is None:
        await db.connect()
        await db.setup_database()
        
    # 2. Unlock vault if needed
    if vault.key == None:
        master = prompt_for_master_password()
        master_salt = await db.authenticate_or_setup(master)
        vault.derive_key(master, master_salt)
    
@mcp.tool()
async def create_new_password(params: CreatePasswordSchema) -> str:
    await ensure_vault_unlocked()
    raw_password=generate_secure_password(params.length, params.symbols, params.digits)
    my_iv = secrets.token_bytes(12)
    ciphertext = vault.encrypt(raw_password, my_iv)

    await db.save_credential(
        website=params.website,
        username=params.username,
        ciphertext=ciphertext,
        iv=my_iv
    ) 
    return f"Successfully generated, encrypted, and saved a new password for {params.website} ({params.username})."

@mcp.tool()
async def get_password(params: GetPasswordSchema) -> str:
    await ensure_vault_unlocked()
    ciphertext, iv = await db.get_credential(params.website, params.username)
    if not ciphertext:
        return "No password found for given account"
    else:
        plaintext = vault.decrypt(ciphertext, iv)
        await copy_and_secure_clear(plaintext)
        return "Successfully found the password and copied it to the clipboard. Do not ask me what it is."

if __name__ == "__main__":

    mcp.run(transport='stdio')
