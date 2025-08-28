import os
import jwt
import json
import pyodbc
import requests
import datetime
from .utils import jwt_required
from django.http import JsonResponse
from json.decoder import JSONDecodeError
from .onedrive import get_onedrive_headers
from django.views.decorators.csrf import csrf_exempt

# Conexión a OneDrive
def get_onedriveProofsOfPayments(invoiceEntries):
    headers = get_onedrive_headers()
    folder_path = "/GARANTIAS/Facturas"
    updated_entries = []
    
    for entry in invoiceEntries:
        if entry[7]:
            filename = entry[7].split('/')[-1]
            file_url = f"https://graph.microsoft.com/v1.0/users/desarrollo@grupogipsy.com/drive/root:{folder_path}/{filename}"

            try:
                response = requests.get(file_url, headers=headers)
                if response.status_code == 200:
                    file_data = response.json()
                    
                    file_id = file_data['id']

                    # Generación de enlace de compartición
                    share_url = f"https://graph.microsoft.com/v1.0/users/desarrollo@grupogipsy.com/drive/items/{file_id}/createLink"
                    share_data = {
                        "type": "view",
                        "scope": "anonymous"
                    }
                    share_response = requests.post(share_url, headers=headers, json=share_data)

                    updated_entry = list(entry)
                    if share_response.status_code == 200:
                        shared_link = share_response.json()["link"]["webUrl"]
                        updated_entry[7] = {
                            'url': shared_link,
                            'name': filename,
                            'error': False,
                            'email_url': f"https://graph.microsoft.com/v1.0/users/desarrollo@grupogipsy.com/drive/items/{file_id}/content"
                        }
                    else:
                        shared_link = file_data.get('webUrl')
                        updated_entry[7] = {
                            'url': shared_link,
                            'name': filename,
                            'error': True,
                            'email_url': f"https://graph.microsoft.com/v1.0/users/desarrollo@grupogipsy.com/drive/items/{file_id}/content"
                        }

                    updated_entries.append(tuple(updated_entry))
                
                else:
                    updated_entries.append(entry)
            
            except Exception as e:
                updated_entries.append(entry)
    
    return updated_entries

# General use Views
#   Get Roles
#   Get Users
#   Get Branches
#   Get CustomerByID
#   Get Main.Customers (With Warranty.Inventory)

@jwt_required
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
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            return JsonResponse({'error': f'A database error ocurred: {db_error}'}, status=500)
        
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

@jwt_required
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
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            return JsonResponse({'error': f'A database error ocurred: {db_error}'}, status=500)        
        
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

@jwt_required
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
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            return JsonResponse({'error': f'A database error ocurred: {db_error}'}, status=500)        
        
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

