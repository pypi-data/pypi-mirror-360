"""Initialize simple .env file. On production apps, change `SUPERUSERNAME` and `SUPERUSERPASSWORD`"""

from .utils.criptografy_key import generate_criptografy_key, write_key_to_file


def main():
    write_key_to_file(key="user", name="SUPERUSERNAME")
    write_key_to_file(key="password", name="SUPERUSERPASSWORD")
    generate_criptografy_key()


if __name__ == "main":
    main()
