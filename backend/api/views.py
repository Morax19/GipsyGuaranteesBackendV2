import os
import jwt
import json
import pyodbc
import requests
import datetime

from .emails import (
    send_user_register_email,
    send_warranty_register_email,
    send_warranty_open_case_email,
    send_warranty_update_case_email,
    send_warranty_close_case_email,
    send_temp_password_email,
)

from django.http import JsonResponse
from json.decoder import JSONDecodeError
from .onedrive import get_onedrive_headers
from django.views.decorators.csrf import csrf_exempt
from .utils import jwt_required, generate_temp_password
    
# General use Views
#   Get Roles
#   Get Users
#   Get Branches
#   Get CustomerByID
#   Get Main.Customers (With Warranty.Inventory)
@jwt_required
def adminGetRoles(request):
    if request.method == 'GET':
        connection = None
        cursor = None

        try:
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            sql = "SELECT RoleID, Description FROM Warranty.Role"
            cursor.execute(sql)

            roles = cursor.fetchall()
            if roles:
                role_list = [dict(zip([column[0] for column in cursor.description], row)) for row in roles]
                return JsonResponse(role_list, safe=False)
            else:
                return JsonResponse({
                    'error': 'Error: No se han encontrado los roles.',
                    'warning': 'Error: No se han encontrado los roles.'
                    }, status=404) 
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'                
                }, status=500)
        
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'              
                }, status=500)
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Error: Invalid request method',
            'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'            
            }, status=405)

@jwt_required
def adminGetUsers(request):
    if request.method == 'GET':
        connection = None
        cursor = None
        
        try:
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            sql = """
                SELECT U.userID, U.Users, U.Password, U.registrationDate, U.CustomerID, R.Description
                FROM Warranty.Users U JOIN Warranty.Role R ON U.roleID = R.RoleID
            """
            cursor.execute(sql)

            users = cursor.fetchall()
            if users:
                user_list = [dict(zip([column[0] for column in cursor.description], row)) for row in users]
                return JsonResponse(user_list, safe=False)
            else:
                return JsonResponse({
                    'error': 'Error: No se han encontrado usuarios.',
                    'warning': 'Error: No se han encontrado usuarios.'                    
                    }, status=404)
            
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'                
                }, status=500)
        
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'
            }, status=405)

@jwt_required
def adminGetBranches(request):
    if request.method == 'GET':
        connection = None
        cursor = None
        
        try:
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            sql = """
                SELECT B.branchID, B.customerID, B.isRetail, B.RIFtype, B.RIF, B.companyName, B.address, B.branchDescription
                FROM Warranty.Branch B
            """
            cursor.execute(sql)

            branches = cursor.fetchall()
            if branches:
                branch_list = [dict(zip([column[0] for column in cursor.description], row)) for row in branches]
                return JsonResponse(branch_list, safe=False)
            else:
                return JsonResponse({
                    'error': 'No se han encontrado sucursales',
                    'warning': 'Error: No se han encontrado sucursales.'
                    }, status=404)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)         
        
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500) 
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'
        }, status=405)

@jwt_required
def getBranchByCustomerID(request):
    if request.method == 'GET':
        customer_id = request.GET.get('customerID')
        isRetail = request.GET.get('isRetail')

        if not all([customer_id, isRetail]):
            return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)

        connection = None
        cursor = None

        try:
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
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
            if branchesByID:
                branchesByIDList = [dict(zip([column[0] for column in cursor.description], row)) for row in branchesByID]
                return JsonResponse(branchesByIDList, safe=False)
            else:
                return JsonResponse({
                    'error': 'Error: Sucursales no encontradas',
                    'warning': 'Error: Sucursales no encontradas'
                    }, status=404)
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)         
        
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500) 
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'            
            }, status=405)

@jwt_required
def getProductByBarCode(request):
    if request.method == 'GET':
        barCode = request.GET.get('barCode')

        if not barCode:
            return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400) 

        connection = None
        cursor = None

        try:
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            sql = """
                SELECT I.ID, I.CategoryID, I.Description AS productDetail, I.SubDescription3 AS Brand, C.Name AS Category
                FROM Main.Item I
                JOIN Main.Category C ON C.ID = I.CategoryID AND C.isRetail = I.isRetail
                WHERE I.isRetail = 1
                -- Lista de IDs antigua
                -- AND C.ID IN (4, 7, 13, 15, 16, 18, 19, 20, 21, 22, 24, 25, 27, 29, 30, 40, 45, 74, 75, 97, 98, 107, 127, 130, 131, 135, 136, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 154, 155, 158, 190, 220, 240, 265, 266, 272, 275, 279, 280, 281, 418, 435, 490, 511, 517, 520, 528, 574, 627, 737, 738, 741, 745, 746, 747, 754, 757, 775, 776, 782, 787, 848, 966, 1010, 1012, 1013, 1014, 1019, 1020, 1021)
                AND C.ID IN (4, 5, 7, 13, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 27, 28, 29, 30, 34, 42, 44, 74, 75, 97, 98, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 151, 152, 153, 154, 155, 156, 160, 161, 179, 197, 386, 574, 708, 710, 718, 741, 746, 747, 751, 755, 772, 774, 775, 776, 782, 783, 784, 785, 787, 788, 834, 870, 993, 1015)
				AND I.ItemLookupCode = ?
            """
            cursor.execute(sql, barCode)

            item = cursor.fetchone()

            if item:
                item_dict = dict(zip([column[0] for column in cursor.description], item))
                return JsonResponse(item_dict, safe=False)
            else:
                return JsonResponse({
                    'error': 'Error: No se ha encontrado el producto.',
                    'warning': 'Error: No se ha encontrado el producto.'
                    }, status=404)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)            
        
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500) 
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'
            }, status=405)

@jwt_required
def getBranchByCustomerID(request):
    if request.method == 'GET':
        customer_id = request.GET.get('mainCustomerID')
        isRetail = request.GET.get('isRetail')

        if not all([customer_id, isRetail]):
            return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)

        connection = None
        cursor = None

        try:
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
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
            if branchesByID:
                branchesByIDList = [dict(zip([column[0] for column in cursor.description], row)) for row in branchesByID]
                return JsonResponse(branchesByIDList, safe=False)
            else:
                return JsonResponse({
                    'error': 'Error: No se han encontrado sucursales asociadas a esta compañía.',
                    'warning': 'Error: No se han encontrado sucursales asociadas a esta compañía.'
                }, status=404)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500) 

        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'
            }, status=405)

@jwt_required
def getCustomerByUserID(request):
    if request.method == 'GET':
        user_id = request.GET.get('userID')

        if not user_id:
            return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos. (userID)',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)
        
        connection = None
        cursor = None
        
        try:
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
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
                return JsonResponse({
                    'error': 'Error: Ha ocurrido un error con los campos requeridos. (customerID)',
                    'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                    }, status=400)

            sql = """
                SELECT C.ID, C.FirstName, C.LastName, C.Address, C.Zip, C.EmailAddress, C.PhoneNumber, C.NationalId
                FROM Warranty.Customer C
                WHERE C.ID = ?
            """
            cursor.execute(sql, customer_id)
            customer = cursor.fetchone()
            
            if customer:
                connection.commit()
                customer_dict = dict(zip([column[0] for column in cursor.description], customer))
                return JsonResponse(customer_dict, safe=False)
            else:
                return JsonResponse({
                    'error': 'Error: No se ha encontrado al cliente.',
                    'warning': 'Error: No se ha encontrado al cliente.'
                    }, status=404)  
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)  
        
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'
            }, status=405)