@jwt_required
def getBranchByCustomerID(request):
    if request.method == 'GET':
        customer_id = request.GET.get('customerID')
        isRetail = request.GET.get('isRetail')

        if not customer_id:
            return JsonResponse({'error': 'Se querie el parámetro customerID'}, status=400)
        if not isRetail:
            return JsonResponse({'error': 'Se querie el parámetro isRetail'}, status=400)

        connection = None
        cursor = None

        try:
            connection = pyodbc.connect(f'Driver={{ODBC Driver 18 for SQL Server}};'
                                        f'Server={os.environ["DB_SERVER"]};'
                                        f'Database={os.environ["DB_NAME"]};'
                                        f'UID={os.environ["DB_USER"]};'
                                        f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            sql = """
                SELECT B.branchID, B.companyName, B.address
                FROM Warranty.Branch B
                WHERE B.customerID = ? AND B.isRetail = ?
                ORDER BY B.companyName
            """
            cursor.execute(sql, (customer_id, isRetail))

            branchesByID = cursor.fetchall()
            branchesByIDList = [dict(zip([column[0] for column in cursor.description], row)) for row in branchesByID]
            return JsonResponse(branchesByIDList, safe=False)
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            return JsonResponse({'error': f'A database error ocurred: {db_error}'}, status=500)        
        
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

@jwt_required
def getProductByBarCode(request):
    if request.method == 'GET':
        barCode = request.GET.get('barCode')

        if not barCode:
            return JsonResponse({'error': 'Missing barCode parameter'}, status=400)

        connection = None
        cursor = None

        try:
            connection = pyodbc.connect(f'Driver={{ODBC Driver 18 for SQL Server}};'
                                        f'Server={os.environ["DB_SERVER"]};'
                                        f'Database={os.environ["DB_NAME"]};'
                                        f'UID={os.environ["DB_USER"]};'
                                        f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            sql = """
                SELECT I.ID, I.CategoryID, I.Description AS productDetail, I.SubDescription3 AS Brand, C.Name AS Category
                FROM Main.Item I
                JOIN Main.Category C ON C.ID = I.CategoryID AND C.isRetail = I.isRetail
                WHERE I.isRetail = 1 AND I.ItemLookupCode = ?
            """
            cursor.execute(sql, barCode)

            item = cursor.fetchone()

            if item:
                item_dict = dict(zip([column[0] for column in cursor.description], item))
                return JsonResponse(item_dict, safe=False)
            else:
                return JsonResponse({'error': 'Producto no encontrado'}, status=404)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            return JsonResponse({'error': f'A database error ocurred: {db_error}'}, status=500)            
        
        except Exception as e:
            print(f"Error: {e}") 
            return JsonResponse({'error': str(e)}, status=500)
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

@jwt_required
def getBranchByCustomerID(request):
    if request.method == 'GET':
        customer_id = request.GET.get('mainCustomerID')
        isRetail = request.GET.get('isRetail')

        if not customer_id:
            return JsonResponse({'error': 'Se querie el parámetro customerID'}, status=400)
        if not isRetail:
            return JsonResponse({'error': 'Se querie el parámetro isRetail'}, status=400)

        connection = None
        cursor = None

        try:
            connection = pyodbc.connect(f'Driver={{ODBC Driver 18 for SQL Server}};'
                                        f'Server={os.environ["DB_SERVER"]};'
                                        f'Database={os.environ["DB_NAME"]};'
                                        f'UID={os.environ["DB_USER"]};'
                                        f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            sql = """
                SELECT B.branchID, B.companyName, B.address, B.RIFtype, B.RIF
                FROM Warranty.Branch B
                WHERE B.customerID = ? AND B.isRetail = ?
                ORDER BY B.companyName
            """
            cursor.execute(sql, (customer_id, isRetail))

            branchesByID = cursor.fetchall()
            branchesByIDList = [dict(zip([column[0] for column in cursor.description], row)) for row in branchesByID]
            return JsonResponse(branchesByIDList, safe=False)
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            return JsonResponse({'error': f'A database error ocurred: {db_error}'}, status=500)

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

@jwt_required
def getCustomerByUserID(request):
    if request.method == 'GET':
        user_id = request.GET.get('userID')
        if not user_id:
            return JsonResponse({'error': 'Missing userID parameter'}, status=400)
        
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

            connection.autocommit = False

            sql = """
                SELECT U.CustomerID
                FROM Warranty.Users U
                WHERE U.userID = ?
            """
            cursor.execute(sql, user_id)
            customer_id = cursor.fetchval()

            if not customer_id:
                return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

            sql = """
                SELECT C.ID, C.FirstName, C.LastName, C.Address, C.Zip, C.EmailAddress, C.PhoneNumber
                FROM Warranty.Customer C
                WHERE C.ID = ?
            """
            cursor.execute(sql, customer_id)
            customer = cursor.fetchone()

            connection.commit()
            if customer:
                customer_dict = dict(zip([column[0] for column in cursor.description], customer))
                return JsonResponse(customer_dict, safe=False)
            else:
                return JsonResponse({'error': 'Customer not found'}, status=404)
        
        except pyodbc.Error as db_error:
            # Handle database-specific errors and rollback
            print(f"Database Error: {db_error}")
            if connection:
                connection.rollback()
            return JsonResponse({'error': 'A database error occurred'}, status=500)    
        
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

@jwt_required
def adminGetCustomerByID(request):
    if request.method == 'GET':
        customer_id = request.GET.get('customerID')
        if not customer_id:
            return JsonResponse({'error': 'Se querie el parámetro customerID'}, status=400)
        
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
                SELECT C.ID, C.FirstName, C.LastName, C.EmailAddress, C.PhoneNumber, C.Address, C.Zip
                FROM Warranty.Customer C
                WHERE C.ID = ?
            """
            cursor.execute(sql, customer_id)
            customer = cursor.fetchone()

            if customer:
                customer_dict = dict(zip([column[0] for column in cursor.description], customer))
                return JsonResponse(customer_dict, safe=False)
            else:
                return JsonResponse({'error': 'Customer not found'}, status=404)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            return JsonResponse({'error': f'A database error ocurred: {db_error}'}, status=500)

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

@jwt_required
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

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            return JsonResponse({'error': f'A database error ocurred: {db_error}'}, status=500)

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
    
@jwt_required
def adminGetMainCustomersRetail(request):
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
                WHERE C.isRetail = 0
                ORDER BY FullName
            """
            cursor.execute(sql)
            customers = cursor.fetchall()
            customer_list = [dict(zip([column[0] for column in cursor.description], row)) for row in customers]
            return JsonResponse(customer_list, safe=False)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            return JsonResponse({'error': f'A database error ocurred: {db_error}'}, status=500)        
        
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
    
# Admin Views
#   1. Login
#   2. Create Users
#   3. Edit Users
#   4. Create Branches
#   5. Edit Branches
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
                return JsonResponse({'error': 'JSON Inválido'}, status=400)
            
            email_address = data.get('EmailAddress')
            password = data.get('Password')

            if not all([email_address, password]):
                print("Missing fields")
                return JsonResponse({'error': 'Ha ocurrido un error con los campos requeridos'}, status=400)

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
                SELECT U.Password, R.Description, U.userID
                FROM Warranty.Users U JOIN Warranty.Role R ON U.roleID = R.RoleID
                WHERE U.Users = ?;
            """
            cursor.execute(sql, (email_address,))
            user_data = cursor.fetchone()

            # Check if user exists and if the password is correct
            if not user_data:
                # Use a generic error message to prevent username enumeration
                return JsonResponse({'error': 'Nombre de usuario o contraseña inválido'}, status=401)

            stored_password = user_data[0]
            user_role = user_data[1]
            user_id = user_data[2]

            # Verify the password
            if not password == stored_password:
                return JsonResponse({'error': 'Nombre de usuario o contraseña inválido'}, status=401)

            # Check if the user has the correct role for this login path
            if user_role != 'Administrador':
                return JsonResponse({'error': 'Acceso no autorizado'}, status=403)
            
            # You would generate and return a session token or JWT here
            jwt_secret = os.environ.get("JWT_SECRET_KEY")

            payload = {
                'user_id': user_id,
                'email_address': email_address,
                'role': user_role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            }

            access_token = jwt.encode(payload, jwt_secret, algorithm='HS256')
            if not jwt_secret:
                return JsonResponse({'error': 'Server misconfiguration: missing JWT secret key'}, status=404)
            
            return JsonResponse({
                'message': 'Inicio de sesión éxitoso',
                'access_token': access_token
                }, status=200)
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            return JsonResponse({'error': f'A database error ocurred: {db_error}'}, status=500)
        
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
@jwt_required
def adminCreateUsers(request):
    if request.method == 'POST':
        connection = None
        cursor = None

        try:
            # Parse and validate JSON data
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'error': 'JSON Inválido'}, status=400)

            # Mandatory fields
            first_name = data.get('FirstName')
            last_name = data.get('LastName')
            email_address = data.get('EmailAddress')
            password = data.get('Password')
            role_id = data.get('roleID')
            
            if not all([first_name, last_name, email_address, password, role_id]):
                return JsonResponse({'error': 'Ha ocurrido un error con los campos requeridos'}, status=400)
            
            # Optional fields
            address = data.get('Address')
            zip_code = data.get('Zip')
            phone_number = data.get('PhoneNumber')

            # DB connection
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
                return JsonResponse({'error': 'Ya existe un usuario asociado a este correo electrónico'}, status=400)

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

            return JsonResponse({'message': 'Usuario registrado éxitosamente'}, status=201)
        
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
@jwt_required
def adminEditUsers(request):
    if request.method == 'PUT':
        connection = None
        cursor = None
        
        try:
            # Parse and validate JSON data
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'error': 'JSON Inválido'}, status=400)
            
            # Mandatory fields check
            user_id = data.get('userID')
            first_name = data.get('FirstName')
            last_name = data.get('LastName')
            email_address = data.get('EmailAddress')
            role_id = data.get('roleID')
            
            if not all([user_id, first_name, last_name, email_address, role_id]):
                return JsonResponse({'error': 'Ha ocurrido un error con los campos requeridos'}, status=400)
            
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
                return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
            
            if role_id not in ['1', '2', '3']:
                return JsonResponse({'error': 'Invalid role'}, status=400)
            
            customer_id = user_info[0]
            current_email = user_info[1]

            if email_address.lower() != current_email.lower():
                cursor.execute("SELECT COUNT(*) FROM Warranty.Users WHERE Users = ?", (email_address,))
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({'error': 'Este correo electrónico ya se encuentra asociado a un usuario'}, status=400)
            
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

            return JsonResponse({'message': 'Información del usuario editada con éxito'}, status=200)
        
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

@csrf_exempt
@jwt_required
def adminCreateBranch(request):
    if request.method == 'POST':
        connection = None
        cursor = None
        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'error': 'JSON Inválido'}, status=400)
            
            customerID = data.get('customerID')
            isRetail = data.get('isRetail')
            RIFtype = data.get('RIFtype')
            RIF = data.get('RIF')
            companyName = data.get('companyName')
            address = data.get('address')
            branchDescription = data.get('branchDescription')

            if not isRetail:
                isRetail = 0

            if customerID is None or not all([RIFtype, RIF, companyName, address, branchDescription]):
                return JsonResponse({'error': 'Ha ocurrido un error con los campos requeridos'}, status=400)

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
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            return JsonResponse({'error': f'A database error ocurred: {db_error}'}, status=500)
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
@jwt_required
def adminEditBranch(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
            branchID = data.get('branchID')
            customerID = data.get('customerID')
            RIFtype = data.get('RIFtype')
            isRetail = data.get('isRetail')
            RIF = data.get('RIF')
            companyName = data.get('companyName')
            address = data.get('address')
            branchDescription = data.get('branchDescription')

            if not isRetail:
                isRetail = 0

            if customerID is None or not all([branchID, RIFtype, RIF, companyName, address, branchDescription]):
                return JsonResponse({'error': 'Ha ocurrido un error con los campos requeridos'}, status=400)

            connection = pyodbc.connect(f'Driver={{ODBC Driver 18 for SQL Server}};'
                                        f'Server={os.environ["DB_SERVER"]};'
                                        f'Database={os.environ["DB_NAME"]};'
                                        f'UID={os.environ["DB_USER"]};'
                                        f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

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

# Technical Service Views
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
                return JsonResponse({'error': 'JSON Inválido'}, status=400)
            
            email_address = data.get('EmailAddress')
            password = data.get('Password')

            if not all([email_address, password]):
                return JsonResponse({'error': 'Ha ocurrido un error con los campos requeridos'}, status=400)

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
                SELECT U.Password, R.Description, U.userID
                FROM Warranty.Users U JOIN Warranty.Role R ON U.roleID = R.RoleID
                WHERE U.Users = ?;
            """
            cursor.execute(sql, (email_address,))
            user_data = cursor.fetchone()

            # Check if user exists and if the password is correct
            if not user_data:
                # Use a generic error message to prevent username enumeration
                return JsonResponse({'error': 'Nombre de usuario o contraseña inválido'}, status=401)

            stored_password = user_data[0]
            user_role = user_data[1]
            user_id = user_data[2]

            # Verify the password
            if not password == stored_password:
                return JsonResponse({'error': 'Nombre de usuario o contraseña inválido'}, status=401)

            # Check if the user has the correct role for this login path
            if user_role != 'Servicio Técnico' and user_role != 'Administrador':
                return JsonResponse({'error': 'Acceso no autorizado'}, status=403)
            
            # You would generate and return a session token or JWT here
            jwt_secret = os.environ.get("JWT_SECRET_KEY")
            if not jwt_secret:
                return JsonResponse({'error': 'Server misconfiguration: missing JWT secret key'}, status=404)

            payload = {
                'user_id': user_id,
                'email_address': email_address,
                'role': user_role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            }

            access_token = jwt.encode(payload, jwt_secret, algorithm='HS256')
            
            return JsonResponse({
                'message': 'Inicio de sesión éxitoso',
                'access_token': access_token
                }, status=200)
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            return JsonResponse({'error': f'A database error ocurred: {db_error}'}, status=500)
        
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

@jwt_required
def technicalServiceGetWarrantyByID(request):
    if request.method == 'GET':
        warranty_number = request.GET.get('WarrantyNumber')

        if not warranty_number:
            return JsonResponse({'error': 'El número de garantía no puede estar vacío'}, status=400)

        connection = None
        cursor = None

        try:
            connection = pyodbc.connect(f'Driver={{ODBC Driver 18 for SQL Server}};'
                                    f'Server={os.environ["DB_SERVER"]};'
                                    f'Database={os.environ["DB_NAME"]};'
                                    f'UID={os.environ["DB_USER"]};'
                                    f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            sql = """
                SELECT W.WarrantyNumber, W.purchaseDate, W.invoiceNumber, I.Description AS Brand, I.SubDescription3 AS Model, S.description, W.usedCount, COALESCE(TSS.statusDescription, 'N/A') AS TechnicalServiceStatus
                FROM Warranty.warranty W
                JOIN Main.Item I ON W.ItemId = I.ID
                JOIN Warranty.warrantyStatus S ON W.statusID = S.statusID
                LEFT JOIN Warranty.technicalService TS ON W.WarrantyNumber = TS.warrantyID
                LEFT JOIN Warranty.technicalServiceStatus TSS ON TS.statusID = TSS.statusID
                WHERE W.WarrantyNumber = ?
            """
            cursor.execute(sql, (warranty_number, ))

            warranty = cursor.fetchone()

            if warranty:
                warranty_dict = dict(zip([column[0] for column in cursor.description], warranty))
                return JsonResponse(warranty_dict, safe=False)
            else:
                return JsonResponse({'error': 'Garantía no encontrada'}, status=404)

        except pyodbc.Error as db_error:
            # Handle database-specific errors and rollback
            print(f"Database Error: {db_error}")
            if connection:
                connection.rollback()
            return JsonResponse({'error': 'A database error occurred'}, status=500)    

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
@jwt_required
def technicalServiceOpenCaseWarranty(request):
    if request.method == 'POST':
        connection = None
        cursor = None

        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'error': 'JSON Inválido'}, status=400)

            # Mandatory fields
            register_id = data.get('registerID')
            warranty_id = data.get('WarrantyID')

            if not all([register_id, warranty_id]):
                print(register_id)
                print(warranty_id)
                return JsonResponse({'error': 'Ha ocurrido un error con los campos requeridos'}, status=400)

            # Optional fields
            issue_id = 0
            issue_resolution_details = ''
            status_id = 1

            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};'
            )
            cursor = connection.cursor()

            connection.autocommit = False

            sql = """
                INSERT INTO Warranty.technicalService (registerID, warrantyID, issueID, issueResolutionDetails, statusID, receptionDate)
                VALUES (?, ?, NULL, NULL, ?, GETDATE())
            """
            cursor.execute(sql, (register_id, warranty_id, status_id))

            connection.commit()
            return JsonResponse({'message': 'Se ha abierto el caso éxitosamente'}, status=200)
        
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
        return JsonResponse({'error:' 'Invalid request method'}, status=405)

