from shiny import App, ui, render, Inputs, Outputs, Session
import pandas as pd
import mysql.connector
from getpass import getpass

import conditions_query

print("Enter MySQL password below:")

password = getpass()

# SETUP CONN HERE
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password,  # Replace with your actual MySQL password
    database="medicalcases",
    auth_plugin='mysql_native_password'
)

def query_by_id(table_name, search_id):
    cursor = conn.cursor(dictionary=True)  # Using dictionary=True to get the results as a dictionary

    # Define SQL select query based on the table name and fields
    if table_name == "patients":
        sql = "SELECT * FROM patients WHERE patient_id = %s"
    elif table_name == "hospitals":
        sql = "SELECT * FROM hospitals WHERE hospital_id = %s"
    elif table_name == "rooms":
        sql = "SELECT * FROM rooms WHERE room_id = %s"
    elif table_name == "illnesses":
        sql = "SELECT * FROM illnesses WHERE illness_id = %s"
    elif table_name == "cases":
        sql = "SELECT * FROM cases WHERE case_id = %s"
    else:
        return None

    values = (search_id,)

    try:
        cursor.execute(sql, values)
        result = cursor.fetchone()  # Using fetchone to get a single record

        if result:
            return result
        else:
            return None  # Return None if no record is found

    except mysql.connector.Error as error:
        print(f"Failed to query MySQL table {error}")
        return None
    finally:
        cursor.close()

def query_by_conditions(conditions):
    search_results = pd.DataFrame()

    try:
        print(conditions)
        query = conditions_query.construct_conditional_query(conditions)

        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()

        if results:
            search_results = pd.concat([search_results, pd.DataFrame(results)], ignore_index=True)

        cursor.close()
    
    except mysql.connector.Error as error:
        print(f"Failed to query MySQL table {error}")

    return search_results

def add_row_to_table(table_name, new_row):
    cursor = conn.cursor()

    # Define SQL insert query based on the table name and fields
    if table_name == "patients":
        sql = "INSERT INTO patients (patient_id, city_code, age) VALUES (%s, %s, %s)"
        values = (new_row["ID"], new_row["Field1"], new_row["Field2"])
    elif table_name == "hospitals":
        sql = "INSERT INTO hospitals (hospital_id, hospital_type, hospital_city, hospital_region) VALUES (%s, %s, %s, %s)"
        values = (new_row["ID"], new_row["Field1"], new_row["Field2"], new_row["Field3"])
    elif table_name == "rooms":
        sql = "INSERT INTO rooms (room_id, hospital_id, ward_type, ward_facility, bed_grade) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (new_row["ID"], new_row["Field1"], new_row["Field2"], new_row["Field3"], new_row["Field4"], new_row["Field5"])
    elif table_name == "illnesses":
        sql = "INSERT INTO illnesses (illness_id, department, illness_severity) VALUES (%s, %s, %s)"
        values = (new_row["ID"], new_row["Field1"], new_row["Field2"])
    elif table_name == "cases":
        sql = "INSERT INTO cases (case_id, patient_id, hospital_id, room_id, illness_id, admission_type, patient_visitors, admission_deposit, stay_days) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (new_row["ID"], new_row["Field1"], new_row["Field2"], new_row["Field3"], new_row["Field4"], new_row["Field5"], new_row["Field6"], new_row["Field7"], new_row["Field8"])
    else:
        return False

    try:
        cursor.execute(sql, values)
        conn.commit()
        return True
    except mysql.connector.Error as error:
        if error.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
            print("Duplicate entry error: ID already exists")
        else:
            print(f"Failed to insert into MySQL table {error}")
        return False
    finally:
        cursor.close()

# UI Definition
app_ui = ui.page_fluid(
    ui.head_content(
        ui.tags.style("""
            body {
                font-family: Arial, sans-serif;
            }
            .sidebar {
                background-color: #f8f9fa;
                padding: 10px;
                border-right: 1px solid #ddd;
                border: 1px solid #ccc;
                border-radius: 5px; 
                margin-right: 10px;
            }
            .main {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            .btn {
                margin-top: 10px;
            }
            .title {
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
                padding-top: 20px;
            }
            .pane {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 15px;
            }
            .scrollable-table {
                max-height: 525px;
                max-width: 1100px;
                overflow-y: auto;
                overflow-x: auto;
                display: block;
                white-space: nowrap;
            }
        """)
    ),
    ui.div(
        ui.h2("Hospital Patient Database", class_="title"),
        ui.tags.img(src="7064996.jpg", style="position: absolute; top: 10px; right: 10px; width: 100px; height: auto;")
    ),
    ui.layout_sidebar(
        ui.sidebar(
            ui.div(
                ui.input_select("section", "Select Section", {
                    "id_search": "Search by ID",
                    "conditional_search": "Advanced Search",
                    "add_row": "Insert Data"
                }),
                ui.output_ui("dynamic_ui"),
                class_="sidebar pane"
            )
        ),
        ui.panel_fixed(
            ui.div(
                ui.output_ui("main_output"),
                class_="main pane"
            )
        )
    )
)

