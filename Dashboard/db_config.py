import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="callmesiddie@123",
        database="hospital_db"
    )