def technicalServiceHistory(request):
    if request.method == 'GET':
        connection = None
        cursor = None

        user_id = request.GET.get('userID')

        if not user_id:
            return JsonResponse({'error': 'Usuario inválido'}, status=400)

        try:
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};'
            )
            cursor = connection.cursor()
            
            """
            Flujo real deshabilitado mientras se valida el tema de las sucursales asociadas al servicio técnico

            sql = 
                SELECT U.branchID
                FROM Warranty.Users U
                WHERE U.userID = ?
            
            cursor.execute(sql, (user_id))

            branch_id = cursor.fetchval()

            if not branch_id:
                return JsonResponse({'error': 'No se pudo obtener la sucursal a la que se encuentra asociado'}, status=400)

            sql = 
                SELECT TS.CaseNumber, TS.warrantyID, TS.receptionDate, C.FirstName + ' ' + C.LastName AS Customer, B.companyName, I.Description, TSS.statusDescription, W.branchID
                FROM Warranty.technicalService TS
                JOIN Warranty.Users U ON TS.registerID = U.userID
                JOIN Warranty.Customer C ON U.CustomerID = C.ID
                JOIN Warranty.warranty W ON TS.warrantyID = W.WarrantyNumber
                JOIN Warranty.Branch B ON W.branchID = B.branchID
                JOIN Main.Item I ON W.ItemId = I.ID AND W.isRetail = I.isRetail
                JOIN Warranty.technicalServiceStatus TSS ON TS.statusID = TSS.statusID
                WHERE W.branchID = ?
            

            cursor.execute(sql, (branch_id))
            """

            sql = """
                SELECT TS.CaseNumber, TS.warrantyID, TS.receptionDate, C.FirstName + ' ' + C.LastName AS Customer, B.companyName, I.Description, TSS.statusDescription, W.branchID
                FROM Warranty.technicalService TS
                JOIN Warranty.Users U ON TS.registerID = U.userID
                JOIN Warranty.Customer C ON U.CustomerID = C.ID
                JOIN Warranty.warranty W ON TS.warrantyID = W.WarrantyNumber
                JOIN Warranty.Branch B ON W.branchID = B.branchID
                JOIN Main.Item I ON W.ItemId = I.ID AND W.isRetail = I.isRetail
                JOIN Warranty.technicalServiceStatus TSS ON TS.statusID = TSS.statusID
            """
            cursor.execute(sql)
            ts_cases = cursor.fetchall()

            if ts_cases:
                ts_list = [dict(zip([column[0] for column in cursor.description], row)) for row in ts_cases]
                return JsonResponse(ts_list, safe=False)
            else:
                return JsonResponse({'error': 'No se encontraron resultados'}, status=400)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            print(f"Error: {db_error}")
            return JsonResponse({'error': f'A database error ocurred: {db_error}'}, status=500)

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

