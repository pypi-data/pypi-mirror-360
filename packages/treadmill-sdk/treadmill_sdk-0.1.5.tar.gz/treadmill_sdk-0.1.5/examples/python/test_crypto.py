"""
Treadmill SDK Encryption/Decryption Demo
Demonstrates encryption and decryption using the treadmill_sdk library.
"""

import treadmill_sdk
import logging
from logger import getLogger

# Configure logging
logger = getLogger(logging.INFO)

# Constants
PLAINTEXT = b"Hello, Device!"
# USER_ID = "550e8400-e29b-41d4-a716-446655440000"
# SN_CODE = "SN123456"


def demonstrate_crypto():
    """Demonstrate encryption and decryption process using treadmill_sdk."""
    try:
        # Alias for convenience
        libtml = treadmill_sdk

        # Display original plaintext
        logger.info(f"Plaintext: len={len(PLAINTEXT)}, hex={PLAINTEXT.hex()}")

        # Perform encryption
        # encrypted = libtml.encrypt(KEY, PLAINTEXT, USER_ID, SN_CODE)
        encrypted = libtml.encrypt(PLAINTEXT)
        # 去掉前 12 字节
        encrypted = bytes(encrypted[12:])
        logger.info(f"Encrypted: len={len(encrypted)}, hex={encrypted.hex()}")

        # Perform decryption
        # decrypted = libtml.decrypt(KEY, encrypted, USER_ID, SN_CODE)
        decrypted = libtml.decrypt(encrypted)
        logger.info(f"Decrypted: len={len(decrypted)}, hex={decrypted.hex()}")

        # Verify result
        if decrypted == PLAINTEXT:
            logger.warning("Decryption successful: plaintext restored correctly")
        else:
            logger.error("Decryption failed: plaintext not restored")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


def main():
    """Main entry point of the script."""
    demonstrate_crypto()


if __name__ == "__main__":
    main()