@jwt_required
def adminGetCustomerByID(request):
    if request.method == 'GET':
        customer_id = request.GET.get('customerID')

        if not customer_id:
            return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos. (customerID)',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)
        
        connection = None
        cursor = None
        try:
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()
            
            sql = """
                SELECT C.ID, C.FirstName, C.LastName, C.EmailAddress, C.PhoneNumber, C.Address, C.Zip, C.NationalId
                FROM Warranty.Customer C
                WHERE C.ID = ?
            """
            cursor.execute(sql, customer_id)
            customer = cursor.fetchone()

            if customer:
                customer_dict = dict(zip([column[0] for column in cursor.description], customer))
                return JsonResponse(customer_dict, safe=False)
            else:
                return JsonResponse({
                    'error': 'Error: No se encontró al cliente.',
                    'warning': 'Error: No se encontró al cliente.'
                    }, status=404)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)

        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
            }, status=500)

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'waring': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'
            }, status=405)

@jwt_required
def adminGetMainCustomers(request):
    if request.method == 'GET':
        connection = None
        cursor = None
        
        try:
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            sql = """
                SELECT DISTINCT C.ID, C.FirstName + '' + C.LastName AS FullName, C.isRetail
                FROM Main.Customer C
                JOIN Warranty.Inventory I ON C.ID = I.customerID
                WHERE C.FirstName + '' + C.LastName != ' '
                ORDER BY FullName
            """

            cursor.execute(sql)

            customers = cursor.fetchall()
            if customers:
                customer_list = [dict(zip([column[0] for column in cursor.description], row)) for row in customers]
                return JsonResponse(customer_list, safe=False)
            
            else:
                return JsonResponse({
                    'error': 'Error: No se han encontrado las compañías.',
                    'warning': 'Error: No se han encontrado las compañías.'
                    }, status=404)
            
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)

        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'
            }, status=405)
    
@jwt_required
def adminGetMainCustomersRetail(request):
    if request.method == 'GET':
        connection = None
        cursor = None
        
        try:
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
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
            if customers:
                customer_list = [dict(zip([column[0] for column in cursor.description], row)) for row in customers]
                return JsonResponse(customer_list, safe=False)
            else:
                return JsonResponse({
                    'error': 'Error: No se han encontrado las compañías.',
                    'warning': 'Error: No se han encontrado las compañías.'
                    }, status=404)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)        
        
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'
            }, status=405)
    
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
                return JsonResponse({
                    'error': 'JSON Inválido',
                    'warning': 'Error al enviar los datos al servidor.'
                    }, status=400)
            
            email_address = data.get('EmailAddress')
            password = data.get('Password')

            if not all([email_address, password]):
                return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)

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
                SELECT U.Password, R.Description, U.userID, C.FirstName, C.EmailAddress
                FROM Warranty.Users U
                JOIN Warranty.Role R ON U.roleID = R.RoleID
                JOIN Warranty.Customer C ON U.CustomerID = C.ID
                WHERE U.Users = ?;
            """
            cursor.execute(sql, (email_address,))
            user_data = cursor.fetchone()
            
            # Check if user exists and if the password is correct
            if not user_data:
                return JsonResponse({
                    'error': 'Nombre de usuario o contraseña inválidos.',
                    'warning': 'Nombre de usuario o contraseña inválidos.'
                }, status=401)

            stored_password = user_data[0]
            user_role = user_data[1]
            user_id = user_data[2]
            user_fname = user_data[3]
            user_email = user_data[4]

            # Verify the password
            if not password == stored_password:
                return JsonResponse({
                    'error': 'Nombre de usuario o contraseña inválidos.',
                    'warning': 'Nombre de usuario o contraseña inválidos.'}, status=401)

            if user_role != 'Administrador':
                return JsonResponse({
                    'error': 'Error: Acceso no autorizado',
                    'warning': 'Error: Acceso no autorizado'
                    }, status=403)
            
            jwt_secret = os.environ.get("JWT_SECRET_KEY")

            payload = {
                'user_id': user_id,
                'user_first_name': user_fname,
                'email_address': user_email,
                'role': user_role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            }

            access_token = jwt.encode(payload, jwt_secret, algorithm='HS256')
            if not jwt_secret:
                return JsonResponse({
                    'error': 'Server misconfiguration: missing JWT secret key',
                    'warning': 'Error al generar el token de sesión.'
                    }, status=404)
            
            return JsonResponse({
                'message': 'Inicio de sesión exitoso',
                'access_token': access_token
                }, status=200)
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, inténtelo más tarde. (DB Error)'
                }, status=500)
        
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, inténtelo más tarde. (Invalid Request)'
            }, status=405)

@csrf_exempt
@jwt_required
def adminCreateUsers(request):
    if request.method == 'POST':
        connection = None
        cursor = None

        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({
                    'error': 'JSON Inválido',
                    'warning': 'Error al enviar los datos al servidor.'
                    }, status=400)

            # Mandatory fields
            first_name = data.get('FirstName')
            last_name = data.get('LastName')
            national_id = data.get('NationalID')
            email_address = data.get('EmailAddress')
            phone_number = data.get('PhoneNumber')
            password = data.get('Password')
            role_id = data.get('roleID')
            
            if not all([first_name, last_name, email_address, password, role_id]):
                return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)
            
            # Optional fields
            address = data.get('Address')
            zip_code = data.get('Zip')

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
                return JsonResponse({
                    'error': 'Ya existe un usuario asociado a este correo electrónico',
                    'warning': 'Ya existe un usuario asociado a este correo electrónico'
                    }, status=400)

            cursor.execute("SELECT COUNT(*) FROM Warranty.Customer WHERE NationalId = ?", (national_id,))
            if cursor.fetchone()[0] > 0:
                return JsonResponse({
                    'error': 'Ya existe un usuario asociado a este documento de identificación.',
                    'warning': 'Ya existe un usuario asociado a este documento de identificación.'
                }, status=400)

            # Begin a transaction for atomic insertion
            connection.autocommit = False # Ensure we are in a transaction

            # Insert into the Customer table and get the new CustomerID
            customer_sql = """
                INSERT INTO Warranty.Customer (FirstName, LastName, Address, Zip, EmailAddress, PhoneNumber, NationalId)
                OUTPUT INSERTED.ID
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """
            cursor.execute(customer_sql, (first_name, last_name, address, zip_code, email_address, phone_number, national_id))
            
            customer_id = cursor.fetchval()

            # Insert into the Users table
            user_sql = """
                INSERT INTO Warranty.Users (Users, Password, registrationDate, CustomerID, roleID)
                VALUES (?, ?, GETDATE(), ?, ?);
            """
            cursor.execute(user_sql, (email_address, password, customer_id, role_id))

            data_for_email = {
                'user_name': email_address,
                'first_name': first_name,
                'last_name': last_name,
                'email_address': email_address,
                'address': address,
                'phone_number': phone_number
            }

            email = send_user_register_email(data_for_email)

            if email:
                # Commit the transaction if all operations were successful
                connection.commit()
                return JsonResponse({'message': 'Usuario registrado exitosamente.'}, status=201)
            else:
                return JsonResponse({
                    'error': 'Error: No se ha podido enviar el correo de registro de usuario.',
                    'warning': 'Ha ocurrido un error al enviar el correo de registro de usuario, por favor inténtelo más tarde.'
                    }, status=400)
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, inténtelo más tarde. (DB Error)'
                }, status=500)
            
        except Exception as e:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()         
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, inténtelo más tarde. (Invalid Request)'
            }, status=405)
            
@csrf_exempt
@jwt_required
def adminEditUsers(request):
    if request.method == 'PUT':
        connection = None
        cursor = None
        
        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({
                    'error': 'JSON Inválido',
                    'warning': 'Error al enviar los datos al servidor.'
                    }, status=400)
            
            # Mandatory fields check
            user_id = data.get('userID')
            first_name = data.get('FirstName')
            last_name = data.get('LastName')
            national_id = data.get('NationalID')
            email_address = data.get('EmailAddress')
            phone_number = data.get('PhoneNumber')
            role_id = data.get('roleID')
            
            if not all([user_id, first_name, last_name, email_address, role_id]):
                return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)
            
            # Optional fields
            address = data.get('Address')
            zip_code = data.get('Zip')
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
                return JsonResponse({
                    'error': 'Usuario no encontrado',
                    'warning': 'Error: Usuario no encontrado'}, status=404)
            
            if role_id not in [1, 2, 3]:
                return JsonResponse({
                    'error': 'Invalid role',
                    'warning': 'Error: Valor inválido para el rol'
                    }, status=400)
            
            customer_id = user_info[0]
            current_email = user_info[1]

            if email_address.lower() != current_email.lower():
                cursor.execute("SELECT COUNT(*) FROM Warranty.Users WHERE Users = ?", (email_address,))
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({
                        'error': 'Este correo electrónico ya se encuentra asociado a un usuario',
                        'warning': 'Este correo electrónico ya se encuentra asociado a un usuario.'
                        }, status=400)
            
            # Update the Customer table
            customer_sql = """
                UPDATE Warranty.Customer
                SET FirstName = ?, LastName = ?, Address = ?, Zip = ?, EmailAddress = ?, PhoneNumber = ?, NationalId = ?
                WHERE ID = ?
            """
            cursor.execute(customer_sql, (first_name, last_name, address, zip_code, email_address, phone_number, national_id, customer_id))

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
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)
        
        except Exception as e:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, inténtelo más tarde. (Invalid Request)'
            }, status=405)

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
                return JsonResponse({
                    'error': 'JSON Inválido',
                    'warning': 'Error al enviar los datos al servidor.'
                    }, status=400)
            
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
                return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)

            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            # Check if branch already exists
            #cursor.execute("SELECT COUNT(*) FROM Warranty.Branch WHERE Branch.RIF = ?", (RIF,))
            #if cursor.fetchone()[0] > 0:
            #    return JsonResponse({
            #        'error': 'Error: Esta sucursal ya existe.',
            #        'warning': 'Error: Esta sucursal ya existe.'
            #        }, status=400)

            sql = """
                INSERT INTO Warranty.Branch (customerID, isRetail, RIFtype, RIF, companyName, address, branchDescription)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql, (customerID, isRetail, RIFtype, RIF, companyName, address, branchDescription))
            connection.commit()

            return JsonResponse({'message': 'Sucusal creada correctamente.'}, status=201)
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)
        
        except Exception as e:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, inténtelo más tarde. (Invalid Request)'
            }, status=405)

