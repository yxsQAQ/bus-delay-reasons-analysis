import os
import time
import csv
import mysql.connector
import warnings

from My_API.data_explore import Siri
from bods_client.client import BODSClient
from bods_client.models import BoundingBox, SIRIVMParams


warnings.filterwarnings("ignore")

# Set this to your API key, either save to an environment variable or put in plain text
# be careful if its in plain text, this is your secret key!
API_KEY = '7bc31553f16519592e923a9e071bb526dd52d725'


bods = BODSClient(api_key=API_KEY)

# Same bounding box as in other examples
box = BoundingBox(min_longitude=-1.204376, min_latitude=52.934672, max_longitude=-1.091766, max_latitude=52.986581)
siri_params = SIRIVMParams(bounding_box=box)
data = bods.get_siri_vm_data_feed(params=siri_params)
current_dir = os.path.dirname(os.path.abspath(__file__))

# This will save a zip to the current working folder every 60 seconds forever...
# decide for yourself how often you want to collect data


# Open database
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="root123"
)

database_name = "BODS_BUS_DATABASE"
cursor = conn.cursor()

# operate database
cursor.execute("USE {}".format(database_name))

loop = 0

# ##################### AUTO version #####################
while True:

    data = bods.get_siri_vm_data_feed(params = siri_params)

    siri = Siri(data)
    file_name = siri.save_to_zip()
    path = siri.decompress_and_delete_zip(file_name, current_dir)
    file = siri.xml_to_csv(path)

    df = siri.get_dataframe(file)
    df = siri.preprocessing(df)
    df = siri.get_csv_file_name(df)
    df = siri.process_dataframe(df)
    siri.drop_noUse_lines(df)

    df.to_csv(file, index=False)

    with open(file, 'r') as file:
        csv_data = csv.reader(file)
        header = next(csv_data)

        for row in csv_data:
            table_name = "_".join(row[1:3] + row[4:6])

            # Check whether the table exists
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
                    "Latitude FLOAT",
                    "Degree VARCHAR(128)"
                ]
                table_query = "CREATE TABLE {} ({})".format(table_name, ", ".join(columns))
                cursor.execute(table_query)

            # Insert data
            insert_query = "INSERT INTO {} (RecordedAtTime, OperatorRef, LineRef, DirectionRef, OriginRef, DestinationRef, DatedVehicleJourneyRef, OriginAimedDepartureTime, DestinationAimedArrivalTime, Longitude, Latitude, degree) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(
                table_name)
            values = tuple(row)
            cursor.execute(insert_query, values)

    loop += 1

    print('here is loop ' + str(loop))

    time.sleep(300)

# ##################### SINGLE version #####################

# siri = Siri(data)
# file_name = siri.save_to_zip()
#
# while True:
#     if file_name:
#         path = siri.decompress_and_delete_zip(file_name, current_dir)
#         file_name = siri.xml_to_csv(path)
#         break
#
#
# df = siri.get_dataframe(file_name)
# df = siri.preprocessing(df)
# df = siri.get_csv_file_name(df)
# siri.get_ratio(df)




