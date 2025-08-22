import os
import json
import pyodbc
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

# Admin Views
#   1. Get All Users
#   2. Get All Branches
#   3. Get All Customers
#   4. Create User
#   5. Edit User
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

@csrf_exempt
def adminCreateUser(request):
    if request.method == 'POST':
        connection = None
        cursor = None
        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
            User = data.get('User')
            Password = data.get('Password')
            customerID = data.get('CustomerID')
            roleID = data.get('roleID')

            if not all([User, Password, roleID, customerID]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            connection = pyodbc.connect(f'Driver={{ODBC Driver 18 for SQL Server}};'
                                        f'Server={os.environ["DB_SERVER"]};'
                                        f'Database={os.environ["DB_NAME"]};'
                                        f'UID={os.environ["DB_USER"]};'
                                        f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            # Check if username already exists
            cursor.execute("SELECT COUNT(*) FROM Warranty.Users WHERE Users = ?", (User,))
            if cursor.fetchone()[0] > 0:
                return JsonResponse({'error': 'Username already exists'}, status=400)

            # Get roleID from role description
            cursor.execute("SELECT RoleID FROM Warranty.Role WHERE Description = ?", (roleID,))
            role_row = cursor.fetchone()
            if not role_row:
                return JsonResponse({'error': 'Invalid role'}, status=400)
            roleID = role_row[0]

            sql = """
                INSERT INTO Warranty.Users (Users, Password, registrationDate, CustomerID, roleID)
                VALUES (?, ?, GETDATE(), ?, ?)
            """
            cursor.execute(sql, (User, Password, customerID, roleID))
            connection.commit()

            return JsonResponse({'message': 'User created successfully'}, status=201)
        
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
def adminEditUser(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            userID = data.get('userID')
            User = data.get('User')
            Password = data.get('Password')
            customerID = data.get('CustomerID')
            roleID = data.get('roleID')

            if not all([userID, User, Password, roleID, customerID]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            connection = pyodbc.connect(f'Driver={{ODBC Driver 18 for SQL Server}};'
                                        f'Server={os.environ["DB_SERVER"]};'
                                        f'Database={os.environ["DB_NAME"]};'
                                        f'UID={os.environ["DB_USER"]};'
                                        f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            # Check if username already exists
            cursor.execute("SELECT COUNT(*) FROM Warranty.Users WHERE Users = ? AND userID != ?", (User, userID))
            if cursor.fetchone()[0] > 0:
                return JsonResponse({'error': 'Username already exists'}, status=400)

            # Get roleID from role description
            cursor.execute("SELECT RoleID FROM Warranty.Role WHERE Description = ?", (roleID,))
            role_row = cursor.fetchone()
            if not role_row:
                return JsonResponse({'error': 'Invalid role'}, status=400)
            roleID = role_row[0]

            sql = """
                UPDATE Warranty.Users
                SET Users = ?, Password = ?, CustomerID = ?, roleID = ?
                WHERE userID = ?
            """
            cursor.execute(sql, (User, Password, customerID, roleID, userID))
            connection.commit()

            return JsonResponse({'message': 'User updated successfully'}, status=200)
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
            sql = "SELECT C.ID, C.FirstName + '' + C.LastName AS FullName, C.isRetail FROM Main.Customer C ORDER BY FullName"
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

# User Views
#   1. Registration

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
            
            User = data.get('User')
            Password = data.get('Password')
            customerID = data.get('customerID')
            roleID = data.get('roleID')

            if not all([User, Password, roleID, customerID]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            connection = pyodbc.connect(f'Driver={{ODBC Driver 18 for SQL Server}};'
                                        f'Server={os.environ["DB_SERVER"]};'
                                        f'Database={os.environ["DB_NAME"]};'
                                        f'UID={os.environ["DB_USER"]};'
                                        f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            # Check if username already exists
            cursor.execute("SELECT COUNT(*) FROM Warranty.Users WHERE Users = ?", (User,))
            if cursor.fetchone()[0] > 0:
                return JsonResponse({'error': 'Username already exists'}, status=400)

            # Get roleID from role description
            cursor.execute("SELECT RoleID FROM Warranty.Role WHERE Description = ?", (roleID,))
            role_row = cursor.fetchone()
            if not role_row:
                return JsonResponse({'error': 'Invalid role'}, status=400)
            roleID = role_row[0]

            sql = """
                INSERT INTO Warranty.Users (Users, Password, registrationDate, CustomerID, roleID)
                VALUES (?, ?, GETDATE(), ?, ?)
            """
            cursor.execute(sql, (User, Password, customerID, roleID))
            connection.commit()

            return JsonResponse({'message': 'User created successfully'}, status=201)
        
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