@csrf_exempt
@jwt_required
def adminEditBranch(request):
    if request.method == 'PUT':
        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({
                    'error': 'JSON Inválido',
                    'warning': 'Error al enviar los datos al servidor.'
                    }, status=400)

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
                return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)

            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
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

            return JsonResponse({'message': 'Sucursal actualizada correctamente.'}, status=200)
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)

        except Exception as e:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, inténtelo más tarde. (Invalid Request)'
            }, status=405)

# Technical Service Views
#   1. Login
#   2. Get Warranty By ID
#   3. Technical Service History
#   4. Technical Service Get Status
#   5. Technical Service Get Issue
#   6. Technical Service Open Case
#   7. Technical Service Update Case
#   8. Technical Service Close Case
@csrf_exempt
def technicalServiceLogin(request):
    if request.method == 'POST':
        connection = None
        cursor = None

        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({
                    'error': 'JSON Inválido',
                    'warning': 'Error al enviar los datos al servidor.'
                    }, status=400)
            
            email_address = data.get('EmailAddress')
            password = data.get('Password')

            if not all([email_address, password]):
                return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)

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
                SELECT U.Password, R.Description, U.userID, C.FirstName, C.EmailAddress
                FROM Warranty.Users U
                JOIN Warranty.Role R ON U.roleID = R.RoleID
                JOIN Warranty.Customer C ON U.CustomerID = C.ID
                WHERE U.Users = ?;
            """
            cursor.execute(sql, (email_address,))
            user_data = cursor.fetchone()

            # Check if user exists and if the password is correct
            if not user_data:
                # Use a generic error message to prevent username enumeration
                return JsonResponse({
                    'error': 'Nombre de usuario o contraseña inválidos.',
                    'warning': 'Nombre de usuario o contraseña inválidos.'}, status=401)

            stored_password = user_data[0]
            user_role = user_data[1]
            user_id = user_data[2]
            user_fname = user_data[3]
            user_email = user_data[4]

            # Verify the password
            if not password == stored_password:
                return JsonResponse({
                    'error': 'Nombre de usuario o contraseña inválidos.',
                    'warning': 'Nombre de usuario o contraseña inválidos.'
                    }, status=401)

            # Check if the user has the correct role for this login path
            if user_role != 'Servicio Técnico' and user_role != 'Administrador':
                return JsonResponse({'error': 'Acceso no autorizado'}, status=403)
            
            # You would generate and return a session token or JWT here
            jwt_secret = os.environ.get("JWT_SECRET_KEY")
            if not jwt_secret:
                return JsonResponse({
                    'error': 'Server misconfiguration: missing JWT secret key',
                    'warning': 'Error al generar el token de sesión.'
                    }, status=404)

            payload = {
                'user_id': user_id,
                'user_first_name': user_fname,
                'email_address': user_email,
                'role': user_role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            }

            access_token = jwt.encode(payload, jwt_secret, algorithm='HS256')
            
            return JsonResponse({
                'message': 'Inicio de sesión exitoso',
                'access_token': access_token
                }, status=200)
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)
        
        except Exception as e:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, inténtelo más tarde. (Invalid Request)'
            }, status=405)

@jwt_required
def technicalServiceGetWarrantyByID(request):
    if request.method == 'GET':
        warranty_number = request.GET.get('WarrantyNumber')

        if not warranty_number:
            return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)

        connection = None
        cursor = None

        try:
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            # Se añadieron W.invoiceCopyPath y W.invoiceFileName al SELECT
            sql = """
                SELECT 
                    W.WarrantyNumber, W.purchaseDate, W.invoiceNumber, 
                    W.invoiceCopyPath, W.invoiceFileName, 
                    I.Description AS Brand, I.SubDescription3 AS Model, 
                    S.description, W.usedCount, 
                    COALESCE(TSS.statusDescription, 'N/A') AS TechnicalServiceStatus, 
                    C.FirstName + ' ' + C.LastName AS Customer, C.NationalId, C.PhoneNumber, C.EmailAddress, B.companyName
                FROM Warranty.warranty W
                JOIN Main.Item I ON W.ItemId = I.ID AND W.isRetail = I.isRetail
                JOIN Warranty.warrantyStatus S ON W.statusID = S.statusID
                LEFT JOIN Warranty.technicalService TS ON W.WarrantyNumber = TS.warrantyID
                LEFT JOIN Warranty.technicalServiceStatus TSS ON TS.statusID = TSS.statusID
                JOIN Warranty.Users U ON W.registerID = U.userID
                JOIN Warranty.Customer C ON U.CustomerID = C.ID
                LEFT JOIN Warranty.Branch B ON W.branchID = B.branchID
                WHERE W.WarrantyNumber = ?
            """
            cursor.execute(sql, (warranty_number, ))

            warranty = cursor.fetchone()

            if warranty:
                # Esta línea automáticamente incluirá invoiceCopyPath e invoiceFileName en el JSON
                warranty_dict = dict(zip([column[0] for column in cursor.description], warranty))
                return JsonResponse(warranty_dict, safe=False)
            else:
                return JsonResponse({
                    'error': 'Garantía no encontrada.',
                    'warning': 'Grantía no encontrada.'
                    }, status=404)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)   

        except Exception as e:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'
            }, status=405)

def technicalServiceHistory(request):
    if request.method == 'GET':
        connection = None
        cursor = None

        user_id = request.GET.get('userID')

        if not user_id:
            return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)

        try:
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};'
            )
            cursor = connection.cursor()

            sql = """
                SELECT TS.CaseNumber, TS.warrantyID, TS.receptionDate, TS.lastUpdated, TS.closedDate, 
                        C.FirstName + ' ' + C.LastName AS Customer, B.companyName, I.Description, TSS.statusDescription,
                        W.branchID, I.BinLocation, I.SubDescription3 AS Brand, C.NationalId, C.PhoneNumber, C.EmailAddress
                FROM Warranty.technicalService TS
                JOIN Warranty.warranty W ON TS.warrantyID = W.WarrantyNumber
				JOIN Warranty.Users U ON W.registerID = U.userID
                JOIN Warranty.Customer C ON U.CustomerID = C.ID
                LEFT JOIN Warranty.Branch B ON W.branchID = B.branchID
                JOIN Main.Item I ON W.ItemId = I.ID AND W.isRetail = I.isRetail
                JOIN Warranty.technicalServiceStatus TSS ON TS.statusID = TSS.statusID
				ORDER BY TS.warrantyID
            """
            cursor.execute(sql)
            ts_cases = cursor.fetchall()

            if ts_cases:
                ts_list = [dict(zip([column[0] for column in cursor.description], row)) for row in ts_cases]
                return JsonResponse(ts_list, safe=False)
            else:
                return JsonResponse({
                    'error': 'Error: No se encontraron resultados.',
                    'warning': 'Error: No se han encontrado resultados. (test1)'
                    }, status=404)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)

        except Exception as e:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, inténtelo más tarde. (Invalid Request)'
            }, status=405)

def technicalServiceGetStatus(request):
    if request.method == 'GET':
        connection = None
        cursor = None
        
        try:
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
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
                return JsonResponse({
                    'error': 'Error: No se encontraron resultados.',
                    'warning': 'Error: No se han encontrado resultados.'
                    }, status=404)
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)
        
        except Exception as e:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'
            }, status=405)

def technicalServiceGetIssue(request):
    if request.method == 'GET':
        connection = None
        cursor = None
        
        try:
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
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
                return JsonResponse({
                    'error': 'Error: No se encontraron resultados.',
                    'warning': 'Error: No se encontrado resultados.'
                    }, status=404)
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)
        
        except Exception as e:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'
            }, status=405)

@csrf_exempt
@jwt_required
def technicalServiceCreateIssue(request):
    if request.method == 'POST':
        connection = None
        cursor = None

        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({
                    'error': 'JSON Inválido',
                    'warning': 'Error al enviar los datos al servidor.'
                    }, status=400)
            
            issue_description = data.get('IssueDescription')

            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            sql = """
                INSERT INTO Warranty.Issue (IssueDescription)
                OUTPUT INSERTED.IssueId
                VALUES (?);
            """
            cursor.execute(sql, (issue_description,))
            issue_id = cursor.fetchval()

            if issue_id:
                connection.commit()
                return JsonResponse({
                    'message': 'Se ha creado la falla correctamente.'
                    }, status=200)
            else:
                return JsonResponse({
                    'error': 'Error: No se ha podido crear la falla',
                    'warning': 'Error: Ha ocurrido un error al crear la falla.'
                    }, status=400)
            
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)

        except Exception as e:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'
            }, status=405)

@csrf_exempt
@jwt_required
def technicalServiceEditIssue(request):
    if request.method == 'PUT':
        connection = None
        cursor = None

        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({
                    'error': 'JSON Inválido',
                    'warning': 'Error al enviar los datos al servidor.'
                    }, status=400)
            
            issue_id = data.get('IssueId')
            issue_description = data.get('IssueDescription')

            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            sql = """
                UPDATE Warranty.Issue
                SET IssueDescription = ?
                WHERE IssueId = ?
            """
            cursor.execute(sql, (issue_description, issue_id))

            connection.commit()
            return JsonResponse({
                'message': 'Se ha editado la falla correctamente'
                }, status=200)
            
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)

        except Exception as e:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'
            }, status=405)

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
                return JsonResponse({
                    'error': 'JSON Inválido',
                    'warning': 'Error al enviar los datos al servidor.'
                    }, status=400)

            # Mandatory fields
            register_id = data.get('registerID')
            warranty_id = data.get('WarrantyID')

            if not all([register_id, warranty_id]):
                return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)

            # Optional fields
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
                INSERT INTO Warranty.technicalService (registerID, warrantyID, issueID, issueResolutionDetails, statusID, receptionDate, lastUpdated, closedDate)
                OUTPUT INSERTED.CaseNumber, INSERTED.receptionDate
                VALUES (?, ?, NULL, NULL, ?, GETDATE(), NULL, NULL)
            """
            cursor.execute(sql, (register_id, warranty_id, status_id))
            case_number, reception_date = cursor.fetchone()

            sql_warranty = """
                UPDATE Warranty.warranty
                SET usedCount = usedCount + 1
                WHERE WarrantyNumber = ?
            """
            cursor.execute(sql_warranty, (warranty_id))

            data_for_email = {
                'user_name': data.get('Customer'),
                'email_address': {
                    'technical_service': data.get('TechnicalServiceEmail'),
                    'customer': data.get('CustomerEmail')
                },
                'case_number': case_number,
                'warranty_code': warranty_id,
                'store_name': data.get('StoreName'),
                'product_name': data.get('ProductName'),
                'reception_date': reception_date,
                'case_status': 'Abierto'
            }

            email = send_warranty_open_case_email(data_for_email)

            if email:
                connection.commit()
                return JsonResponse({'message': 'Se ha abierto el caso exitosamente'}, status=200)
            else:
                return JsonResponse({
                    'error': 'Error: No se ha podido enviar el correo de apertura de caso.',
                    'warning': 'Ha ocurrido un error al enviar el correo de apertura de caso, por favor inténtelo más tarde.'
                    }, status=400)
            
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)
        
        except Exception as e:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'
            }, status=405)

