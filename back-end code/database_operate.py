import mysql.connector
import csv


conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="root123"
)


# create database
database_name = "BODS_BUS_DATABASE"
cursor = conn.cursor()

# operate database
cursor.execute("USE {}".format(database_name))

csv_file = "20230705-235405.csv"

with open(csv_file, 'r') as file:
    csv_data = csv.reader(file)
    header = next(csv_data)

    for row in csv_data:
        table_name = "_".join(row[1:3] + row[4:6])

        cursor.execute("SHOW TABLES LIKE %s", (table_name,))
        existing_tables = cursor.fetchall()

        if not existing_tables:
            columns = [
                "id INT AUTO_INCREMENT PRIMARY KEY",
                "RecordedAtTime VARCHAR(64)",
                "OperatorRef VARCHAR(32)",
                "LineRef VARCHAR(32)",
                "DirectionRef VARCHAR(64)",
                "OriginRef VARCHAR(64)",
                "DestinationRef VARCHAR(64)",
                "DatedVehicleJourneyRef VARCHAR(64)",
                "OriginAimedDepartureTime VARCHAR(64)",
                "DestinationAimedArrivalTime VARCHAR(64)",
                "Longitude FLOAT",
                "Latitude FLOAT"
            ]
            table_query = "CREATE TABLE {} ({})".format(table_name, ", ".join(columns))
            cursor.execute(table_query)

        insert_query = "INSERT INTO {} (RecordedAtTime, OperatorRef, LineRef, DirectionRef, OriginRef, DestinationRef, DatedVehicleJourneyRef, OriginAimedDepartureTime, DestinationAimedArrivalTime, Longitude, Latitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(table_name)
        values = tuple(row)
        cursor.execute(insert_query, values)



conn.commit()
cursor.close()
conn.close()