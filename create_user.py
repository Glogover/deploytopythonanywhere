# create_user.py - Run once to create an application user.
# Example: python create_user.py admin password123

import getpass
import sys

import mysql.connector
from werkzeug.security import generate_password_hash

import dbconfig as cfg


def main():
    if len(sys.argv) >= 3:
        username = sys.argv[1].strip()
        password = sys.argv[2]
    else:
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")

    if not username or not password:
        raise SystemExit("Username and password are required.")

    connection = mysql.connector.connect(**cfg.mysql)
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, generate_password_hash(password)),
        )
        connection.commit()
        print(f"User '{username}' created.")
    except mysql.connector.IntegrityError:
        print(f"User '{username}' already exists.")
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
