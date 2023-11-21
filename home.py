import streamlit as st
import mysql.connector as mysql
#import pymysql as mysql
import pandas as pd
import datetime

mydb = mysql.connect(
    host="localhost", user="root", password="Archishmanvb27@", database="college_parking_lot"
)


def execute_query(query, values=None):
    cursor = mydb.cursor(buffered=True)
    if values:
        cursor.execute(query, values)
    else:
        cursor.execute(query)
    mydb.commit()
    return cursor


# CRUD functions for User table
def create_user(user_id, user_name, phone_number, user_type):
    query = "INSERT INTO User_table (UserID, UserName, PhoneNumber, UserType) VALUES (%s, %s, %s, %s)"
    values = (user_id, user_name, phone_number, user_type)
    execute_query(query, values)


def read_user(user_id):
    query = "SELECT * FROM User_table WHERE UserID = %s"
    values = (user_id,)
    cursor = execute_query(query, values)
    return cursor.fetchone()


def update_user(user_id, new_user_name, new_phone_number, new_user_type):
    query = "UPDATE User_table SET UserName = %s, PhoneNumber = %s, UserType = %s WHERE UserID = %s"
    values = (new_user_name, new_phone_number, new_user_type, user_id)
    execute_query(query, values)


def delete_user(user_id):
    query = "DELETE FROM User_table WHERE UserID = %s"
    values = (user_id,)
    execute_query(query, values)

    # CRUD functions for Vehicle table


def create_vehicle(vehicle_id, user_id, vehicle_type):
    query = "INSERT INTO Vehicle (VehicleID, UserID, VehicleType) VALUES (%s, %s,%s)"
    values = (vehicle_id, user_id, vehicle_type)
    execute_query(query, values)


def read_vehicle(vehicle_id):
    query = "SELECT * FROM Vehicle WHERE VehicleID = %s"
    values = (vehicle_id,)
    cursor = execute_query(query, values)
    return cursor.fetchone()




def delete_vehicle(vehicle_id):
    query = "DELETE FROM Vehicle WHERE VehicleID = %s"
    values = (vehicle_id,)
    execute_query(query, values)


# CRUD functions for ParkingRecord table
def update_parking_record(
    new_exit_time,
    record_id,
):
    query = "UPDATE ParkingRecord SET ExitTime = %s WHERE RecordID = %s"
    values = (new_exit_time, record_id)
    execute_query(query, values)


def view_tables():
    st.title("View Tables")

    # Select the table to view
    table_name = st.selectbox(
        "Select Table",
        [
            "User_table",
            "Vehicle",
            "ParkingRecord",
            "ParkingLot",
            "TransactionLog",
            "ParkingPass",
        ],
    )

    # Display the table
    if table_name == "User_table":
        df = pd.read_sql_query("SELECT * FROM User_table", mydb)
    elif table_name == "Vehicle":
        df = pd.read_sql_query("SELECT * FROM Vehicle", mydb)
    elif table_name == "ParkingRecord":
        df = pd.read_sql_query("SELECT * FROM ParkingRecord", mydb)
    elif table_name == "ParkingLot":
        df = pd.read_sql_query("SELECT * FROM ParkingLot", mydb)
    elif table_name == "TransactionLog":
        df = pd.read_sql_query("SELECT * FROM TransactionLog", mydb)
    elif table_name == "ParkingPass":
        df = pd.read_sql_query("SELECT * FROM ParkingPass", mydb)

    st.write(f"Viewing table: {table_name}")
    st.write(df)

