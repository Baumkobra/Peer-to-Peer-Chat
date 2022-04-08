from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import AES
from Message import debug
import os
# create a private key public key 
def create_rsa_keypair(key_size=2048):
    new_key = RSA.generate(key_size)
    public_key = new_key.publickey().exportKey("PEM")
    private_key = new_key.exportKey("PEM")
    return public_key, private_key


def encrypt_rsa(public_key, message:bytes):
    # encrypt the message
    if type(message) != bytes: message = message.encode()
    debug(f"encrypyting rsa {message}")
    public_key = RSA.importKey(public_key)
    encryptor = PKCS1_OAEP.new(public_key)
    encrypted_msg = encryptor.encrypt(message)
    debug(f"encrypted rsa {encrypted_msg}")
    return encrypted_msg

def decrypt_rsa(private_key, message:bytes):
    # decrypt the message
    if type(message) != bytes: message = message.encode()
    debug(f"decrypting rsa{message}")
    private_key = RSA.importKey(private_key)
    decryptor = PKCS1_OAEP.new(private_key)
    decrypted_msg = decryptor.decrypt(message)
    debug(f"decrypted rsa {decrypted_msg}")
    return decrypted_msg

#create a aes key
def create_aes_key():
    return os.urandom(32)

#encrypt using an aes key
def encrypt_aes(aes_key, message:bytes):
    debug("encrypting aes") 
    if type(message) != bytes: message = message.encode()
    iv = os.urandom(16)	
    cipher = AES.new(aes_key, AES.MODE_CFB, iv)
    encrypted_msg = iv + cipher.encrypt(message)
    debug(f"encrypted aes {encrypted_msg}")
    return encrypted_msg

#decrypt using an aes key
def decrypt_aes(aes_key, message:bytes):
    debug("decrypting aes")
    if type(message) != bytes: message = message.encode()
    iv = message[:16]
    cipher = AES.new(aes_key, AES.MODE_CFB, iv)
    decrypted_msg = cipher.decrypt(message[16:])
    debug(f"decrypted aes {decrypted_msg}")
    return decrypted_msg


#if the main file is called, test the functions
if __name__ == "__main__":
    public_key, private_key = create_rsa_keypair()
    message = "Hello World"
    encrypted_msg = encrypt_rsa(public_key, message)
    decrypted_msg = decrypt_rsa(private_key, encrypted_msg)
    print(f"message: {message}")
    print(f"encrypted_msg: {encrypted_msg}")
    print(f"decrypted_msg: {decrypted_msg}")

    aes_key = create_aes_key()
    encrypted_msg = encrypt_aes(aes_key, message)
    decrypted_msg = decrypt_aes(aes_key, encrypted_msg)
    print(f"message: {message}")
    print(f"encrypted_msg: {encrypted_msg}")
    print(f"decrypted_msg: {decrypted_msg}")


