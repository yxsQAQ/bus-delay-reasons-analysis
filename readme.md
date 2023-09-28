Bus Delay Research Project

This project investigates bus delay issues based on open bus data from England. Below are the steps to set up the project environment and run the code.


How to Get Started?
1. Install Required Packages
In addition to commonly used Python packages, run the following command to install the necessary packages:

pip install mysql-connector-python pymysql pandas sqlalchemy numpy BODSDataExtractor Pillow Django

If any other packages are missing in your IDE, please install them manually.


2. Download Timetable Data
Download timetable data with stop-level information from https://github.com/department-for-transport-BODS/bods-data-extractor/tree/release-sb-1.2. Use the parameter nocs to specify the bus operators you need. After downloading, place the output datasets in the back-end code directory.


3. Set Up MySQL Database
Download MySQL and create a default user with the following configuration:

Host: 127.0.0.1
User: root
Password: root123


4. Initialize Database
Open the back-end code directory and run database_start.py.


5. Configure and Run Generate.py
In the Generate.py file, replace the API_KEY parameter with your own key. Obtain a free API key by registering at https://www.bus-data.dft.gov.uk/.

Then, modify the parameters in box = BoundingBox() to your specific coordinates.

Run Generate.py. The program will automatically collect the data. To stop data collection, terminate the program.


6. Remove Duplicate Data
Run delete_repeated_data.py after each data collection to avoid data duplication.


7. Create Tables in MySQL
Open your command prompt and input the following commands step-by-step:
cd your_root/code/data_visualization
python manage.py makemigrations
python manage.py migrate
mysql -u root -p

Enter the password root123, and then execute:
use bods_bus_visualization_users;

Create a table named bods_bus_visualization_users. The table headers are located in code/back-end code/My_API/data_analysis.py. Also, create another table named bods_bus_analysis_all with headers: OperatorRef, LineRef, DirectionRef, hour, Degree, GroupSize.


8. Run Data Analysis
Open the back-end code directory and run Analysis.py.


9. Launch Web Server
Open your command prompt and input the following:
cd your_root/code/data_visualization
python manage.py runserver
Open your web browser and navigate to http://127.0.0.1:8000/ to view the data visualizations.


Author
Xinsheng Yao

Date
09/05/2023









