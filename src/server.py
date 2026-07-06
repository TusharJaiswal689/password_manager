import asyncio
import secrets
import tkinter as tk
from tkinter import simpledialog

from mcp.server.fastmcp import FastMCP

from crypto import CryptoVault , generate_secure_password
from db import DatabaseManager
from clipboard import copy_and_secure_clear

mcp =FastMCP("Local Password Manager")
db = DatabaseManager()
vault = CryptoVault()

def prompt_for_master_password() -> str:
    root = tk.Tk()
    root.withdraw() # Hides the main background window
    
    # Prompt the user
    master = simpledialog.askstring("Vault Lock", "Enter Master Password:", show="*")
    root.destroy() # Cleans up tkinter completely
    
    if master:
        return master
    else:
        # Stop the program if they hit cancel, don't return a fake password!
        raise ValueError("Authentication cancelled by user.")


async def ensure_vault_unlocked():
    # 1. Ensure database is connected on the correct event loop
    if db.pool is None:
        await db.connect()
        await db.setup_database()
        
    # 2. Unlock vault if needed
    if vault.key == None:
        master = prompt_for_master_password()
        master_salt = await db.get_or_create_salt()
        vault.derive_key(master, master_salt)
    
@mcp.tool()
async def create_new_password(website:str, username:str, length: int=16, symbols: int=2, digits: int=4) -> str:
    await ensure_vault_unlocked()
    raw_password=generate_secure_password(length, symbols, digits)
    my_iv = secrets.token_bytes(12)
    ciphertext = vault.encrypt(raw_password, my_iv)

    await db.save_credential(
        website=website,
        username=username,
        ciphertext=ciphertext,
        iv=my_iv
    ) 
    return f"Successfully generated, encrypted, and saved a new password for {website} ({username})."

@mcp.tool()
async def get_password(website:str, username:str) -> str:
    await ensure_vault_unlocked()
    ciphertext, iv = await db.get_credential(website, username)
    if not ciphertext:
        return "No password found for given account"
    else:
        plaintext = vault.decrypt(ciphertext, iv)
        copy_and_secure_clear(plaintext)
        
if __name__ == "__main__":

    mcp.run(transport='stdio')