@csrf_exempt
@jwt_required
def technicalServiceUpdateCase(request):
    if request.method == 'POST':
        connection = None
        cursor = None
        
        try:            
            # Mandatory fields check
            case_number = request.POST['CaseNumber']
            issue_id = request.POST['issueID']
            issue_resolution_details = request.POST['issueResolutionDetails']
            status_id = request.POST['statusID']
            diagnostic_img = request.FILES['diagnosticIMG']

            if not all([case_number, issue_id, issue_resolution_details, status_id, diagnostic_img]):
                return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)

            headers = get_onedrive_headers()
            ext = diagnostic_img.name.split('.')[-1]
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = diagnostic_img.name.replace(" ", "_").replace("/", "_")
            unique_name = f"{timestamp}_{safe_name}"
            folder_path = "/GARANTIAS/Casos"
            upload_url = f"https://graph.microsoft.com/v1.0/users/desarrollo@grupogipsy.com/drive/root:/{folder_path}/{unique_name}:/content"
        
            resp = requests.put(upload_url, headers=headers, data=diagnostic_img.read())
            if resp.status_code not in (200, 201):
                return JsonResponse({
                    'error': 'Error al subir la imagen a OneDrive',
                    'warning': 'Ha ocurrido un error al subir su imagen, inténtelo más tarde.',
                    'details': resp.text
                    }, status=500)

            data = resp.json()
            diagnostic_copy_path = data["webUrl"]

            file_id = data['id']

            create_link_url = f"https://graph.microsoft.com/v1.0/users/desarrollo@grupogipsy.com/drive/items/{file_id}/createLink"

            body = {
                'type': 'view',
                'scope': 'anonymous'
            }

            response = requests.post(create_link_url, headers=headers, json=body)
            public_diagnostic_url = response.json()['link']['webUrl']

            # Establish database connection
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};'
            )
            cursor = connection.cursor()

            sql = """
                UPDATE Warranty.technicalService
                SET issueID = ?, issueResolutionDetails = ?, statusID = ?, lastUpdated = GETDATE(), diagnosticCopyPath = ?
                WHERE CaseNumber = ?
            """
            cursor.execute(sql, (int(issue_id), str(issue_resolution_details), int(status_id), public_diagnostic_url, int(case_number)))
            
            if cursor.rowcount == 0:
                return JsonResponse({
                    'error': 'No se encontró el caso para actualizar',
                    'warning': 'Error: No se encontró el caso solicitado.'
                }, status=404)

            data_for_email = {
                'user_name': request.POST['Customer'],
                'email_address': {
                    'technical_service': request.POST['TechnicalServiceEmail'],
                    'customer': request.POST['CustomerEmail']
                },
                'case_number': case_number,
                'warranty_code': request.POST['WarrantyID'],
                'store_name': request.POST['StoreName'],
                'product_name': request.POST['ProductName'],
                'reception_date': request.POST['ReceptionDate'],
                'case_status': request.POST['statusDescription'],
                'issue_description': request.POST['issueDescription'],
                'issue_resolution_details': issue_resolution_details
            }

            email = send_warranty_update_case_email(data_for_email)

            if email:
                connection.commit()
                return JsonResponse({'message': 'El caso se ha actualizado correctamente'}, status=200)
            else:
                return JsonResponse({
                    'error': 'Error: No se ha podido enviar el correo de actualización del caso.',
                    'warning': 'Ha ocurrido un error al enviar el correo de actualización del caso, por favor inténtelo más tarde.'
                    }, status=400)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)
        
        except Exception as e:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'
            }, status=405)

