import zipfile
import time
import os
import csv
import re
import datetime
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np


class Siri:

    def __init__(self, xml):
        self.xml = xml
        self.dict = self.parse(self.xml)

    def parse(self, raw_xml):
        tree = ET.ElementTree(ET.fromstring(raw_xml))
        root = tree.getroot()
        return self.parse_element(root)

    def parse_element(self, element):
        data = {}

        for current in element:
            name = current.tag[29:]

            if current:
                if name in data:
                    if not isinstance(data[name], list):
                        temp = data[name]
                        data[name] = [temp]
                    data[name].append(self.parse_element(current))
                else:
                    data[name] = self.parse_element(current)

            elif current.text:
                data[name] = current.text

        return data

    def save_to_zip(self):
        now = time.strftime("%Y%m%d-%H%M%S")
        zip_file_path = f"{now}.zip"
        with zipfile.ZipFile(zip_file_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            # Add the XML content to the Zip file
            zipf.writestr(f'{now}.xml', self.xml)

        return zip_file_path

    def decompress_and_delete_zip(self, zip_file_name, path):
        # Create the absolute path to the zip file
        zip_file_path = os.path.join(path, zip_file_name)

        # Extract the zip file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # Get the list of files inside the zip file
            file_list = zip_ref.namelist()

            # Assuming there's only one XML file, extract it
            if len(file_list) == 1 and file_list[0].lower().endswith('.xml'):
                xml_file_path = os.path.join(path, file_list[0])
                zip_ref.extract(file_list[0], path)

        # Delete the zip file
        os.remove(zip_file_path)

        # Return the path of the extracted XML file
        return xml_file_path

    def xml_to_csv(self, path):

        file_path = os.path.join(path)

        # Read the XML data from the file
        with open(file_path, 'r') as xmlfile:
            data = xmlfile.read()

        # Parse the XML data
        root = ET.fromstring(data)

        # Define the namespaces
        namespaces = {
            'default': 'http://www.siri.org.uk/siri',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

        # Define the column names
        column_names = ['RecordedAtTime', 'OperatorRef', 'LineRef', 'DirectionRef', 'OriginRef', 'DestinationRef',
                        'DatedVehicleJourneyRef', 'OriginAimedDepartureTime', 'DestinationAimedArrivalTime',
                        'Longitude', 'Latitude']

        output_file = file_path.replace('.xml', '.csv')

        csv_filename = os.path.basename(output_file)

        # Create a new CSV file and write the column names
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(column_names)

            # Extract data and write to CSV
            for vehicle in root.findall('.//default:VehicleActivity', namespaces):
                recorded_at_time = vehicle.find('.//default:RecordedAtTime', namespaces).text
                operator_ref = vehicle.find('.//default:OperatorRef', namespaces).text
                line_ref = vehicle.find('.//default:LineRef', namespaces).text
                direction_ref = vehicle.find('.//default:DirectionRef', namespaces).text
                origin_ref = vehicle.find('.//default:OriginRef', namespaces).text
                destination_ref = vehicle.find('.//default:DestinationRef', namespaces).text
                dated_vehicle_journey_ref = vehicle.find('.//default:DatedVehicleJourneyRef', namespaces).text
                if vehicle.find('.//default:DestinationAimedArrivalTime', namespaces) is not None:
                    destination_aimed_arrival_time = vehicle.find('.//default:DestinationAimedArrivalTime',
                                                                  namespaces).text
                else:
                    destination_aimed_arrival_time = ''
                if vehicle.find('.//default:OriginAimedDepartureTime', namespaces) is not None:
                    origin_aimed_departure_time = vehicle.find('.//default:OriginAimedDepartureTime', namespaces).text
                else:
                    origin_aimed_departure_time = ''
                longitude = vehicle.find('.//default:Longitude', namespaces).text
                latitude = vehicle.find('.//default:Latitude', namespaces).text

                # Write the extracted data to the CSV file
                writer.writerow([recorded_at_time, operator_ref, line_ref, direction_ref, origin_ref, destination_ref,
                                 dated_vehicle_journey_ref, origin_aimed_departure_time, destination_aimed_arrival_time,
                                 longitude, latitude])
        # Delete xml file
        os.remove(file_path)

        # Example: 20230705-151055.csv
        return csv_filename

    def get_dataframe(self, filename):

        df = pd.read_csv(filename)

        return df

    def get_weekday(self, date_string):

        date_object = datetime.datetime.strptime(date_string, "%Y-%m-%d")

        return date_object.strftime("%A")

    def preprocessing(self, dataframe):
        dataframe = dataframe.dropna(subset=['DestinationAimedArrivalTime', 'OriginAimedDepartureTime'])
        dataframe['DestinationAimedArrivalTime'] = dataframe['DestinationAimedArrivalTime'].astype(str)
        dataframe['DestinationWeekday'] = dataframe['DestinationAimedArrivalTime'].str[:10].map(self.get_weekday)
        dataframe['DepartureTime'] = dataframe['OriginAimedDepartureTime'].str[11:16]
        dataframe['RecordedAtTimeSimple'] = dataframe['RecordedAtTime'].str[11:19]
        return dataframe

    def search_csv_files(self, root_folder, search_value):
        for root, dirs, files in os.walk(root_folder):
            for file in files:
                if file.endswith(".csv"):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as csv_file:
                        reader = csv.reader(csv_file)
                        for row in reader:
                            if search_value in row:
                                return file_path
        return None

    def get_csv_file_name(self, dataframe):
        # input: dataframe
        # output: create a new line that shows the linked root of csv file
        for index, row in dataframe.iterrows():
            DirectionRef = row['DirectionRef']

            # This line can be changed to satisfy your matching strategy
            search_value = str(row['DatedVehicleJourneyRef'])

            if DirectionRef == 'outbound' or DirectionRef == 'OUTBOUND':
                root_folder_value = 'outbound_timetable_folder'
            else:
                root_folder_value = 'inbound_timetable_folder'

            result = self.search_csv_files(root_folder_value, search_value)
            if result is not None:
                dataframe.at[index, 'result'] = result
            else:
                dataframe.at[index, 'result'] = np.nan

        dataframe = dataframe.dropna()
        return dataframe

    def process_csv_file(self, file_path, destination_weekday, destination_ref, destination_time):

        data = pd.read_csv(file_path)

        sixth_row = data.iloc[4]
        second_column = data.iloc[:, 1]

        # Initialize matching_columns and matching_values as 1D arrays
        matching_columns = []
        matching_rows = []

        for idx, value in enumerate(sixth_row):
            for i, weekday in enumerate(destination_weekday):
                if weekday in str(value):
                    matching_columns.append(idx)

        for idx, value in enumerate(second_column):
            if str(destination_ref) in str(value):
                matching_rows.append(idx)

        match_count = 0
        non_match_count = 0
        difference = None

        if matching_columns and matching_rows:
            for i in range(len(matching_rows)):
                # Get the matching row name
                matching_row_name = matching_rows[i]

                # Get the matching values based on column names and row name
                matching_values = data.iloc[matching_row_name, matching_columns].values

                if all(value == "-" for value in matching_values):

                    pass

                else:
                    # Output the matching values
                    match = any(destination_time in value for value in matching_values)

                    if match:
                        match_count += 1
                        difference = 0
                    else:
                        non_match_count += 1

                        cleaned_values = [value for value in matching_values if
                                          value != "-" and value != destination_time]
                        matching_values = cleaned_values

                        if len(matching_values) >= 2:
                            nearest_time = min(matching_values, key=lambda x: abs(
                                datetime.datetime.strptime(x, "%H:%M") - datetime.datetime.strptime(destination_time,
                                                                                                    "%H:%M")))
                            difference = (datetime.datetime.strptime(nearest_time,
                                                                     "%H:%M") - datetime.datetime.strptime(
                                destination_time, "%H:%M")).total_seconds() // 60

        return match_count, non_match_count, difference

    def get_ratio(self, dataframe):
        # Initialize counters for overall match and not match counts
        total_match_count = 0
        total_not_match_count = 0

        # Initialize difference list
        difference_list = []

        # Iterate over each row in the DataFrame and process the corresponding CSV file
        for index, row in dataframe.iterrows():
            csv_path = row["result"]
            destination_weekday = row["DestinationWeekday"].split(",")  # Split DestinationWeekday by comma into a list
            destination_ref = row["DestinationRef"]
            destination_time = row['DestinationTime']

            match_count, not_match_count, differences = self.process_csv_file(csv_path, destination_weekday, destination_ref,
                                                                         destination_time)

            total_match_count += match_count
            total_not_match_count += not_match_count

            difference_list.append(differences)  # Append differences to the difference list

        # Calculate the overall match and not match ratios
        total_count = total_match_count + total_not_match_count
        match_ratio = total_match_count / total_count
        not_match_ratio = total_not_match_count / total_count

        # Output the overall match and not match ratios
        print("Overall Match Ratio:", match_ratio)
        print("Overall Not Match Ratio:", not_match_ratio)
        print('total count:', total_count)
        print('total match count:', total_match_count)
        print('total not match count:', total_not_match_count)
        print("Difference list:", difference_list)

        dataframe["difference"] = difference_list

        return dataframe

    def get_time_lag(self, dataframe):
        dataframe['TimeDifference'] = dataframe.\
            apply(lambda row: (datetime.datetime.strptime(row['DestinationTime'],'%H:%M') - datetime.datetime.strptime(
            row['DepartureTime'], '%H:%M')).total_seconds() // 60, axis=1)

        return dataframe

    def get_degree_of_delay(self, dataframe):
        dataframe['degree'] = np.where(dataframe['difference'].isna() | dataframe['TimeDifference'].isna(),
                                       np.nan,
                                       dataframe['difference'] / dataframe['TimeDifference'])

        dataframe['degree'] = dataframe['degree'].round(5)

        return dataframe

    def process_row(self, row):
        # Extract the first 6 characters of the 'Latitude' and get the 'Longitude' from the current row
        real_latitude = str(row['Latitude'])[:6]
        real_longitude = row['Longitude']

        # Read the 'Stops.csv' file and store it in the 'stop' dataframe
        stop = pd.read_csv('Stops.csv', encoding='gbk')

        # Find matching latitudes in the 'stop' dataframe
        matched_latitudes = []
        for index, stop_row in stop.iloc[176338:187032].iterrows():
            if str(real_latitude) in str(stop_row['Latitude']):
                matched_latitudes.append([index, stop_row['Latitude']])

        # Get matched longitudes from the 'stop' dataframe based on the matched latitudes
        matched_longitudes = [stop.loc[row[0], 'Longitude'] for row in matched_latitudes]

        # Find the closest longitude index to the real longitude
        closest_longitude_index = matched_longitudes.index(
            min(matched_longitudes, key=lambda x: abs(x - real_longitude)))
        closest_longitude = matched_longitudes[closest_longitude_index]
        matched_row_index = matched_latitudes[closest_longitude_index][0]
        result_array = [matched_row_index, closest_longitude]

        # Get the bus stop, file path, and dated vehicle journey reference from the current row
        bus_stop = stop['CommonName'].iloc[result_array[0]]
        file_path = row['result']
        dated_vehicle_journey_ref = row['DatedVehicleJourneyRef']

        # Read the data from the file specified in 'file_path'
        data = pd.read_csv(file_path)

        # Find matching column index with 'dated_vehicle_journey_ref' in the third row of the data
        matching_column = []
        matching_row = []
        differences = []

        forth_row = data.iloc[2]
        for idx, value in enumerate(forth_row):
            if str(dated_vehicle_journey_ref) == str(value):
                matching_column = idx

        # Find matching row indices with 'bus_stop' in the fifth column of the data
        fifth_column = data.iloc[:, 4]
        for idx, value in enumerate(fifth_column):
            if str(bus_stop) == str(value):
                matching_row.append(idx)

        # Calculate time differences for each matching row and column
        for index in range(len(matching_row)):
            if matching_row and matching_column:
                matching_value = data.iloc[matching_row[index], matching_column]

                if matching_value != '-':
                    time_format = '%H:%M'
                    time_obj = datetime.datetime.strptime(matching_value, time_format)
                    time_obj -= datetime.timedelta(hours=1)
                    result_value = time_obj.strftime(time_format)

                    if result_value.startswith("00"):
                        result_value = "24" + result_value[2:]
                    result_value = result_value + ':00'
                    time_format = '%H:%M:%S'
                    row['RecordedAtTimeSimple'] = pd.to_datetime(row['RecordedAtTimeSimple'], format=time_format)
                    result_value = datetime.datetime.strptime(result_value, time_format)

                    if result_value.hour == 0:
                        result_value = result_value.replace(hour=24)
                    difference = (row['RecordedAtTimeSimple'] - result_value).total_seconds() / 60

                    differences.append(difference)

        # Process the 'matching_column' data and find the minimum time difference
        arr = data.iloc[:, matching_column].values
        arr = arr.astype(str)
        if arr.size > 0:
            # Use regex to filter elements that match the format '%H:%M'
            time_format_regex = r'\d{2}:\d{2}'
            arr = [value for value in arr if re.match(time_format_regex, value)]

            # Now 'arr' contains only the values that match the format '%H:%M'.
            arr_first = arr[0] + ':00'
            arr_last = arr[-1] + ':00'
            time_format = '%H:%M:%S'
            arr_first_obj = datetime.datetime.strptime(arr_first, time_format)
            arr_first_obj -= datetime.timedelta(hours=1)
            arr_first = arr_first_obj.strftime(time_format)
            arr_first = datetime.datetime.strptime(arr_first, time_format)
            arr_last_obj = datetime.datetime.strptime(arr_last, time_format)
            arr_last_obj -= datetime.timedelta(hours=1)
            arr_last = arr_last_obj.strftime(time_format)
            arr_last = datetime.datetime.strptime(arr_last, time_format)

            row['RecordedAtTimeSimple'] = pd.to_datetime(row['RecordedAtTimeSimple'], format=time_format)
            dif_first = (row['RecordedAtTimeSimple'] - arr_first).total_seconds() / 60
            dif_last = (row['RecordedAtTimeSimple'] - arr_last).total_seconds() / 60

            differences.append(dif_first)
            differences.append(dif_last)

            total_time = (arr_last - arr_first).total_seconds() / 60

        # Return the minimum time difference if there are any differences, otherwise return NaN
        if differences:
            return min(np.abs(differences)) / total_time
        else:
            return np.nan

    def process_dataframe(self, dataframe):
        # Process each row in the dataframe and calculate the differences
        for index, row in dataframe.iterrows():
            degree = self.process_row(row)
            dataframe.loc[index, 'Degree'] = degree

        dataframe = dataframe.dropna()

        return dataframe

    def drop_noUse_lines(self, dataframe):
        dataframe.drop('DestinationWeekday', axis=1, inplace=True)
        dataframe.drop('DepartureTime', axis=1, inplace=True)
        dataframe.drop('RecordedAtTimeSimple', axis=1, inplace=True)
        dataframe.drop('result', axis=1, inplace=True)


class folder:

    def extract_and_check_unique_numbers(self, folder_path):
        csv_files = []
        result = []

        # Traverse all folders and files in the root directory
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.csv'):
                    csv_files.append(os.path.join(root, file))

        # Process all CSV files
        for file_path in csv_files:
            try:
                # Read the fourth row of the CSV file using pandas
                df = pd.read_csv(file_path, header=None, skiprows=3, nrows=1)
                row_values = df.values.flatten().tolist()

                # Compare the numbers with the existing numbers in result
                for value in row_values:
                    if value == 'Journey Code' or value == '->':
                        continue  # Skip non-numeric rows
                    if (file_path, value) not in result:
                        result.append([file_path, value])
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

        new_res = []
        for i in result:
            new_res.append(i[1])

        # True: All numbers are unique.
        return len(new_res) == len(set(new_res))