def technicalServiceGetStatus(request):
    if request.method == 'GET':
        connection = None
        cursor = None
        
        try:
            connection = pyodbc.connect(f'Driver={{ODBC Driver 18 for SQL Server}};'
                                        f'Server={os.environ["DB_SERVER"]};'
                                        f'Database={os.environ["DB_NAME"]};'
                                        f'UID={os.environ["DB_USER"]};'
                                        f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()
            
            sql = """
                SELECT statusID, statusDescription
                FROM Warranty.technicalServiceStatus
            """
            cursor.execute(sql)
            status = cursor.fetchall()
            
            if status:
                status_list = [dict(zip([column[0] for column in cursor.description], row)) for row in status]
                return JsonResponse(status_list, safe=False)
            else:
                return JsonResponse({'error': 'No se encontraron resultados'}, status=400)
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            
            print(f"Error: {db_error}")
            return JsonResponse({'error': f'A database error ocurred: {db_error}'}, status=500)
        
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

def technicalServiceGetIssue(request):
    if request.method == 'GET':
        connection = None
        cursor = None
        
        try:
            connection = pyodbc.connect(f'Driver={{ODBC Driver 18 for SQL Server}};'
                                        f'Server={os.environ["DB_SERVER"]};'
                                        f'Database={os.environ["DB_NAME"]};'
                                        f'UID={os.environ["DB_USER"]};'
                                        f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()
            
            sql= """
                SELECT IssueId, IssueDescription
                FROM Warranty.Issue
            """
            cursor.execute(sql)
            issue = cursor.fetchall()
            
            if issue:
                issue_list = [dict(zip([column[0] for column in cursor.description], row)) for row in issue]
                return JsonResponse(issue_list, safe=False)
            else:
                return JsonResponse({'error': 'No se encontraron resultados'}, status=400)
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            
            print(f"Error: {db_error}")
            return JsonResponse({'error': f'A database error ocurred: {db_error}'}, status=500)
        
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

def technicalServiceUpdateCase(request):
    if request.method == 'PUT':
        connection = None
        cursor = None
        
        try:
            # Parse and validate JSON data
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'error': 'JSON Inválido'}, status=400)
            
            # Mandatory fields check
            
            if not all([]):
                return JsonResponse({'error': 'Ha ocurrido un error con los campos requeridos'}, status=400)
            
            # Optional fields
            

            # Establish database connection
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};'
            )
            cursor = connection.cursor()

                    
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