@csrf_exempt
@jwt_required
def technicalServiceCloseCase(request):
    if request.method == 'POST':
        connection = None
        cursor = None
        
        try:            
            # Mandatory fields check
            case_number = request.POST['CaseNumber']
            issue_id = request.POST['issueID']
            issue_resolution_details = request.POST['issueResolutionDetails']
            status_id = 3
            diagnostic_img = request.FILES['diagnosticIMG']
            required_change = request.POST['requiredChange']
        
            if not all([case_number, issue_id, issue_resolution_details, diagnostic_img, required_change]):
                return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)

            headers = get_onedrive_headers()
            ext = diagnostic_img.name.split('.')[-1]
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = diagnostic_img.name.replace(" ", "_").replace("/", "_")
            unique_name = f"{timestamp}_{safe_name}"
            folder_path = "/GARANTIAS/Casos"
            upload_url = f"https://graph.microsoft.com/v1.0/users/desarrollo@grupogipsy.com/drive/root:/{folder_path}/{unique_name}:/content"
        
            resp = requests.put(upload_url, headers=headers, data=diagnostic_img.read())
            if resp.status_code not in (200, 201):
                return JsonResponse({
                    'error': 'Error al subir la imagen a OneDrive',
                    'warning': 'Ha ocurrido un error al subir su imagen, inténtelo más tarde.',
                    'details': resp.text
                    }, status=500)

            data = resp.json()
            diagnostic_copy_path = data["webUrl"]

            file_id = data['id']

            create_link_url = f"https://graph.microsoft.com/v1.0/users/desarrollo@grupogipsy.com/drive/items/{file_id}/createLink"

            body = {
                'type': 'view',
                'scope': 'anonymous'
            }

            response = requests.post(create_link_url, headers=headers, json=body)
            public_diagnostic_url = response.json()['link']['webUrl']


            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};'
            )
            cursor = connection.cursor()

            sql = """
                UPDATE Warranty.technicalService
                SET issueID = ?, issueResolutionDetails = ?, statusID = ?, lastUpdated = GETDATE(), closedDate = GETDATE(), requiredChange = ?, diagnosticCopyPath = ?
                WHERE CaseNumber = ?
            """
            cursor.execute(sql, (int(issue_id), str(issue_resolution_details), status_id, required_change, public_diagnostic_url, case_number))
            
            if cursor.rowcount == 0:
                return JsonResponse({
                    'error': 'No se encontró el caso para cerrar.',
                    'warning': 'Error: No se encontró el caso para cerrar.'
                }, status=404)

            data_for_email = {
                'user_name': request.POST['Customer'],
                'email_address': {
                    'technical_service': request.POST['TechnicalServiceEmail'],
                    'customer': request.POST['CustomerEmail']
                },
                'case_number': case_number,
                'warranty_code': request.POST['WarrantyID'],
                'store_name': request.POST['StoreName'],
                'product_name': request.POST['ProductName'],
                'reception_date': request.POST['ReceptionDate'],
                'case_status': request.POST['statusDescription'],
                'issue_description': request.POST['issueDescription'],
                'issue_resolution_details': issue_resolution_details,
                'required_change': required_change
            }

            email = send_warranty_close_case_email(data_for_email)

            if email:
                connection.commit()
                return JsonResponse({'message': 'El caso se ha cerrado correctamente.'}, status=200)
            else:
                return JsonResponse({
                    'error': 'Error: No se ha podido enviar el correo de cierre del caso.',
                    'warning': 'Ha ocurrido un error al enviar el correo de cierre del caso, por favor inténtelo más tarde.'
                    }, status=400)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)
        
        except Exception as e:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, inténtelo más tarde. (Invalid Request)'
            }, status=405)

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
                return JsonResponse({
                    'error': 'JSON Inválido',
                    'warning': 'Error al enviar los datos al servidor.'
                    }, status=400)
            
            email_address = data.get('EmailAddress')
            password = data.get('Password')

            if not all([email_address, password]):
                return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)

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
                SELECT U.Password, R.Description, U.userID, C.FirstName, C.EmailAddress
                FROM Warranty.Users U
                JOIN Warranty.Role R ON U.roleID = R.RoleID
                JOIN Warranty.Customer C ON U.CustomerID = C.ID
                WHERE U.Users = ?;
            """
            cursor.execute(sql, (email_address,))
            user_data = cursor.fetchone()

            # Check if user exists and if the password is correct
            if not user_data:
                return JsonResponse({
                    'error': 'Nombre de usuario o contraseña inválidos.',
                    'warning': 'Nombre de usuario o contraseña inválidos.'}, status=401)

            stored_password = user_data[0]
            user_role = user_data[1]
            user_id = user_data[2]
            user_fname = user_data[3]
            user_email = user_data[4]

            # Verify the password
            if not password == stored_password:
                return JsonResponse({
                    'error': 'Nombre de usuario o contraseña inválidos.',
                    'warning': 'Nombre de usuario o contraseña inválidos.'}, status=401)

            # Check if the user has the correct role for this login path
            if user_role != 'Cliente' and user_role != 'Administrador':
                return JsonResponse({'error': 'Acceso no autorizado'}, status=403)
            
            # You would generate and return a session token or JWT here
            jwt_secret = os.environ.get("JWT_SECRET_KEY")
            if not jwt_secret:
                return JsonResponse({
                    'error': 'Server misconfiguration: missing JWT secret key',
                    'warning': 'Error al generar el token de sesión'
                    }, status=404)
            
            payload = {
                'user_id': user_id,
                'user_first_name': user_fname,
                'email_address': user_email,
                'role': user_role,
                'exp': datetime.datetime.now() + datetime.timedelta(hours=2)
            }

            access_token = jwt.encode(payload, jwt_secret, algorithm='HS256')
            
            return JsonResponse({
                'message': 'Inicio de sesión exitoso',
                'access_token': access_token
                }, status=200)
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)
        
        except Exception as e:
            if connection:
                connection.rollback()

            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, inténtelo más tarde. (Invalid Request)'
            }, status=405)

@csrf_exempt
def publicRegister(request):
    if request.method == 'POST':
        connection = None
        cursor = None
        
        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({
                    'error': 'JSON Inválido',
                    'warning': 'Error al enviar los datos al servidor.'
                    }, status=400)
            
            # Mandatory fields
            first_name = data.get('FirstName')
            last_name = data.get('LastName')
            national_id = data.get('NationalID')
            email_address = data.get('EmailAddress')
            phone_number = data.get('PhoneNumber')
            password = data.get('Password')
            role_id = 3  # Assuming '3' is the roleID for 'Cliente'
            
            if not all([first_name, last_name, national_id, email_address, password]):
                return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)
            
            # Optional fields
            address = data.get('Address')
            zip_code = data.get('Zip')

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
                return JsonResponse({
                    'error': 'Ya existe un usuario asociado a este correo electrónico.',
                    'warning': 'Ya existe un usuario asociado a este correo electrónico.'
                    }, status=400)

            cursor.execute("SELECT COUNT(*) FROM Warranty.Customer WHERE NationalId = ?", (national_id,))
            if cursor.fetchone()[0] > 0:
                return JsonResponse({
                    'error': 'Ya existe un usuario asociado a este documento de identificación.',
                    'warning': 'Ya existe un usuario asociado a este documento de identificación.'
                }, status=400)

            # Begin a transaction for atomic insertion
            connection.autocommit = False # Ensure we are in a transaction

            # Insert into the Customer table and get the new CustomerID
            customer_sql = """
                INSERT INTO Warranty.Customer (FirstName, LastName, Address, Zip, EmailAddress, PhoneNumber, NationalId)
                OUTPUT INSERTED.ID
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """
            cursor.execute(customer_sql, (first_name, last_name, address, zip_code, email_address, phone_number, national_id))
            
            customer_id = cursor.fetchval()

            # Insert into the Users table
            user_sql = """
                INSERT INTO Warranty.Users (Users, Password, registrationDate, CustomerID, roleID)
                VALUES (?, ?, GETDATE(), ?, ?);
            """
            cursor.execute(user_sql, (email_address, password, customer_id, role_id))

            data_for_email = {
                'user_name': email_address,
                'first_name': first_name,
                'last_name': last_name,
                'email_address': email_address,
                'address': address,
                'phone_number': phone_number
            }

            email = send_user_register_email(data_for_email)

            if email:
                # Commit the transaction if all operations were successful
                connection.commit()
                return JsonResponse({'message': 'Usuario registrado exitosamente.'}, status=201)
            else:
                return JsonResponse({
                    'error': 'Error: No se ha podido enviar el correo de registro de usuario',
                    'warning': 'Ha ocurrido un error al enviar el correo de registro de usuario, por favor inténtelo más tarde.'
                    }, status=400)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)
            
        except Exception as e:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()     
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, inténtelo más tarde. (Invalid Request)'
            }, status=405)

@csrf_exempt
@jwt_required
def getMainCustomersWarrantyRegister(request):
    if request.method == 'GET':
        item_id = request.GET.get('itemID')

        if not item_id:
            return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
            }, status=400)

        connection = None
        cursor = None

        try:
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};')
            cursor = connection.cursor()

            sql = """
                SELECT I.customerID AS ID, C.FirstName + '' + C.LastName AS FullName, C.isRetail, I.itemID
                FROM Main.Customer C
                JOIN Warranty.Inventory I ON C.ID = I.customerID AND C.isRetail = I.isRetail
                WHERE C.FirstName + '' + C.LastName != ' '
                AND itemID = ?
                ORDER BY FullName
            """

            cursor.execute(sql, (item_id,))

            stores = cursor.fetchall()
            if stores:
                storesList = [dict(zip([column[0] for column in cursor.description], row)) for row in stores]
                return JsonResponse(storesList, safe=False)

            else:
                return JsonResponse({
                    'error': 'Error: Clientes no encontrados',
                    'warning': 'Error: Clientes no encontrados'
                    }, status=404)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)

        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, inténtelo más tarde. (Invalid Request)'
            }, status=405)

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

            if branch_id == '': branch_id = None

            item_id = request.POST['ItemId']
            is_retail = request.POST['isRetail']
            purchase_date = request.POST['purchaseDate']
            status_id = 1
            product_brand = request.POST['productBrand']
            product_barcode = request.POST['productBarcode']
            invoice_img = request.FILES['invoiceIMG']
            used_count = 0
            invoice_number = request.POST['invoiceNumber']
            main_customer = request.POST['mainCustomerID']

            if not all([
                register_id,
                item_id,
                is_retail,
                purchase_date,
                status_id,
                product_brand,
                product_barcode,
                invoice_img,
                invoice_number,
                main_customer
            ]):
                return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)

            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};'
            )
            cursor = connection.cursor()

            inventory_sql = """
                SELECT quantity
                FROM Warranty.Inventory
                WHERE customerID = ? AND itemID = ? AND isRetail = ?
            """
            cursor.execute(inventory_sql, (main_customer, item_id, is_retail))

            inventory_quantity = cursor.fetchval()

            if inventory_quantity == None or inventory_quantity < 1:
                return JsonResponse({
                    'error': 'Error: No hay garantías disponibles en el inventario para este producto.',
                    'warning': 'No existen garantías disponibles en el inventario para este producto.',
                    }, status=400)
            else:
                # Almacenamiento de facturas en OneDrive
                headers = get_onedrive_headers()
                ext = invoice_img.name.split('.')[-1]
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_name = invoice_img.name.replace(" ", "_").replace("/", "_")
                
                # Este es el nombre exacto que se guarda en OneDrive y ahora en BD
                unique_name = f"{timestamp}_{safe_name}" 
                
                folder_path = "/GARANTIAS/Facturas"
                upload_url = f"https://graph.microsoft.com/v1.0/users/desarrollo@grupogipsy.com/drive/root:/{folder_path}/{unique_name}:/content"
                
                resp = requests.put(upload_url, headers=headers, data=invoice_img.read())
                if resp.status_code not in (200, 201):
                    return JsonResponse({
                        'error': 'Error al subir la factura a OneDrive',
                        'warning': 'Ha ocurrido un error al subir su factura, inténtelo más tarde.',
                        'details': resp.text
                        }, status=500)

                data = resp.json()
                invoice_copy_path = data["webUrl"]

                # Generación de enlace público para la factura
                file_id = data['id']

                create_link_url = f"https://graph.microsoft.com/v1.0/users/desarrollo@grupogipsy.com/drive/items/{file_id}/createLink"

                body = {
                    'type': 'view',
                    'scope': 'anonymous'
                }

                response = requests.post(create_link_url, headers=headers, json=body)
                public_invoice_url = response.json()['link']['webUrl']

                # Check if the warranty already exists by invoiceNumber
                cursor.execute("SELECT COUNT(*) FROM Warranty.warranty WHERE invoiceNumber = ? AND ItemId = ?", (invoice_number, item_id))
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({
                        'error': 'Ya existe una garantía para este producto asociada a esta factura.',
                        'warning': 'Ya existe una garantía para este producto asociada a esta factura.'
                        }, status=400)

                # --- QUERY ACTUALIZADO ---
                # Se añadió invoiceFileName al INSERT y su respectivo parámetro '?' en VALUES
                sql = """
                    INSERT INTO Warranty.warranty (registerID, branchID, ItemId, isRetail, purchaseDate, registrationDate, statusID, productBrand, productBarcode, invoiceCopyPath, usedCount, invoiceNumber, CustomerID, invoiceFileName)
                    OUTPUT INSERTED.WarrantyNumber
                    VALUES (?, ?, ?, ?, ?, GETDATE(), ?, ?, ?, ?, ?, ?, ?, ?)
                """
                # Se añadió unique_name en el execute en el mismo orden que en el query
                cursor.execute(sql, (register_id, branch_id, item_id, is_retail, purchase_date, status_id, product_brand, product_barcode, public_invoice_url, used_count, invoice_number, main_customer, unique_name))
                warranty_number = cursor.fetchval()

                # Reduce the quantity of available warranties in the inventory
                update_inventory_sql = """
                    UPDATE Warranty.Inventory
                    SET quantity = quantity - 1
                    WHERE customerID = ? AND itemID = ? AND isRetail = ?
                """
                cursor.execute(update_inventory_sql, (main_customer, item_id, is_retail))
                
                # Extra fields needed for the email
                user_name = request.POST['userFirstName']
                email_address = request.POST['emailAddress']
                store_name = request.POST['storeName']
                branch_name = request.POST['branchName']
                store_rif = f"{request.POST['RIFtype']} - {request.POST['RIF']}"
                product_model = request.POST['productModel']

                data_for_email = {
                    'user_name': user_name,
                    'email_address': email_address,
                    'warranty_id': warranty_number,
                    'store_name': store_name,
                    'branch_name': branch_name,
                    'store_rif': store_rif,
                    'purchase_date': purchase_date,
                    'invoice_number': invoice_number,
                    'product_brand': product_brand,
                    'product_model': product_model,
                    'product_barcode': product_barcode,
                    'invoice_img_path': public_invoice_url
                }

                email = send_warranty_register_email(data_for_email)

                if email:
                    connection.commit()
                    return JsonResponse({'message': 'Garantía registrada de forma exitosa.'}, status=201)
                else:
                    return JsonResponse({
                        'error': 'Error: No se ha podido enviar el correo de registro de garrantía.',
                        'warning': 'Ha ocurrido un error al enviar el correo de registro de garantía, por favor inténtelo más tarde.'
                        }, status=400)
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)

        except Exception as e:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, inténtelo más tarde. (Invalid Request)'
            }, status=405)

@csrf_exempt
@jwt_required
def warrantyHistory(request):
    if request.method == 'GET':
        connection = None
        cursor = None

        user_id = request.GET.get('userID')
        if not user_id:
            return JsonResponse({
                'error': 'Error: Parámetro user_id inválido.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)
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
                SELECT W.WarrantyNumber, W.purchaseDate, W.registrationDate, W.usedCount, B.companyName, I.Description AS ProductName, S.description AS WarrantyStatus, I.SubDescription3 AS itemBrand
                FROM Warranty.warranty W
                LEFT JOIN Warranty.Branch B ON W.branchID = B.branchID
                JOIN Main.Item I ON W.ItemId = I.ID AND I.isRetail = W.isRetail
                JOIN Warranty.warrantyStatus S ON W.statusID = S.statusID
				WHERE W.registerID = ?
            """
            cursor.execute(sql, (user_id,))
            warranties = cursor.fetchall()

            if warranties:
                warranties_list = [dict(zip([column[0] for column in cursor.description], row)) for row in warranties]
                return JsonResponse(warranties_list, safe=False)
            else:
                return JsonResponse({
                    'error': 'Error: No se encontraron garantías registradas.',
                    'warning': 'Error: No se encontraron garantías registradas.'
                }, status=404)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)

        except Exception as e:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'
            }, status=405)
    