def analysis():
    st.title("Analysis")
    action = st.radio(
        "Select your requirement",
        [
            "Count of Vehicles by Type",
            "Total Transactions and Revenue by Payment Method",
            "Users with Multiple Vehicles",
            "Busiest Parking Lots",
            "Owned Vehicles",
        ],
    )
    if action == "Count of Vehicles by Type":
        # nested
        # st.write("Count of Vehicles by Type")
        dff = pd.read_sql_query(
            "SELECT VehicleType, COUNT(*) AS NumVehicles FROM Vehicle WHERE UserID IN (SELECT UserID FROM User_table) GROUP BY VehicleType",
            mydb,
        )
        st.write(dff)

    if action == "Total Transactions and Revenue by Payment Method":
        # join
        # st.write("Total Transactions and Revenue by Payment Method")
        dff = pd.read_sql_query(
            "SELECT TransactionLog.PaymentMethod, COUNT(*) AS NumTransactions, SUM(TransactionLog.Amount) AS TotalRevenue FROM TransactionLog JOIN User_table ON TransactionLog.UserID = User_table.UserID GROUP BY TransactionLog.PaymentMethod",
            mydb,
        )
        st.write(dff)

    if action == "Users with Multiple Vehicles":
        # aggregate
        # st.write("Users with Multiple Vehicles")
        dff = pd.read_sql_query(
            "SELECT UserID, COUNT(*) AS NumVehicles FROM Vehicle GROUP BY UserID HAVING NumVehicles > 1",
            mydb,
        )
        st.write(dff)

    if action == "Busiest Parking Lots":
        # join
        # st.write("Busiest Parking Lots")
        dff = pd.read_sql_query(
            "SELECT ParkingLot.LotName, COUNT(*) AS NumCheckIns FROM ParkingRecord JOIN ParkingLot ON ParkingRecord.LotName = ParkingLot.LotName GROUP BY ParkingLot.LotName ORDER BY NumCheckIns DESC",
            mydb,
        )
        st.write(dff)

    if action == "Owned Vehicles":
        user_id = st.text_input("Enter User ID:")
        if st.button("Display"):
            query = "SELECT Vehicle.* FROM Vehicle JOIN User_table ON Vehicle.UserID = User_table.UserID WHERE User_table.UserID = %s"
            values = (user_id,)
            dff = pd.read_sql_query(query, mydb, params=values)
            st.write(dff)



def register_ui():
    st.write("Select your role")
    user_type = st.selectbox("Select User Type", ["Student", "Employee", "Visitor"])
    user_id = st.text_input("Enter User ID:")
    # handle case when user id already exists
    user_name = st.text_input("Enter User Name:")
    phone_number = st.text_input("Enter Phone Number:")
    vehicle_id = st.text_input("Enter Vehicle ID:")
    vehicle_type = st.selectbox("Select User Type", ["TwoWheeler", "FourWheeler"])

    if st.button("Register"):
        create_user(user_id, user_name, phone_number, user_type)
        create_vehicle(vehicle_id, user_id, vehicle_type)
        st.success("Registration successful.")


def check_in_ui():
    check_in_method = st.radio(
        "How would you like to check in today? ", ["Daily Check In", "Parking Pass"]
    )
    if check_in_method == "Daily Check In":
        user_id = st.text_input("Enter User ID:")
        vehicle_type = st.selectbox(
            "Select Vehicle Type", ["TwoWheeler", "FourWheeler"]
        )
        if vehicle_type == "TwoWheeler":
            amount = 10.00
            st.write("Amount to be paid: Rs 10.00")
        elif vehicle_type == "FourWheeler":
            amount = 20.00
            st.write("Amount to be paid: Rs 20.00")
        payment_method = st.selectbox("Select Payment Method", ["UPI", "Cash"])
        lot_name = st.selectbox("Select Parking Lot", ["GJB", "FBlock", "OpenAir"])
        if st.button("Check In"):
            try:
                # Call the stored procedure
                cursor = mydb.cursor(buffered=True)
                cursor.callproc("CheckIn", args=(user_id, lot_name))
                mydb.commit()
                pass_id = None

                query_transaction_log = "INSERT INTO TransactionLog (UserID, PassID,Amount,TransactionDate,PaymentMethod) VALUES (%s, %s, %s, %s,%s)"
                values_transaction_log = (
                    user_id,
                    pass_id,
                    amount,
                    datetime.datetime.now(),
                    payment_method,
                )
                execute_query(query_transaction_log, values_transaction_log)

                st.success("Check-in successful.")
            except Exception as e:
                st.error(f"Check-in failed. Error: {e}")
            finally:
                cursor.close()

    elif check_in_method == "Parking Pass":
        user_id = st.text_input("Enter User ID:")

        # Check if the user has a parking pass and if it's valid
        query_check_pass = (
            "SELECT * FROM ParkingPass WHERE UserID = %s AND ExpiryDate >= %s"
        )
        values_check_pass = (user_id, datetime.datetime.now())
        cursor_check_pass = execute_query(query_check_pass, values_check_pass)
        parking_pass_record = cursor_check_pass.fetchone()

        if parking_pass_record:
            st.success("Check-in successful.")
        else:
            st.warning(
                "User does not have a valid parking pass or the parking pass has expired."
            )