def technicalServiceCloseCase(request):
    sql = """
        UPDATE Warranty.technicalService
        SET issueID = ?, issueResolutionDetails = ?, statusID = 3
        WHERE CaseNumber = ?
    """
    # cursor.execute(sql, (issueID, issueResolutionDetails, CaseNumber))
    return

# User Views
#   1. Login
#   2. Public Register
#   3. Warranty Register
#   4. Warranty History
#   5. Edit Profile
#   6. Change Password
@csrf_exempt
def userLogin(request):
    if request.method == 'POST':
        connection = None
        cursor = None

        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'error': 'JSON Inválido'}, status=400)
            
            email_address = data.get('EmailAddress')
            password = data.get('Password')

            if not all([email_address, password]):
                return JsonResponse({'error': 'Ha ocurrido un error con los campos requeridos'}, status=400)

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
                SELECT U.Password, R.Description, U.userID, U.Users
                FROM Warranty.Users U JOIN Warranty.Role R ON U.roleID = R.RoleID
                WHERE U.Users = ?;
            """
            cursor.execute(sql, (email_address,))
            user_data = cursor.fetchone()

            # Check if user exists and if the password is correct
            if not user_data:
                # Use a generic error message to prevent username enumeration
                return JsonResponse({'error': 'Nombre de usuario o contraseña inválido'}, status=401)

            stored_password = user_data[0]
            user_role = user_data[1]
            user_id = user_data[2]

            # Verify the password
            if not password == stored_password:
                return JsonResponse({'error': 'Nombre de usuario o contraseña inválido'}, status=401)

            # Check if the user has the correct role for this login path
            if user_role != 'Cliente' and user_role != 'Administrador':
                return JsonResponse({'error': 'Acceso no autorizado'}, status=403)
            
            # You would generate and return a session token or JWT here
            jwt_secret = os.environ.get("JWT_SECRET_KEY")
            if not jwt_secret:
                return JsonResponse({'error': 'Server misconfiguration: missing JWT secret key'}, status=404)
            
            payload = {
                'user_id': user_id,
                'email_address': email_address,
                'role': user_role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            }

            access_token = jwt.encode(payload, jwt_secret, algorithm='HS256')
            
            return JsonResponse({
                'message': 'Inicio de sesión éxitoso',
                'access_token': access_token
                }, status=200)
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            return JsonResponse({'error': f'A database error ocurred: {db_error}'}, status=500)
        
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
def publicRegister(request):
    if request.method == 'POST':
        connection = None
        cursor = None
        
        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'error': 'JSON Inválido'}, status=400)
            
            # Mandatory fields
            first_name = data.get('FirstName')
            last_name = data.get('LastName')
            email_address = data.get('EmailAddress')
            password = data.get('Password')
            role_id = 3  # Assuming '3' is the roleID for 'Cliente'
            
            if not all([first_name, last_name, email_address, password]):
                return JsonResponse({'error': 'Ha ocurrido un error con los campos requeridos'}, status=400)
            
            # Optional fields
            address = data.get('Address')
            zip_code = data.get('Zip')
            phone_number = data.get('PhoneNumber')

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
                return JsonResponse({'error': 'Ya existe un usuario asociado a este correo electrónico'}, status=400)

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

            return JsonResponse({'message': 'Usuario registrado éxitosamente'}, status=201)
        
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
@jwt_required
def warrantyRegister(request):
    if request.method == 'POST':
        connection = None
        cursor = None

        try:
            # Mandatory fields
            register_id = request.POST['registerID']
            branch_id = request.POST['branchID']
            item_id = request.POST['ItemId']
            is_retail = request.POST['isRetail']
            purchase_date = request.POST['purchaseDate']
            status_id = 1
            product_brand = request.POST['productBrand']
            product_barcode = request.POST['productBarcode']
            invoice_img = request.FILES['invoiceIMG']
            used_count = 0
            invoice_number = request.POST['invoiceNumber']

            if not all([
                register_id,
                branch_id,
                item_id,
                is_retail,
                purchase_date,
                status_id,
                product_brand,
                product_barcode,
                invoice_img,
                invoice_number
            ]):
                return JsonResponse({'error': 'Ha ocurrido un error con los campos requeridos'}, status=400)

            # Almacenamiento de facturas en OneDrive
            headers = get_onedrive_headers()
            ext = invoice_img.name.split('.')[-1]
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = invoice_img.name.replace(" ", "_").replace("/", "_")
            unique_name = f"{timestamp}_{safe_name}"
            folder_path = "/GARANTIAS/Facturas"
            upload_url = f"https://graph.microsoft.com/v1.0/users/desarrollo@grupogipsy.com/drive/root:/{folder_path}/{unique_name}:/content"
            
            resp = requests.put(upload_url, headers=headers, data=invoice_img.read())
            if resp.status_code not in (200, 201):
                return JsonResponse({'error': 'Error al subir la factura a OneDrive', 'details': resp.text}, status=500)

            data = resp.json()
            invoice_copy_path = data["webUrl"]

            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};'
            )
            cursor = connection.cursor()

            # Check if the warranty already exists by invoiceNumber
            cursor.execute("SELECT COUNT(*) FROM Warranty.warranty WHERE invoiceNumber = ? AND ItemId = ?", (invoice_number, item_id))
            if cursor.fetchone()[0] > 0:
                return JsonResponse({'error': 'Ya existe una garantía para este producto asociada a esta factura'}, status=400)

            sql = """
                INSERT INTO Warranty.warranty (registerID, branchID, ItemId, isRetail, purchaseDate, registrationDate, statusID, productBrand, productBarcode, invoiceCopyPath, usedCount, invoiceNumber)
                VALUES (?, ?, ?, ?, ?, GETDATE(), ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql, (register_id, branch_id, item_id, is_retail, purchase_date, status_id, product_brand, product_barcode, invoice_copy_path, used_count, invoice_number))
            connection.commit()

            return JsonResponse({'message': '¡Garantía registrada éxitosamente!'}, status=201)
        
        except pyodbc.Error as db_error:
            print(f"Database Error: {db_error}")
            if connection:
                connection.rollback()
            return JsonResponse({'error': str(db_error)}, status=500)

        except Exception as e:
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

