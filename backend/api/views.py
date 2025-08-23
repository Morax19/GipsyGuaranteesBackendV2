import os
import json
import pyodbc
from datetime import datetime
from django.http import JsonResponse
from json.decoder import JSONDecodeError
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

# CSRF Logic
@api_view(['GET'])
@ensure_csrf_cookie
def getCSRF(request):
    return JsonResponse({'csrfToken': get_token(request)})

# General Views
#   1. User Registration
#   2. User Edit
@csrf_exempt
def userRegister(request):
    if request.method == 'POST':
        connection = None
        cursor = None
        
        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
            # Mandatory fields
            first_name = data.get('FirstName')
            last_name = data.get('LastName')
            email_address = data.get('EmailAddress')
            password = data.get('Password')
            
            if not all([first_name, last_name, email_address, password]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            
            # Optional fields
            address = data.get('Address')
            zip_code = data.get('Zip')
            phone_number = data.get('PhoneNumber')
            role_id = data.get('RoleID')

            # Establish database connection
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};'
            )
            cursor = connection.cursor()

            # Check if the user already exists within a transaction
            cursor.execute("SELECT COUNT(*) FROM Warranty.Users WHERE Users = ?", (email_address,))
            if cursor.fetchone()[0] > 0:
                return JsonResponse({'error': 'User with this email already exists'}, status=400)

            if not role_id:
                # Registro de usuario cliente
                role_id = 3  # Assuming '3' is the roleID for 'Cliente'
            else:
                # Get roleID from role description
                cursor.execute("SELECT RoleID FROM Warranty.Role WHERE Description = ?", (role_id,))
                role_id = cursor.fetchval()

            # Begin a transaction for atomic insertion
            connection.autocommit = False # Ensure we are in a transaction

            # Insert into the Customer table and get the new CustomerID
            customer_sql = """
                INSERT INTO Warranty.Customer (FirstName, LastName, Address, Zip, EmailAddress, PhoneNumber)
                OUTPUT INSERTED.ID
                VALUES (?, ?, ?, ?, ?, ?);
            """
            cursor.execute(customer_sql, (first_name, last_name, address, zip_code, email_address, phone_number))
            
            customer_id = cursor.fetchval()

            # Insert into the Users table
            user_sql = """
                INSERT INTO Warranty.Users (Users, Password, registrationDate, CustomerID, roleID)
                VALUES (?, ?, GETDATE(), ?, ?);
            """
            cursor.execute(user_sql, (email_address, password, customer_id, role_id))

            # Commit the transaction if all operations were successful
            connection.commit()

            return JsonResponse({'message': 'User created successfully'}, status=201)
        
        except pyodbc.Error as db_error:
            # Handle database-specific errors and rollback
            print(f"Database Error: {db_error}")
            if connection:
                connection.rollback()
            return JsonResponse({'error': 'A database error occurred'}, status=500)
            
        except Exception as e:
            # Catch all other exceptions and rollback
            print(f"Error: {e}")
            if connection:
                connection.rollback()
            return JsonResponse({'error': str(e)}, status=500)
            
        finally:
            # Always close the cursor and connection
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def userEdit(request):
    if request.method == 'PUT':
        connection = None
        cursor = None
        
        try:
            # Parse and validate JSON data
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
            # Mandatory fields check
            user_id = data.get('userID')
            first_name = data.get('FirstName')
            last_name = data.get('LastName')
            email_address = data.get('EmailAddress')
            role_id = data.get('roleID')
            
            if not all([user_id, first_name, last_name, email_address, role_id]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            
            # Optional fields
            address = data.get('Address')
            zip_code = data.get('Zip')
            phone_number = data.get('PhoneNumber')
            password = data.get('Password')

            # Establish database connection
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};'
            )
            cursor = connection.cursor()

            # Begin a transaction for atomic updates
            connection.autocommit = False

            # Get the user's current information in a single query
            cursor.execute("SELECT CustomerID, Users FROM Warranty.Users WHERE userID = ?", (user_id,))
            user_info = cursor.fetchone()

            if not user_info:
                return JsonResponse({'error': 'User not found'}, status=404)
            
            if role_id not in ['1', '2', '3']:
                return JsonResponse({'error': 'Invalid role'}, status=400)
            
            customer_id = user_info[0]
            current_email = user_info[1]

            # Only check for email existence if the email is being changed
            print(email_address)
            print(current_email)

            if email_address.lower() != current_email.lower():
                cursor.execute("SELECT COUNT(*) FROM Warranty.Users WHERE Users = ?", (email_address,))
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({'error': 'Email address is already in use by another user'}, status=400)
            
            # Update the Customer table
            customer_sql = """
                UPDATE Warranty.Customer
                SET FirstName = ?, LastName = ?, Address = ?, Zip = ?, EmailAddress = ?, PhoneNumber = ?
                WHERE ID = ?
            """
            cursor.execute(customer_sql, (first_name, last_name, address, zip_code, email_address, phone_number, customer_id))

            # Update the Users table (conditionally update password)
            if password:
                user_sql = """
                    UPDATE Warranty.Users
                    SET Users = ?, Password = ?, roleID = ?
                    WHERE userID = ?
                """
                cursor.execute(user_sql, (email_address, password, role_id, user_id))
            else:
                user_sql = """
                    UPDATE Warranty.Users
                    SET Users = ?, roleID = ?
                    WHERE userID = ?
                """
                cursor.execute(user_sql, (email_address, role_id, user_id))
            
            # Commit the transaction if all operations were successful
            connection.commit()

            return JsonResponse({'message': 'User updated successfully'}, status=200)
        
        except pyodbc.Error as db_error:
            # Handle database-specific errors and rollback
            print(f"Database Error: {db_error}")
            if connection:
                connection.rollback()
            return JsonResponse({'error': 'A database error occurred'}, status=500)
        
        except Exception as e:
            # Catch all other exceptions and rollback
            print(f"Error: {e}")
            if connection:
                connection.rollback()
            return JsonResponse({'error': str(e)}, status=500)
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
# Admin Views
#   Getter Functions
#       1. Get All Roles
#       2. Get All Users
#       3. Get All Branches
#       4. Get All Customers
#       5. Get All Main.Customers
#       6. Admin Login
def adminGetRoles(request):
    if request.method == 'GET':
        connection = None  # Initialize variables to None
        cursor = None
        try:
            # Correct f-string syntax
            connection = pyodbc.connect(f'Driver={{ODBC Driver 18 for SQL Server}};'
                                        f'Server={os.environ["DB_SERVER"]};'
                                        f'Database={os.environ["DB_NAME"]};'
                                        f'UID={os.environ["DB_USER"]};'
                                        f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()
            sql = "SELECT RoleID, Description FROM Warranty.Role"
            cursor.execute(sql)
            roles = cursor.fetchall()
            role_list = [dict(zip([column[0] for column in cursor.description], row)) for row in roles]
            return JsonResponse(role_list, safe=False)
        except Exception as e:
            # Print the actual error to the console for debugging
            print(f"Error: {e}") 
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def adminGetUsers(request):
    if request.method == 'GET':
        connection = None  # Initialize variables to None
        cursor = None
        try:
            # Correct f-string syntax
            connection = pyodbc.connect(f'Driver={{ODBC Driver 18 for SQL Server}};'
                                        f'Server={os.environ["DB_SERVER"]};'
                                        f'Database={os.environ["DB_NAME"]};'
                                        f'UID={os.environ["DB_USER"]};'
                                        f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()
            sql = "SELECT U.userID, U.Users, U.Password, U.registrationDate, U.CustomerID, R.Description FROM Warranty.Users U JOIN Warranty.Role R ON U.roleID = R.RoleID"
            cursor.execute(sql)
            users = cursor.fetchall()
            user_list = [dict(zip([column[0] for column in cursor.description], row)) for row in users]
            return JsonResponse(user_list, safe=False)
        except Exception as e:
            # Print the actual error to the console for debugging
            print(f"Error: {e}") 
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def adminGetBranches(request):
    if request.method == 'GET':
        connection = None  # Initialize variables to None
        cursor = None
        try:
            # Correct f-string syntax
            connection = pyodbc.connect(f'Driver={{ODBC Driver 18 for SQL Server}};'
                                        f'Server={os.environ["DB_SERVER"]};'
                                        f'Database={os.environ["DB_NAME"]};'
                                        f'UID={os.environ["DB_USER"]};'
                                        f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()
            sql = "SELECT B.branchID, B.customerID, B.isRetail, B.RIFtype, B.RIF, B.companyName, B.address, B.branchDescription FROM Warranty.Branch B"
            cursor.execute(sql)
            branches = cursor.fetchall()
            branch_list = [dict(zip([column[0] for column in cursor.description], row)) for row in branches]
            return JsonResponse(branch_list, safe=False)
        except Exception as e:
            # Print the actual error to the console for debugging
            print(f"Error: {e}") 
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def adminGetCustomers(request):
    if request.method == 'GET':
        connection = None  # Initialize variables to None
        cursor = None
        try:
            # Correct f-string syntax
            connection = pyodbc.connect(f'Driver={{ODBC Driver 18 for SQL Server}};'
                                        f'Server={os.environ["DB_SERVER"]};'
                                        f'Database={os.environ["DB_NAME"]};'
                                        f'UID={os.environ["DB_USER"]};'
                                        f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()
            sql = "SELECT C.ID, C.FirstName + '' + C.LastName AS FullName FROM Warranty.Customer C"
            cursor.execute(sql)
            customers = cursor.fetchall()
            customer_list = [dict(zip([column[0] for column in cursor.description], row)) for row in customers]
            return JsonResponse(customer_list, safe=False)
        except Exception as e:
            # Print the actual error to the console for debugging
            print(f"Error: {e}") 
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def adminGetMainCustomers(request):
    if request.method == 'GET':
        connection = None  # Initialize variables to None
        cursor = None
        try:
            # Correct f-string syntax
            connection = pyodbc.connect(f'Driver={{ODBC Driver 18 for SQL Server}};'
                                        f'Server={os.environ["DB_SERVER"]};'
                                        f'Database={os.environ["DB_NAME"]};'
                                        f'UID={os.environ["DB_USER"]};'
                                        f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()
            sql = """
                SELECT DISTINCT(C.ID), C.FirstName + '' + C.LastName AS FullName, C.isRetail
                FROM Main.Customer C
                JOIN Warranty.Inventory I ON C.ID = I.customerID
                ORDER BY FullName
            """
            cursor.execute(sql)
            customers = cursor.fetchall()
            customer_list = [dict(zip([column[0] for column in cursor.description], row)) for row in customers]
            return JsonResponse(customer_list, safe=False)
        except Exception as e:
            # Print the actual error to the console for debugging
            print(f"Error: {e}") 
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def adminLogin(request):
    if request.method == 'POST':
        connection = None
        cursor = None

        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                print("Wrong JSON")
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
            email_address = data.get('EmailAddress')
            password = data.get('Password')

            if not all([email_address, password]):
                print("Missing fields")
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            # Establish database connection
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};'
            )
            cursor = connection.cursor()

            # Retrieve user information and hashed password in a single query
            sql = """
                SELECT U.Password, R.Description 
                FROM Warranty.Users U JOIN Warranty.Role R ON U.roleID = R.RoleID
                WHERE U.Users = ?;
            """
            cursor.execute(sql, (email_address,))
            user_data = cursor.fetchone()

            # Check if user exists and if the password is correct
            if not user_data:
                # Use a generic error message to prevent username enumeration
                return JsonResponse({'error': 'Invalid username or password'}, status=401)

            stored_password = user_data[0]
            user_role = user_data[1]

            # Verify the password using bcrypt.checkpw()
            if not password == stored_password:
                return JsonResponse({'error': 'Invalid username or password'}, status=401)

            # Check if the user has the correct role for this login path
            if user_role != 'Administrador':
                return JsonResponse({'error': 'Unauthorized access'}, status=403)
            
            # You would generate and return a session token or JWT here
            return JsonResponse({'message': 'Login successful', 'role': user_role}, status=200)

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

#   Setter Functions
#       1. Create Branch
#       2. Edit Branch
@csrf_exempt
def adminCreateBranch(request):
    if request.method == 'POST':
        connection = None
        cursor = None
        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
            customerID = data.get('customerID')
            isRetail = data.get('isRetail')
            RIFtype = data.get('RIFtype')
            RIF = data.get('RIF')
            companyName = data.get('companyName')
            address = data.get('address')
            branchDescription = data.get('branchDescription')

            if not all([customerID, isRetail, RIFtype, RIF, companyName, address, branchDescription]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            connection = pyodbc.connect(f'Driver={{ODBC Driver 18 for SQL Server}};'
                                        f'Server={os.environ["DB_SERVER"]};'
                                        f'Database={os.environ["DB_NAME"]};'
                                        f'UID={os.environ["DB_USER"]};'
                                        f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            # Check if branch already exists
            cursor.execute("SELECT COUNT(*) FROM Warranty.Branch WHERE Branch.RIF = ?", (RIF,))
            if cursor.fetchone()[0] > 0:
                return JsonResponse({'error': 'Branch already exists'}, status=400)

            sql = """
                INSERT INTO Warranty.Branch (customerID, isRetail, RIFtype, RIF, companyName, address, branchDescription)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql, (customerID, isRetail, RIFtype, RIF, companyName, address, branchDescription))
            connection.commit()

            return JsonResponse({'message': 'Branch created successfully'}, status=201)
        
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def adminEditBranch(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            branchID = data.get('branchID')
            customerID = data.get('customerID')
            isRetail = data.get('isRetail')
            RIFtype = data.get('RIFtype')
            RIF = data.get('RIF')
            companyName = data.get('companyName')
            address = data.get('address')
            branchDescription = data.get('branchDescription')

            if not all([branchID, customerID, isRetail, RIFtype, RIF, companyName, address, branchDescription]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            connection = pyodbc.connect(f'Driver={{ODBC Driver 18 for SQL Server}};'
                                        f'Server={os.environ["DB_SERVER"]};'
                                        f'Database={os.environ["DB_NAME"]};'
                                        f'UID={os.environ["DB_USER"]};'
                                        f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            # Check if username already exists
            cursor.execute("SELECT COUNT(*) FROM Warranty.Branch WHERE Branch.branchID = ? AND Branch.RIF = ?", (branchID, RIF))
            if cursor.fetchone()[0] > 0:
                return JsonResponse({'error': 'Username already exists'}, status=400)

            sql = """
                UPDATE Warranty.Branch
                SET customerID = ?, isRetail = ?, RIFtype = ?, RIF = ?, companyName = ?, address = ?, branchDescription = ?
                WHERE branchID = ?
            """
            cursor.execute(sql, (customerID, isRetail, RIFtype, RIF, companyName, address, branchDescription, branchID))
            connection.commit()

            return JsonResponse({'message': 'Branch updated successfully'}, status=200)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    

# User Views
#   1. Login
@csrf_exempt
def userLogin(request):
    if request.method == 'POST':
        connection = None
        cursor = None

        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
            email_address = data.get('EmailAddress')
            password = data.get('Password')

            if not all([email_address, password]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            # Establish database connection
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};'
            )
            cursor = connection.cursor()

            # Retrieve user information and hashed password in a single query
            sql = """
                SELECT U.Password, R.Description 
                FROM Warranty.Users U JOIN Warranty.Role R ON U.roleID = R.RoleID
                WHERE U.Users = ?;
            """
            cursor.execute(sql, (email_address,))
            user_data = cursor.fetchone()

            # Check if user exists and if the password is correct
            if not user_data:
                # Use a generic error message to prevent username enumeration
                return JsonResponse({'error': 'Invalid username or password'}, status=401)

            stored_password = user_data[0]
            user_role = user_data[1]

            # Verify the password using bcrypt.checkpw()
            if not password == stored_password:
                return JsonResponse({'error': 'Invalid username or password'}, status=401)

            # Check if the user has the correct role for this login path
            if user_role != 'Cliente':
                return JsonResponse({'error': 'Unauthorized access'}, status=403)
            
            # You would generate and return a session token or JWT here
            return JsonResponse({'message': 'Login successful', 'role': user_role}, status=200)

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# Technical service Views
#   1. Login
@csrf_exempt
def technicalServiceLogin(request):
    if request.method == 'POST':
        connection = None
        cursor = None

        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
            email_address = data.get('EmailAddress')
            password = data.get('Password')

            if not all([email_address, password]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            # Establish database connection
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};'
            )
            cursor = connection.cursor()

            # Retrieve user information and hashed password in a single query
            sql = """
                SELECT U.Password, R.Description 
                FROM Warranty.Users U JOIN Warranty.Role R ON U.roleID = R.RoleID
                WHERE U.Users = ?;
            """
            cursor.execute(sql, (email_address,))
            user_data = cursor.fetchone()

            # Check if user exists and if the password is correct
            if not user_data:
                # Use a generic error message to prevent username enumeration
                return JsonResponse({'error': 'Invalid username or password'}, status=401)

            stored_password = user_data[0]
            user_role = user_data[1]

            # Verify the password using bcrypt.checkpw()
            if not password == stored_password:
                return JsonResponse({'error': 'Invalid username or password'}, status=401)

            # Check if the user has the correct role for this login path
            if user_role != 'Servicio Técnico':
                return JsonResponse({'error': 'Unauthorized access'}, status=403)
            
            # You would generate and return a session token or JWT here
            return JsonResponse({'message': 'Login successful', 'role': user_role}, status=200)

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)