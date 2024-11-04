import os
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from Crypto.Protocol.KDF import scrypt
from base64 import b64encode, b64decode


class DataEncryption:
    def __init__(self):
        self.aes_key_size = 32  # AES-256 requires a 32-byte key
        self.block_size = AES.block_size
        self.salt_size = 16

    def generate_rsa_key_pair(self, key_size=2048):
        """
        Generate a new RSA key pair.
        """
        key = RSA.generate(key_size)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        return private_key, public_key

    def encrypt_with_rsa(self, public_key, data):
        """
        Encrypt data using RSA public key.
        """
        rsa_key = RSA.import_key(public_key)
        cipher_rsa = PKCS1_OAEP.new(rsa_key)
        encrypted_data = cipher_rsa.encrypt(data)
        return b64encode(encrypted_data).decode('utf-8')

    def decrypt_with_rsa(self, private_key, encrypted_data):
        """
        Decrypt data using RSA private key.
        """
        encrypted_data = b64decode(encrypted_data)
        rsa_key = RSA.import_key(private_key)
        cipher_rsa = PKCS1_OAEP.new(rsa_key)
        return cipher_rsa.decrypt(encrypted_data)

    def derive_key(self, password, salt):
        """
        Derive a key using the scrypt KDF.
        """
        return scrypt(password, salt, self.aes_key_size, N=2**14, r=8, p=1)

    def encrypt_with_aes(self, password, data):
        """
        Encrypt data using AES with a password-derived key.
        """
        salt = get_random_bytes(self.salt_size)
        key = self.derive_key(password, salt)
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return b64encode(salt + cipher.nonce + tag + ciphertext).decode('utf-8')

    def decrypt_with_aes(self, password, encrypted_data):
        """
        Decrypt data encrypted with AES using a password-derived key.
        """
        decoded_data = b64decode(encrypted_data)
        salt = decoded_data[:self.salt_size]
        nonce = decoded_data[self.salt_size:self.salt_size + self.block_size]
        tag = decoded_data[self.salt_size + self.block_size:self.salt_size + self.block_size + 16]
        ciphertext = decoded_data[self.salt_size + self.block_size + 16:]
        key = self.derive_key(password, salt)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)

    def sign_data(self, private_key, data):
        """
        Sign data using RSA private key.
        """
        rsa_key = RSA.import_key(private_key)
        hash_value = SHA256.new(data)
        signature = pkcs1_15.new(rsa_key).sign(hash_value)
        return b64encode(signature).decode('utf-8')

    def verify_signature(self, public_key, data, signature):
        """
        Verify the RSA signature.
        """
        rsa_key = RSA.import_key(public_key)
        hash_value = SHA256.new(data)
        signature = b64decode(signature)
        try:
            pkcs1_15.new(rsa_key).verify(hash_value, signature)
            return True
        except (ValueError, TypeError):
            return False


def main():
    encryption_system = DataEncryption()

    # Generate RSA key pair for asymmetric encryption
    private_key, public_key = encryption_system.generate_rsa_key_pair()
    print("RSA Private Key:", private_key.decode('utf-8'))
    print("RSA Public Key:", public_key.decode('utf-8'))

    # Original data to be encrypted
    original_data = b"Sensitive data that requires encryption"

    # RSA Encryption
    encrypted_data_rsa = encryption_system.encrypt_with_rsa(public_key, original_data)
    print("Encrypted Data (RSA):", encrypted_data_rsa)

    # RSA Decryption
    decrypted_data_rsa = encryption_system.decrypt_with_rsa(private_key, encrypted_data_rsa)
    print("Decrypted Data (RSA):", decrypted_data_rsa.decode('utf-8'))

    # AES Encryption with password
    password = b"StrongPassword123"
    encrypted_data_aes = encryption_system.encrypt_with_aes(password, original_data)
    print("Encrypted Data (AES):", encrypted_data_aes)

    # AES Decryption
    decrypted_data_aes = encryption_system.decrypt_with_aes(password, encrypted_data_aes)
    print("Decrypted Data (AES):", decrypted_data_aes.decode('utf-8'))

    # Sign the original data with the private RSA key
    signature = encryption_system.sign_data(private_key, original_data)
    print("Signature:", signature)

    # Verify the signature using the public RSA key
    is_verified = encryption_system.verify_signature(public_key, original_data, signature)
    print("Signature Verified:", is_verified)


if __name__ == "__main__":
    main()