from cryptography.fernet import Fernet
from .read_write2file import write_key_to_file


def generate_criptografy_key(add2env: bool = True):
    """ """
    key = Fernet.generate_key().decode()
    keep = "no"
    if add2env:
        keep = input("Warning. To continue the operation type (y/yes).")
        if keep == "y" or keep == "yes":
            write_key_to_file(key=key, name="CRIPTOGRAFY_KEY")

    print(
        f"criptografy_key: {key}"
        + (" " if add2env and (keep == "y" or keep == "yes") else " not ")
        + "added to .env file"
    )
    return key
