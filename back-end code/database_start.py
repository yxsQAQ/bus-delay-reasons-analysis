import mysql.connector


# Create connection to mysql database
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="root123"
)

# create database
database_name = "BODS_BUS_DATABASE"
cursor = conn.cursor()
cursor.execute("CREATE DATABASE {}".format(database_name))