@csrf_exempt
@jwt_required
def updateWarrantyUsedCount(request):
    if request.method == 'PUT':
        connection = None
        cursor = None

        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'error': 'JSON INválido'}, status=400)

            # Mandatory fields
            warranty_number = data.get('WarrantyNumber')

            if not warranty_number:
                return JsonResponse({'error': 'El número de garantía no es válido'}, status=400)

            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};'
            )
            cursor = connection.cursor()

            sql = """
                UPDATE Warranty.warranty
                SET usedCount = usedCount + 1
                WHERE WarrantyNumber = ?
            """
            cursor.execute(sql, (warranty_number,))
            connection.commit()

            return JsonResponse({'message': 'Contador de usos de la garantía actualizado con éxito'}, status=200)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            return JsonResponse({'error': f'A database error occurred: {db_error}'}, status=500)

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

@csrf_exempt
@jwt_required
def warrantyHistory(request):
    if request.method == 'GET':
        connection = None
        cursor = None

        user_id = request.GET.get('userID')

        try:
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};'
            )
            cursor = connection.cursor()

            # Fetch warranty history
            sql = """
                SELECT W.WarrantyNumber, W.purchaseDate, W.registrationDate, W.usedCount, B.companyName, I.Description AS ProductName, S.description AS WarrantyStatus
                FROM Warranty.warranty W
                JOIN Warranty.Branch B ON W.branchID = B.branchID
                JOIN Main.Item I ON W.ItemId = I.ID AND I.isRetail = W.isRetail
                JOIN Warranty.warrantyStatus S ON W.statusID = S.statusID
				WHERE W.registerID = ?  
            """
            cursor.execute(sql, (user_id,))
            warranties = cursor.fetchall()
            warranties_list = [dict(zip([column[0] for column in cursor.description], row)) for row in warranties]
            
            return JsonResponse(warranties_list, safe=False)

        except pyodbc.Error as db_error:
            print(f"Database Error: {db_error}")
            if connection:
                connection.rollback()
            return JsonResponse({'error': str(e)}, status=500)

        except Exception as e:
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
    
