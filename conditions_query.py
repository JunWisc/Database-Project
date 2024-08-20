def construct_conditional_query(conditions):
    # conditions is a dictionary containing mapping variable to input values.

    # tables query needs to access
    access_tables = set()

    for var in conditions:
        access_tables.add(variable_table_check(var))

    query = "select * from cases "
    
    # equi-join relavent tables
    for t in access_tables:
        end = -1
        if t == "illnesses": end = -2

        query = query + "join " + t + " on cases." + t[:end] + "_id" + " = " + t + "." + t[:end] + "_id "

    # if conditions:
    if conditions:
        query = query + "where "
        for cond in conditions:
            if isinstance(conditions[cond], str): query = query + variable_table_check(cond) + "." + cond + " = \"" + str(conditions[cond]) + "\" AND "
            else: query = query + variable_table_check(cond) + "." + cond + " = " + str(conditions[cond]) + " AND "

        query = query[:-4]

    print(query)

    return query

# returns which table variable belongs to
def variable_table_check(var):

    patients_variables = ["patient_id", "city_code", "age"]
    hospitals_variables = ["hospital_id", "hospital_type", "hospital_city", "hospital_region"]
    rooms_variables = ["room_id", "hospital_id", "ward_type", "ward_facility", "bed_grade"]
    illnesses_variables = ["illness_id", "department", "illness_severity"]
    cases_variables = ["case_id", "patient_id", "hospital_id", "room_id", "illness_id", "admission_type", "patient_visitors", "admission_deposit", "stay_days"]

    if var in patients_variables: return "patients"
    if var in hospitals_variables: return "hospitals"
    if var in rooms_variables: return "rooms"
    if var in illnesses_variables: return "illnesses"
    if var in cases_variables: return "cases"

    return None


conditions = dict()
# conditions["hospital_type"] = 3
# conditions["illness_severity"] = "Extreme"
conditions["patient_id"] = 1
construct_conditional_query(conditions)