# # Server Logic
# def server(input: Inputs, output: Outputs, session: Session):

#     # Dynamic UI for Add Row section based on table selection
#     @output
#     @render.ui
#     def add_row_dynamic_fields():
#         table = input.add_table_select()
#         if table == "patients":
#             return ui.TagList(
#                 ui.input_numeric("new_id", "Patient ID", 0),
#                 ui.input_text("field1", "City Code", 0),
#                 ui.input_select("field2", "Age", {
#                     "0-10": "0-10",
#                     "11-20": "11-20",
#                     "21-30": "21-30",
#                     "31-40": "31-40",
#                     "41-50": "41-50",
#                     "51-60": "51-60",
#                     "61-70": "61-70",
#                     "71-80": "71-80",
#                     "81-90": "81-90",
#                     "91-100": "91-100"
#                 })
#             )
#         elif table == "hospitals":
#             return ui.TagList(
#                 ui.input_numeric("new_id", "Hospital ID", 0),
#                 ui.input_text("field1", "Hospital Type", 0),
#                 ui.input_text("field2", "Hospital City", 0),
#                 ui.input_text("field3", "Hospital Region", 0)
#             )
#         elif table == "rooms":
#             return ui.TagList(
#                 ui.input_numeric("new_id", "Room ID", 0),
#                 ui.input_numeric("field1", "Hospital ID", 0),
#                 ui.input_select("field2", "Ward Type", {
#                     "Q": "Q",
#                     "R": "R",
#                     "S": "S",
#                     "T" : "T",
#                     "U": "U",
#                     "P" : "P",
#                 }),
#                 ui.input_select("field3", "Ward Facility", {
#                     "A": "A",
#                     "B": "B",
#                     "C": "C",
#                     "D" : "D",
#                     "E": "E",
#                     "F" : "F",
#                 }),
#                 ui.input_numeric("field4", "Bed Grade", 0)
#             )
#         elif table == "illnesses":
#             return ui.TagList(
#                 ui.input_numeric("new_id", "Illness ID", 0),
#                 ui.input_select("field1", "Department", {
#                     "anesthesia": "anesthesia",
#                     "gynecology": "gynecology",
#                     "radiotherapy": "radiotherapy",
#                     "surgery" : "surgery",
#                     "TB & Chest disease" : "TB & Chest disease",
#                     "others" : "others"
#                 }),
#                 ui.input_select("field2", "Illness Severity", {
#                     "extreme": "Extreme",
#                     "moderate": "Moderate",
#                     "minor": "Minor"
#                 })
#             )
#         elif table == "cases":
#             return ui.TagList(
#                 ui.input_numeric("new_id", "Case ID", 0),
#                 ui.input_numeric("field1", "Patient ID", 0),
#                 ui.input_numeric("field2", "Hospital ID", 0),
#                 ui.input_numeric("field3", "Room ID", 0),
#                 ui.input_numeric("field4", "Illness ID", 0),
#                 ui.input_select("field5", "Admission Type", {
#                     "trauma": "Trauma",
#                     "emergency": "Emergency",
#                     "urgent": "Urgent"
#                 }),
#                 ui.input_numeric("field6", "Patient Visitors", 0),
#                 ui.input_numeric("field7", "Admission Deposit", 0),
#                 ui.input_select("field8", "Stay Days", {
#                     "0-10": "0-10",
#                     "11-20": "11-20",
#                     "21-30": "21-30",
#                     "31-40": "31-40",
#                     "41-50": "41-50",
#                     "51-60": "51-60",
#                     "61-70": "61-70",
#                     "71-80": "71-80",
#                     "81-90": "81-90",
#                     "91-100": "91-100",
#                     "More than 100": "More than 100"
#                 })
#             )
#         return ui.div()

