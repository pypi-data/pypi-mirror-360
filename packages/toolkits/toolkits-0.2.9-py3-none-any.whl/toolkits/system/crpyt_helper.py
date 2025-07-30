# -*- coding: utf-8 -*-
import argparse
import sys
from log4python.Log4python import log
from simplecrypt import encrypt, decrypt
import traceback
from unipath import Path
import importlib

importlib.reload(sys)
logger = log("MisUserActionEtl")


def encrypt_file(file_name):
    ciphertext = encrypt('password', plaintext)


def decrypt_file(file_name):
    if not Path(file_name).exists():
        pass
    plaintext = decrypt('password', ciphertext)

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("action", type=str, help="action: [encrypt|decrypt]")
        parser.add_argument("file_path", type=str, help="action: [encrypt|decrypt]")
        args = parser.parse_args()

        if args.action not in ['encrypt', 'decrypt']:
            print("action value was wrong! please check.[encrypt|decrypt]")

        if args.action == 'encrypt':
            encrypt_file(args.file_path)
        elif args.action == 'decrypt':
            decrypt_file(args.file_path)
    except Exception as ex:
        logger.debug("Error: %s" % ex)
        logger.debug(traceback.format_exc())