"""Encryption utilities for securing user data."""
from cryptography.fernet import Fernet, InvalidToken
import os
from pathlib import Path
import base64
from .exceptions import EncryptionError
from .logger import logger

def get_or_create_key() -> bytes:
    """Get existing encryption key or create a new one.
    
    Returns:
        bytes: The encryption key
        
    Raises:
        EncryptionError: If key cannot be accessed or created
    """
    try:
        key_file = Path.home() / ".sentence_completion" / "key.key"
        key_file.parent.mkdir(exist_ok=True)
        
        if key_file.exists():
            key = key_file.read_bytes()
            logger.info("Successfully loaded existing encryption key")
        else:
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            logger.info("Successfully created new encryption key")
            
        return key
        
    except Exception as e:
        logger.error(f"Failed to access encryption key: {str(e)}")
        raise EncryptionError("Could not access encryption key") from e

def encrypt_data(data: str) -> bytes:
    """Encrypt the given string data.
    
    Args:
        data: String to encrypt
        
    Returns:
        bytes: Encrypted data
        
    Raises:
        EncryptionError: If encryption fails
    """
    try:
        key = get_or_create_key()
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        logger.debug("Successfully encrypted data")
        return encrypted_data
        
    except Exception as e:
        logger.error(f"Failed to encrypt data: {str(e)}")
        raise EncryptionError("Could not encrypt data") from e

def decrypt_data(encrypted_data: bytes) -> str:
    """Decrypt the given encrypted data.
    
    Args:
        encrypted_data: Data to decrypt
        
    Returns:
        str: Decrypted string
        
    Raises:
        EncryptionError: If decryption fails
    """
    try:
        key = get_or_create_key()
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data).decode()
        logger.debug("Successfully decrypted data")
        return decrypted_data
        
    except InvalidToken:
        logger.error("Invalid or corrupted encrypted data")
        raise EncryptionError("Data is corrupted or was encrypted with a different key")
        
    except Exception as e:
        logger.error(f"Failed to decrypt data: {str(e)}")
        raise EncryptionError("Could not decrypt data") from e 