@csrf_exempt
@jwt_required
def userProfileEdit(request):
    if request.method == 'PUT':
        connection = None
        cursor = None
        
        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({
                    'error': 'JSON Inválido',
                    'warning': 'Error al enviar los datos al servidor.'
                    }, status=400)
            
            # Mandatory fields check
            user_id = data.get('userID')
            first_name = data.get('FirstName')
            last_name = data.get('LastName')
            national_id = data.get('NationalID')
            email_address = data.get('EmailAddress')
            phone_number = data.get('PhoneNumber')
            
            if not all([user_id, first_name, last_name, national_id, email_address, phone_number]):
                return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)
            
            # Optional fields
            address = data.get('Address')
            zip_code = data.get('Zip')

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
                return JsonResponse({
                    'error': 'Usuario no encontrado.',
                    'warning': 'Usuario no encontrado.'}, status=404)
            
            customer_id = user_info[0]
            current_email = user_info[1]

            if email_address.lower() != current_email.lower():
                cursor.execute("SELECT COUNT(*) FROM Warranty.Users WHERE Users = ?", (email_address,))
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({
                    'error': 'Ya existe un usuario asociado a este correo electrónico.',
                    'warning': 'Ya existe un usuario asociado a este correo electrónico.'}
                    , status=400)
            
            # Update the Customer table
            customer_sql = """
                UPDATE Warranty.Customer
                SET FirstName = ?, LastName = ?, Address = ?, Zip = ?, EmailAddress = ?, PhoneNumber = ?, NationalId = ?
                WHERE ID = ?
            """
            cursor.execute(customer_sql, (first_name, last_name, address, zip_code, email_address, phone_number, national_id, customer_id))

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
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)
        
        except Exception as e:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, inténtelo más tarde. (Invalid Request)'
            }, status=405)

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
                return JsonResponse({
                    'error': 'JSON Inválido',
                    'warning': 'Error al enviar los datos al servidor.'
                    }, status=400)

            # Mandatory fields check
            user_id = data.get('userID')
            current_password = data.get('old_password')
            new_password = data.get('new_password')

            if not all([user_id, current_password, new_password]):
                return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)

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
                return JsonResponse({
                    'error': 'Error: Contraseña actual incorrecta.',
                    'warning': 'Contraseña actual incorrecta, inténtelo nuevamente.'}, status=400)

            sql = """
                UPDATE Warranty.Users
                SET Password = ?
                WHERE userID = ?
            """
            cursor.execute(sql, (new_password, user_id))
            connection.commit()

            return JsonResponse({'message': 'Contraseña actualizada con éxito'}, status=200)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)

        except Exception as e:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
                
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (Invalid Request)'
            }, status=405)