searchidbut = 0
searchcondbut = 0
addbut = 0  
Flagid = True
Flagadd = True

def update_searchid():
    global searchidbut, Flagid
    searchidbut +=1
    if searchidbut == 2 and Flagid:
        searchidbut -= 1
        Flagid = False

    return searchidbut

def get_searchid():
    global searchidbut
    return searchidbut

def update_add():
    global addbut, Flagadd
    addbut +=1
    if addbut == 2 and Flagadd:
        addbut -= 1
        Flagadd = False

    return addbut

def get_add():
    global addbut
    return addbut
# Server Logic
def server(input: Inputs, output: Outputs, session: Session):



    # Dynamic UI for Add Row section based on table selection
    @output
    @render.ui
    def add_row_dynamic_fields():
        table = input.add_table_select()
        if table == "patients":
            return ui.TagList(
                ui.input_numeric("new_id", "Patient ID", 0),
                ui.input_text("field1", "City Code", 0),
                ui.input_select("field2", "Age", {
                    "0-10": "0-10",
                    "11-20": "11-20",
                    "21-30": "21-30",
                    "31-40": "31-40",
                    "41-50": "41-50",
                    "51-60": "51-60",
                    "61-70": "61-70",
                    "71-80": "71-80",
                    "81-90": "81-90",
                    "91-100": "91-100"
                })
            )
        elif table == "hospitals":
            return ui.TagList(
                ui.input_numeric("new_id", "Hospital ID", 0),
                ui.input_text("field1", "Hospital Type", 0),
                ui.input_text("field2", "Hospital City", 0),
                ui.input_text("field3", "Hospital Region", 0)
            )
        elif table == "rooms":
            return ui.TagList(
                ui.input_numeric("new_id", "Room ID", 0),
                ui.input_numeric("field1", "Hospital ID", 0),
                ui.input_select("field2", "Ward Type", {
                    "Q": "Q",
                    "R": "R",
                    "S": "S",
                    "T" : "T",
                    "U": "U",
                    "P" : "P",
                }),
                ui.input_select("field3", "Ward Facility", {
                    "A": "A",
                    "B": "B",
                    "C": "C",
                    "D" : "D",
                    "E": "E",
                    "F" : "F",
                }),
                ui.input_numeric("field4", "Bed Grade", 0)
            )
        elif table == "illnesses":
            return ui.TagList(
                ui.input_numeric("new_id", "Illness ID", 0),
                ui.input_select("field1", "Department", {
                    "anesthesia": "anesthesia",
                    "gynecology": "gynecology",
                    "radiotherapy": "radiotherapy",
                    "surgery" : "surgery",
                    "TB & Chest disease" : "TB & Chest disease",
                    "others" : "others"
                }),
                ui.input_select("field2", "Illness Severity", {
                    "extreme": "Extreme",
                    "moderate": "Moderate",
                    "minor": "Minor"
                })
            )
        elif table == "cases":
            return ui.TagList(
                ui.input_numeric("new_id", "Case ID", 0),
                ui.input_numeric("field1", "Patient ID", 0),
                ui.input_numeric("field2", "Hospital ID", 0),
                ui.input_numeric("field3", "Room ID", 0),
                ui.input_numeric("field4", "Illness ID", 0),
                ui.input_select("field5", "Admission Type", {
                    "trauma": "Trauma",
                    "emergency": "Emergency",
                    "urgent": "Urgent"
                }),
                ui.input_numeric("field6", "Patient Visitors", 0),
                ui.input_numeric("field7", "Admission Deposit", 0),
                ui.input_select("field8", "Stay Days", {
                    "0-10": "0-10",
                    "11-20": "11-20",
                    "21-30": "21-30",
                    "31-40": "31-40",
                    "41-50": "41-50",
                    "51-60": "51-60",
                    "61-70": "61-70",
                    "71-80": "71-80",
                    "81-90": "81-90",
                    "91-100": "91-100",
                    "More than 100": "More than 100"
                })
            )
        return ui.div()

    # Dynamic Main Screen UI
    @output
    @render.ui
    def dynamic_ui():
        section = input.section()
        if section == "id_search":
            return ui.TagList(
                ui.input_select("table_select", "Select Table", {
                    "cases": "Cases", 
                    "hospitals": "Hospitals", 
                    "patients": "Patients", 
                    "illnesses": "Illnesses", 
                    "rooms": "Rooms"
                }),
                ui.input_numeric("search_id", "Search by ID", 0),
                ui.input_action_button("search_btn", "Search", class_="btn btn-primary")
            )
        elif section == "conditional_search":
            return ui.TagList(
                ui.input_checkbox_group("conditions", "Search By", {
                    "case_id": "Case ID",
                    "patient_id": "Patient ID",
                    "hospital_id": "Hospital ID",
                    "room_id": "Room ID",
                    "illness_id": "Illness ID",
                    "admission_type": "Admission Type", 
                    "stay_days": "Stay Days",
                    "city_code": "Patient City Code",
                    "age": "Patient Age", 
                    "hospital_type": "Hospital Type", 
                    "hospital_city": "Hospital City", 
                    "hospital_region": "Hospital Region",
                    "ward_type": "Room Ward Type",
                    "ward_facility": "Room Ward Facility",
                    "bed_Grade": "Room Bed Grade",
                    "department": "Illness Department", 
                    "illness_severity": "Illness Severity"
                }),
                ui.output_ui("conditional_inputs"),
                ui.input_action_button("search_cond_btn", "Search", class_="btn btn-primary")
            )
        elif section == "add_row":
            return ui.TagList(
                ui.input_select("add_table_select", "Select Table", {
                    "cases": "Cases", 
                    "hospitals": "Hospitals", 
                    "patients": "Patients", 
                    "illnesses": "Illnesses", 
                    "rooms": "Rooms"
                }),
                ui.output_ui("add_row_dynamic_fields"),
                ui.input_action_button("add_btn", "Insert Data", class_="btn btn-success")
            )
        return ui.div()

    # Conditional Inputs
    @output
    @render.ui
    def conditional_inputs():
        conditions = input.conditions()
        inputs = []
        if "case_id" in conditions:
            inputs.append(ui.input_text("search_case_id", "Case ID",0))
        if "patient_id" in conditions:
            inputs.append(ui.input_text("search_patient_id", "Patient ID",0))
        if "hospital_id" in conditions:
            inputs.append(ui.input_text("search_hospital_id", "Hospital ID",0))
        if "room_id" in conditions:
            inputs.append(ui.input_text("search_room_id", "Room ID",0))
        if "illness_id" in conditions:
            inputs.append(ui.input_text("search_illness_id", "Illness ID",0))
        if "admission_type" in conditions:
            inputs.append(ui.input_select("search_admission_type", "Admission Type", {
                "trauma": "Trauma", 
                "emergency": "Emergency", 
                "urgent": "Urgent"
            }))
        if "stay_days" in conditions:
            inputs.append(ui.input_select("search_stay_days", "Stay Days", {
                "0-10": "0-10",
                "11-20": "11-20",
                "21-30": "21-30",
                "31-40": "31-40",
                "41-50": "41-50",
                "51-60": "51-60",
                "61-70": "61-70",
                "71-80": "71-80",
                "81-90": "81-90",
                "91-100": "91-100",
                "More than 100": "More than 100"
            }))
        if "city_code" in conditions:
            inputs.append(ui.input_text("search_city_code", "Patient City Code",0))   
        if "age" in conditions:
            inputs.append(ui.input_select("search_age", "Patient Age", {
                "0-10": "0-10",
                "11-20": "11-20",
                "21-30": "21-30",
                "31-40": "31-40",
                "41-50": "41-50",
                "51-60": "51-60",
                "61-70": "61-70",
                "71-80": "71-80",
                "81-90": "81-90",
                "91-100": "91-100"
            }))  
        if "hospital_type" in conditions:
            inputs.append(ui.input_text("search_hospital_type", "Hospital Type",0))
        if "hospital_city" in conditions:
            inputs.append(ui.input_text("search_hospital_city", "Hospital City",0))
        if "hospital_region" in conditions:
            inputs.append(ui.input_text("search_hospital_region", "Hospital Region",0))
        if "ward_type" in conditions:
            inputs.append(ui.input_select("search_ward_type", "Room Ward Facility", {
                "Q": "Q",
                "R": "R",
                "S": "S",
                "T" : "T",
                "U": "U",
                "P" : "P",
            }))    
        if "ward_facility" in conditions:
            inputs.append(ui.input_select("search_ward_facility", "Room Ward Facility", {
                "A": "A", 
                "B": "B", 
                "C": "C", 
                "D": "D", 
                "E": "E", 
                "F": "F"
            }))
        if "bed_grade" in conditions:
            inputs.append(ui.input_text("search_bed_grade", "Room Bed Grade",0))   
        if "department" in conditions:
            inputs.append(ui.input_select("search_department", "Illness Department", {
                "radiotherapy": "Radiotherapy", 
                "anesthesia": "Anesthesia", 
                "gynecology": "Gynecology", 
                "tb_chest_disease": "TB & Chest Disease", 
                "surgery": "Surgery",
                "others": "Others"
            }))
        if "illness_severity" in conditions:
            inputs.append(ui.input_select("search_illness_severity", "Illness Severity", {
                "extreme": "Extreme", 
                "moderate": "Moderate", 
                "minor": "Minor"
            }))
        return ui.TagList(*inputs)

    # Main output based on section selection
    @output
    @render.ui
    def main_output():
        section = input.section()
        if section == "id_search":
            return ui.div(ui.output_table("search_result"), class_="scrollable-table")
        elif section == "conditional_search":
            return ui.div(ui.output_table("conditional_search_result"), class_="scrollable-table")
        elif section == "add_row":
            return ui.output_text_verbatim("add_status")
        return ui.div()

    # Search by ID
    @output
    @render.table
    def search_result():
        r = get_searchid()
        # if input.search_btn():
        #     print("IN add")
        #     print(r)
        #     print(input.search_btn())


        if input.search_btn() == r:
            print(r)
            print(input.search_btn())
            table = input.table_select()
            search_id = input.search_id()
            r = update_searchid()

            result = query_by_id(table, search_id)
            if result:
                return pd.DataFrame([result])
            else:
                return pd.DataFrame()


    # Search with Conditionals
    @output
    @render.table
    def conditional_search_result():
        if input.search_cond_btn():
            conditions = {}

            selected_conditions = input.conditions()

            print("selected_conditions")
            print(selected_conditions)

            if "case_id" in selected_conditions:
                conditions["case_id"] = input.search_case_id()
            if "patient_id" in selected_conditions:
                conditions["patient_id"] = input.search_patient_id()
            if "hospital_id" in selected_conditions:
                conditions["hospital_id"] = input.search_hospital_id()
            if "room_id" in selected_conditions:
                conditions["room_id"] = input.search_room_id()
            if "illness_id" in selected_conditions:
                conditions["illness_id"] = input.search_illness_id()
            if "admission_type" in selected_conditions:
                conditions["admission_type"] = input.search_admission_type()
            if "stay_days" in selected_conditions:
                conditions["stay_days"] = input.search_stay_days()
            if "city_code" in selected_conditions:
                conditions["city_code"] = input.search_city_code()   
            if "age" in selected_conditions:
                conditions["age"] = input.search_age()  
            if "hospital_type" in selected_conditions:
                conditions["hospital_type"] = input.search_ospital_type()
            if "hospital_city" in selected_conditions:
                conditions["hospital_city"] = input.search_hospital_city()
            if "hospital_region" in selected_conditions:
                conditions["hospital_region"] = input.search_hospital_region()
            if "ward_type" in selected_conditions:
                conditions["ward_type"] = input.search_ward_type()    
            if "ward_facility" in selected_conditions:
                conditions["ward_facility"] = input.search_ward_facility()
            if "bed_grade" in selected_conditions:
                conditions["bed_grade"] = input.search_bed_grade()   
            if "department" in selected_conditions:
                conditions["department"] = input.search_department()
            if "illness_severity" in selected_conditions:
                conditions["illness_severity"] = input.search_illness_severity()

            search_results = query_by_conditions(conditions)
            return search_results if not search_results.empty else pd.DataFrame()

    # Add Status function to handle dynamic fields
    @output
    @render.text
    def add_status():
        r = get_add()
        if input.add_btn() == r:
            table = input.add_table_select()
            r = update_add()
            new_row = {
                "ID": int(input.new_id()),
                "Field1": input.field1(),
                "Field2": input.field2(),
                "Field3": input.field3()
            }
            if table == "rooms":
                new_row["Field4"] = input.field4()
                new_row["Field5"] = input.field5()
            elif table == "cases":
                new_row["Field4"] = input.field4()
                new_row["Field5"] = input.field5()
                new_row["Field6"] = input.field6()
                new_row["Field7"] = input.field7()
                new_row["Field8"] = input.field8()
            success = add_row_to_table(table, new_row)
            if success:
                return f"Added row to {table} with ID {new_row['ID']}"
            else:
                return "ID already exists."

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
