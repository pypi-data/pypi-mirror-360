from rich import print
import os
from src.data.ascii import ascii
from src.data.crypt_file import ask_encrypt_file, ask_decrypt_file
from src.data.crypt_key import setup_masterkey, setup_new_rsa_files


def main():
    # set up master passwd
    print(ascii("crypt - key !"))
    masterkey = setup_masterkey()
    print('Your Master Password: ')
    print(ascii(masterkey))

    if not os.path.exists("private.pem"):
        # set up new rsa pairs, and encrypt private.pem
        setup_new_rsa_files(masterkey)

    # encrypt or decrypt a file? with master passwd
    ask_encrypt_file(masterkey)
    ask_decrypt_file(masterkey)
    

if __name__ == "__main__":
    main()
