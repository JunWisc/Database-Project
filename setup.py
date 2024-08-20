import mysql.connector
from getpass import getpass

print("Enter MySQL password below:")
password = getpass()

# Setup MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password,
    auth_plugin='mysql_native_password'
)

mycursor = conn.cursor()

# Uncomment the following line on first run to create the database
mycursor.execute("CREATE DATABASE IF NOT EXISTS medicalcases")

# Use the database
mycursor.execute("USE medicalcases")

# Data import
mycursor.execute("SET FOREIGN_KEY_CHECKS=0;")  # Ignores inconsistencies between patient_id and cases on data entry

# Create tables
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS hospitals (
        hospital_id INT UNSIGNED PRIMARY KEY,
        hospital_type INT UNSIGNED,
        hospital_city INT UNSIGNED,
        hospital_region INT UNSIGNED
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id BIGINT UNSIGNED PRIMARY KEY,
        city_code INT UNSIGNED,
        age VARCHAR(50)
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
        room_id INT UNSIGNED PRIMARY KEY,
        hospital_id INT UNSIGNED,
        FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id),
        ward_type VARCHAR(1),
        ward_facility VARCHAR(1),
        bed_grade TINYINT UNSIGNED
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS illnesses (
        illness_id INT UNSIGNED PRIMARY KEY,
        department VARCHAR(50),
        illness_severity VARCHAR(50)
    )
""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        case_id BIGINT UNSIGNED PRIMARY KEY,
        patient_id BIGINT UNSIGNED,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
        hospital_id INT UNSIGNED,
        FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id),
        room_id INT UNSIGNED,
        FOREIGN KEY (room_id) REFERENCES rooms(room_id),
        illness_id INT UNSIGNED,
        FOREIGN KEY (illness_id) REFERENCES illnesses(illness_id),
        admission_type VARCHAR(50),
        patient_visitors INT UNSIGNED,
        admission_deposit INT UNSIGNED,
        stay_days VARCHAR(50)
    )
""")

# Load data using LOAD DATA INFILE
try:
    mycursor.execute("""
        LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/relations/cases.csv' 
        INTO TABLE cases 
        FIELDS TERMINATED BY ',' 
        LINES TERMINATED BY '\n' 
        IGNORE 1 ROWS;
    """)
    
    mycursor.execute("""
        LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/relations/hospitals.csv' 
        INTO TABLE hospitals 
        FIELDS TERMINATED BY ',' 
        LINES TERMINATED BY '\n' 
        IGNORE 1 ROWS;
    """)
    
    mycursor.execute("""
        LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/relations/patients.csv' 
        INTO TABLE patients 
        FIELDS TERMINATED BY ',' 
        LINES TERMINATED BY '\n' 
        IGNORE 1 ROWS;
    """)
    
    mycursor.execute("""
        LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/relations/rooms.csv' 
        INTO TABLE rooms 
        FIELDS TERMINATED BY ',' 
        LINES TERMINATED BY '\n' 
        IGNORE 1 ROWS;
    """)
    
    mycursor.execute("""
        LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/relations/illnesses.csv' 
        INTO TABLE illnesses 
        FIELDS TERMINATED BY ',' 
        LINES TERMINATED BY '\n' 
        IGNORE 1 ROWS;
    """)
except mysql.connector.Error as err:
    print(f"Error: {err}")

# Remove \r in data
mycursor.execute("UPDATE `cases` SET `stay_days` = REPLACE(`stay_days`, '\r', '') WHERE `stay_days` LIKE '%\r%';")
mycursor.execute("UPDATE `patients` SET `age` = REPLACE(`age`, '\r', '') WHERE `age` LIKE '%\r%';")
mycursor.execute("UPDATE `illnesses` SET `illness_severity` = REPLACE(`illness_severity`, '\r', '') WHERE `illness_severity` LIKE '%\r%';")
conn.commit()

# Database checks
tables = ["cases", "patients", "hospitals", "rooms", "illnesses"]

# Describe cases entity
print("\nDescribe cases entity")
mycursor.execute("DESCRIBE cases")
for x in mycursor:
    print(x)

# Show first 3 entries of all tables in the database
for table in tables:
    print(f"\nFirst 3 {table} entries")
    mycursor.execute(f"SELECT * FROM {table} LIMIT 3")
    for x in mycursor:
        print(x)

mycursor.close()
conn.close()
