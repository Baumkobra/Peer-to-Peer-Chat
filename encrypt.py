from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Message import debug
# create a private key public key 
def create_key(key_size=2048):
    new_key = RSA.generate(key_size)
    public_key = new_key.publickey().exportKey("PEM")
    private_key = new_key.exportKey("PEM")
    return public_key, private_key


def encrypt(public_key, message:bytes):
    # encrypt the message
    if type(message) != bytes: message = message.encode()
    debug(f"encrypyting {message}")
    public_key = RSA.importKey(public_key)
    encryptor = PKCS1_OAEP.new(public_key)
    encrypted_msg = encryptor.encrypt(message)
    debug(f"encrypted {encrypted_msg}")
    return encrypted_msg

def decrypt(private_key, message:bytes):
    # decrypt the message
    if type(message) != bytes: message = message.encode()

    private_key = RSA.importKey(private_key)
    decryptor = PKCS1_OAEP.new(private_key)
    decrypted_msg = decryptor.decrypt(message)
    return decrypted_msg


#if the main file is called, test the functions
if __name__ == "__main__":
    public_key, private_key = create_key()
    message = "Hello World"
    encrypted_msg = encrypt(public_key, message)
    decrypted_msg = decrypt(private_key, encrypted_msg)
    print(f"message: {message}")
    print(f"encrypted_msg: {encrypted_msg}")
    print(f"decrypted_msg: {decrypted_msg}")