def check_out_ui():
    user_id = st.text_input("Enter User ID:")
    if st.button("Check Out"):
        try:
            # Find the parking record for the user with no exit time
            query = "SELECT RecordID FROM ParkingRecord WHERE UserID = %s AND ExitTime IS NULL"
            values = (user_id,)
            cursor = execute_query(query, values)
            parking_record = cursor.fetchone()

            if parking_record:
                # Get the current datetime as the exit time
                exit_time = datetime.datetime.now()

                # Update the parking record with the exit time
                update_parking_record(exit_time, parking_record[0])

                st.success("Check-out successful.")
            else:
                st.warning("User has not checked in or has already checked out.")
        except Exception as e:
            st.error(f"Check-out failed. Error: {e}")


def parking_pass_ui():
    user_id = st.text_input("Enter User ID:")
    pass_type = st.selectbox("Select Pass Type", ["Monthly", "Yearly"])
    payment_method = st.selectbox("Select Payment Method", ["UPI", "Cash"])
    amount = 0
    if pass_type == "Monthly":
        amount = 100.00
        st.write("Amount to be paid: Rs 100.00")
    elif pass_type == "Yearly":
        amount = 1200.00
        st.write("Amount to be paid: Rs 1200.00")

    if st.button("Register Parking Pass"):
        try:
            # Set the current date as the issue date
            issue_date = datetime.datetime.now()

            # Calculate the expiry date based on the selected pass type
            if pass_type == "Monthly":
                expiry_date = issue_date + datetime.timedelta(days=30)
            elif pass_type == "Yearly":
                expiry_date = issue_date + datetime.timedelta(days=365)
            else:
                st.warning("Invalid pass type selected.")
                return

            # Insert the parking pass record into the database
            query = "INSERT INTO ParkingPass (UserID, PassType, IssueDate, ExpiryDate) VALUES (%s, %s, %s, %s)"
            values = (user_id, pass_type, issue_date, expiry_date)
            execute_query(query, values)

            query_pass_id = "SELECT PassID FROM ParkingPass WHERE UserID = %s"
            values_pass_id = (user_id,)
            cursor_pass_id = execute_query(query_pass_id, values_pass_id)
            pass_id = cursor_pass_id.fetchone()[0]

            query_transaction_log = "INSERT INTO TransactionLog (UserID, PassID,Amount,TransactionDate,PaymentMethod) VALUES (%s, %s, %s, %s,%s)"
            values_transaction_log = (
                user_id,
                pass_id,
                amount,
                datetime.datetime.now(),
                payment_method,
            )
            execute_query(query_transaction_log, values_transaction_log)

            st.success("Parking pass registration successful.")
        except Exception as e:
            st.error(f"Parking pass registration failed. Error: {e}")

#CRUD for ADMIN
def read_user_admin():
    st.subheader("Read User")
    user_id = st.text_input("Enter User ID:")
    if st.button("Read User"):
        user = read_user(user_id)
        if user:
            st.success("User found:")
            st.write(user)
        else:
            st.warning("User not found.")

def delete_user_admin():
    st.subheader("Delete User")
    user_id = st.text_input("Enter User ID:")
    if st.button("Delete User"):
        try:
            user = read_user(user_id)
            if user:
                delete_user(user_id)
                st.success("User deleted successfully.")
            else:
                st.warning("User not found.")
        except Exception as e:
            st.error(f"Error deleting user: {e}")




def admin_user_management():
    st.title("Admin User Management")
    admin_action = st.selectbox("Select action", ["Read User", "Delete User"])

    if admin_action == "Read User":
        read_user_admin()
    elif admin_action == "Delete User":
        delete_user_admin()

def main():
    st.title("PES Parking Lot Management System")
    # sidebar
    navigation = st.sidebar.radio("Navigation", ["User", "Admin"])
    if navigation == "User":
        action = st.sidebar.selectbox(
            "Select action", ["Register", "Check in", "Check out", "Parking Pass"]
        )

        if action == "Register":
            st.title("Register User")
            register_ui()
        elif action == "Check in":
            st.title("Check In")
            check_in_ui()
        elif action == "Check out":
            st.title("Check Out")
            check_out_ui()
        elif action == "Parking Pass":
            st.title("Purchase Parking Pass")
            parking_pass_ui()

    elif navigation == "Admin":
        admin_action = st.sidebar.selectbox("Select action", ["View tables","Analysis", "User management"])

        if admin_action == "View tables":
            view_tables()
        elif admin_action == "User management":
            admin_user_management()
        elif admin_action == "Analysis":
            analysis()

        





       


if __name__ == "__main__":
    main()
