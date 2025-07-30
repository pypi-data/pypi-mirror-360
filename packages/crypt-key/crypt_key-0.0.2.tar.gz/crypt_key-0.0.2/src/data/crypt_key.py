from Crypto.PublicKey import RSA
from rich import print

# Set up master password
def setup_masterkey() -> str:
    secret_code = 'your-secret-code-is_set_to,default.'
    run = True
    while run:
        answer = input("Setup your MasterKey: ")
        if answer == '':
            print('To short passwd!, try again')
            continue
        else: 
            secret_code = answer
            run = False
    return secret_code


def set_up_rsa()-> bytes:
    key = RSA.generate(2048)
    return key


def encrypt_with_key(secret_code: str, key: bytes) -> str:
    encrypted_key = key.export_key(passphrase=secret_code, pkcs=8,
                               protection="scryptAndAES128-CBC",
                               prot_params={'iteration_count': 131072})
    return encrypted_key


def save_encrypt_key(encrypted_key: bytes ,file="private.pem"):
    # Save encrypted private key
    with open(file, "wb") as f:
        f.write(encrypted_key)
    print("generate encrypted private.pem - file")


def save_public_pem(key: bytes, file="public.pem"):
    # Save public key (no passphrase needed)
    with open("public.pem", "wb") as f:
        f.write(key.publickey().export_key())
    print("generate public.pem - file")


def read_decrypted_private_key(secret_code: str, file="private.pem")-> bytes:
    with open(file, "rb") as f:
        encrypted_key_data = f.read()
        # unlock the private key using the passphrase
        key = RSA.import_key(encrypted_key_data, passphrase=secret_code)
        
        # Now you can use the key for signing, decryption, etc.
        print("Private key successfully unlocked!")
    return key


# Test to se if private.pem can be encryped and decrypted.
def check_key(masterkey: str, key: bytes, encrypt_key: bytes) -> None:
    decrypt_key = read_decrypted_private_key(masterkey)
    print (ascii("key"))
    print(key.export_key())  # inspect the key

    print (ascii("Encrypted_key"))
    print(encrypt_key.decode('utf-8'))  # Print the PEM-formatted encrypted private key

    print (ascii("Decrypted_key"))
    print(decrypt_key.export_key())  # inspect decrypt key


def setup_new_rsa_files(masterkey, private='private.pem', public='public-pem'):
    answer = input('Do you want to set up new rsa-pars (Y/n): ')
    if answer != "n":
        key = set_up_rsa()
        encrypt_key = encrypt_with_key(masterkey, key)
        save_encrypt_key(encrypt_key, private)
        save_public_pem(key, public)

        # Print out and check if encrypt and decrypt works.
        check_key(masterkey, key, encrypt_key)