@csrf_exempt
def forgottenPassword(request):
    if request.method == 'POST':
        connection = None
        cursor = None

        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({
                    'error': 'JSON Inválido',
                    'warning': 'Error al enviar los datos al servidor.'
                    }, status=400)
            
            email_address = data.get('email')

            if not email_address:
                return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un erro con los campos requeridos.'
                }, status=400)

            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};'
            )
            cursor = connection.cursor()

            sql = """
                SELECT COUNT(*)
                FROM Warranty.Users
                WHERE Users = ?
            """
            cursor.execute(sql, (email_address,))
            if cursor.fetchone()[0] <= 0:
                return JsonResponse({
                'error': 'No existe un usuario asociado a este correo electrónico.',
                'warning': 'No existe un usuario asociado a este correo electrónico.'
                }, status=404)

            sql_name = """
                SELECT U.userID, C.FirstName, R.Description
                FROM Warranty.Users U
                JOIN Warranty.Customer C ON C.ID = U.CustomerID
                JOIN Warranty.Role R ON U.roleID = R.RoleID
                WHERE U.Users = ?
            """
            cursor.execute(sql_name, (email_address,))
            user_id, first_name, user_role = cursor.fetchone()

            if not first_name:
                return JsonResponse({
                    'error': 'Error al obtener el nombre del usuario.',
                    'warning': 'Error al obtener el nombre del usuario.'
                }, status=400)

            
            temp_password = generate_temp_password()
            if not temp_password:
                return JsonResponse({
                'error': 'Error: No se ha podido generar el código de verificación.',
                'warning': 'Error: No se ha podido generar el código de verificación.'
                }, status=400)

            jwt_secret = os.environ.get("JWT_SECRET_KEY")
            if not jwt_secret:
                return JsonResponse({
                    'error': 'Server misconfiguration: missing JWT secret key',
                    'warning': 'Error al generar el token de sesión.'
                }, status=404)

            payload = {
                'user_id': user_id,
                'user_first_name': first_name,
                'email_address': email_address,
                'temp_password': temp_password,
                'role': user_role,
                'exp': datetime.datetime.now() + datetime.timedelta(minutes=30)
            }

            temp_token = jwt.encode(payload, jwt_secret, algorithm='HS256')
            
            data_for_email = {
                'user_name': first_name,
                'email_address': email_address,
                'temp_password': temp_password
            }

            email = send_temp_password_email(data_for_email)

            if email:
                return JsonResponse({
                    'message': 'Correo enviado de forma exitosa',
                    'temp_token': temp_token
                }, status=200)
            else:
                return JsonResponse({
                    'error': 'Error: No se ha podido enviar el correo con el código de recuperación.',
                    'warning': 'Ha ocurrido un error al enviar el correo con el código de recuperación, por favor inténtelo más tarde.'
                    }, status=400)

        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, inténtelo más tarde. (Invalid Request)'
            }, status=405)