@csrf_exempt
@jwt_required
def userProfileEdit(request):
    if request.method == 'PUT':
        connection = None
        cursor = None
        
        try:
            # Parse and validate JSON data
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'error': 'JSON Inválido'}, status=400)
            
            # Mandatory fields check
            user_id = data.get('userID')
            first_name = data.get('FirstName')
            last_name = data.get('LastName')
            email_address = data.get('EmailAddress')
            
            if not all([user_id, first_name, last_name, email_address]):
                return JsonResponse({'error': 'Ha ocurrido un error con los campos requeridos'}, status=400)
            
            # Optional fields
            address = data.get('Address')
            zip_code = data.get('Zip')
            phone_number = data.get('PhoneNumber')

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
                return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
            
            customer_id = user_info[0]
            current_email = user_info[1]

            if email_address.lower() != current_email.lower():
                cursor.execute("SELECT COUNT(*) FROM Warranty.Users WHERE Users = ?", (email_address,))
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({'error': 'Este correo electrónico ya se encuentra asociado a un usuario'}, status=400)
            
            # Update the Customer table
            customer_sql = """
                UPDATE Warranty.Customer
                SET FirstName = ?, LastName = ?, Address = ?, Zip = ?, EmailAddress = ?, PhoneNumber = ?
                WHERE ID = ?
            """
            cursor.execute(customer_sql, (first_name, last_name, address, zip_code, email_address, phone_number, customer_id))

            user_sql = """
                UPDATE Warranty.Users
                SET Users = ?
                WHERE userID = ?
            """
            cursor.execute(user_sql, (email_address, user_id))
            
            # Commit the transaction if all operations were successful
            connection.commit()

            return JsonResponse({'message': 'Información del usuario editada con éxito'}, status=200)
        
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

@csrf_exempt
@jwt_required
def userChangePassword(request):
    if request.method == 'PUT':
        connection = None
        cursor = None

        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'error': 'JSON Inválido'}, status=400)

            # Mandatory fields check
            user_id = data.get('userID')
            current_password = data.get('old_password')
            new_password = data.get('new_password')

            if not all([user_id, current_password, new_password]):
                return JsonResponse({'error': 'Ha ocurrido un error con los campos requeridos'}, status=400)

            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};'
            )
            cursor = connection.cursor()

            cursor.execute("SELECT U.Password FROM Warranty.Users U WHERE U.userID = ?", (user_id,))
            actual_password = cursor.fetchval()

            if current_password != actual_password:
                return JsonResponse({'error': 'Contraseña actual incorrecta'}, status=400)

            sql = """
                UPDATE Warranty.Users
                SET Password = ?
                WHERE userID = ?
            """
            cursor.execute(sql, (new_password, user_id))
            connection.commit()

            return JsonResponse({'message': 'Contraseña actualizada con éxito'}, status=200)

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