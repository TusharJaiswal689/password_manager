import asyncio
import pyperclip

async def copy_and_secure_clear(text:str, delay_seconds: int=15):
    #1 copy password to clipboard
    pyperclip.copy(text)

    #2 Wait for 15 seconds before removing password from clipboard
    await asyncio.sleep(delay_seconds)
    if pyperclip.paste() == text:
        pyperclip.copy("")