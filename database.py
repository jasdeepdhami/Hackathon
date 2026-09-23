import os
import mysql.connector
import bcrypt

from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_connection():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            ssl_disabled=True
        )

        if db.is_connected():
            return db

    except Error as e:
        print("Database connection error:", e)

    return None


# ==================================================
# CREATE USER
# ==================================================

def create_user(
    username,
    password,
    first_name,
    last_name,
    phone_number,
    email
):
    db = get_connection()

    if db is None:
        return None

    cursor = db.cursor()

    try:
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        query = """
            INSERT INTO users
            (
                username,
                password_hash,
                first_name,
                last_name,
                phone_number,
                email
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            username,
            password_hash,
            first_name,
            last_name,
            phone_number,
            email
        )

        cursor.execute(query, values)

        db.commit()

        return cursor.lastrowid

    except Error as e:
        db.rollback()
        print("Error creating user:", e)
        return None

    finally:
        cursor.close()
        db.close()


# ==================================================
# GET USER BY ID
# ==================================================

def get_user_by_id(user_id):
    db = get_connection()

    if db is None:
        return None

    cursor = db.cursor(dictionary=True)

    try:
        query = """
            SELECT
                user_id,
                username,
                first_name,
                last_name,
                phone_number,
                email,
                created_at
            FROM users
            WHERE user_id = %s
        """

        cursor.execute(query, (user_id,))

        return cursor.fetchone()

    except Error as e:
        print("Error getting user:", e)
        return None

    finally:
        cursor.close()
        db.close()


# ==================================================
# GET USER BY USERNAME
# ==================================================

def get_user_by_username(username):
    db = get_connection()

    if db is None:
        return None

    cursor = db.cursor(dictionary=True)

    try:
        query = """
            SELECT *
            FROM users
            WHERE username = %s
        """

        cursor.execute(query, (username,))

        return cursor.fetchone()

    except Error as e:
        print("Error getting user:", e)
        return None

    finally:
        cursor.close()
        db.close()


# ==================================================
# UPDATE USER
# ==================================================

def update_user(
    user_id,
    username,
    first_name,
    last_name,
    phone_number,
    email
):
    db = get_connection()

    if db is None:
        return False

    cursor = db.cursor()

    try:
        query = """
            UPDATE users
            SET
                username = %s,
                first_name = %s,
                last_name = %s,
                phone_number = %s,
                email = %s
            WHERE user_id = %s
        """

        values = (
            username,
            first_name,
            last_name,
            phone_number,
            email,
            user_id
        )

        cursor.execute(query, values)

        db.commit()

        return cursor.rowcount > 0

    except Error as e:
        db.rollback()
        print("Error updating user:", e)
        return False

    finally:
        cursor.close()
        db.close()


# ==================================================
# DELETE USER
# ==================================================

def delete_user(user_id):
    db = get_connection()

    if db is None:
        return False

    cursor = db.cursor()

    try:
        query = """
            DELETE FROM users
            WHERE user_id = %s
        """

        cursor.execute(query, (user_id,))

        db.commit()

        return cursor.rowcount > 0

    except Error as e:
        db.rollback()
        print("Error deleting user:", e)
        return False

    finally:
        cursor.close()
        db.close()
