import pyAesCrypt
from rich import print

def encrypt_file(file_path, passwd):
    bufferSize = 64 * 1024  # 64K
    password = passwd
    new_file = file_path + ".aes"
    pyAesCrypt.encryptFile(file_path, new_file, password, bufferSize)


def decrypt_file(file_path, passwd):
    bufferSize = 64 * 1024  # 64K
    password = passwd
    output_file = "decrypy_" + file_path.removesuffix(".aes")
    pyAesCrypt.decryptFile(file_path, output_file, password, bufferSize)


def ask_encrypt_file(masterkey):
    answer = input('Do you want to encrypt a file (Y/n): ')
    if answer != "n":
        file = input('file path or "q" to quit: ')
        if file != "q":
            encrypt_file( file, masterkey )
            print("file: ", file, "is now encrypted as ", file + ".aes")
        else: 
            return


def ask_decrypt_file(masterkey):
    answer = input('Do you want to Decrypt a file (Y/n): ')
    if answer != "n":
        file = input('file path or "q" to quit: ')
        if file != "q":
            decrypt_file( file, masterkey )
            print("file: ", file, "is now decrypted as ", "decrypt_" + file.removesuffix('.aes'))
        else: 
            return