@csrf_exempt
def resetPassword(request):
    if request.method == 'POST':
        connection = None
        cursor = None

        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({
                    'error': 'JSON Inválido',
                    'warning': 'Error al enviar los datos al servidor.'
                    }, status=400)
            
            user_id = data.get('user_id')
            new_password = data.get('new_password')

            if not all([user_id, new_password]):
                return JsonResponse({
                'error': 'Error: Ha ocurrido un error con los campos requeridos.',
                'warning': 'Error: Ha ocurrido un error con los campos requeridos.'
                }, status=400)

            # Establish database connection
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ["DB_SERVER"]};'
                f'Database={os.environ["DB_NAME"]};'
                f'UID={os.environ["DB_USER"]};'
                f'PWD={os.environ["DB_PASSWORD"]};'
            )
            cursor = connection.cursor()

            sql = """
                UPDATE Warranty.Users
                SET Password = ?
                WHERE userID = ?
            """
            cursor.execute(sql, (new_password, user_id))
            connection.commit()
            return JsonResponse({'message': 'Contraseña actualizada con éxito'}, status=200)
        
        except pyodbc.Error as db_error:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': f'A database error ocurred: {db_error}',
                'warning': 'Ha ocurrido un error, por favor inténtelo más tarde. (DB Error)'
                }, status=500)
        
        except Exception as e:
            if connection:
                connection.rollback()
            
            return JsonResponse({
                'error': str(e),
                'warning': f'Ha ocurrido un error: {str(e)}'
                }, status=500)
     
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return JsonResponse({
            'error': 'Invalid request method',
            'warning': 'Ha ocurrido un error, inténtelo más tarde. (Invalid Request)'
            }, status=405)