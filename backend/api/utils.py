import os
import jwt
from functools import wraps
from django.http import JsonResponse

def jwt_required(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authorization header missing or invalid'}, status=401)

        token = auth_header.split(' ')[1]
        jwt_secret = os.environ.get("JWT_SECRET_KEY")

        try:
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            request.user_id = payload['user_id']
            # Assuming you have a role in the token, as per your login view
            if 'role' in payload:
                request.user_role = payload['role'] 
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        except KeyError as e:
            # Handle cases where a key like 'user_id' is missing from the payload
            return JsonResponse({'error': f'Invalid token payload: missing {e}'}, status=401)

        return f(request, *args, **kwargs) # <--- This line is critical!

    return decorated_function # <--- This line is also critical!

def get_onedriveProofsOfPayments(paymentEntries):
    headers = get_onedrive_headers()
    folder_path = "/Recibos de Cobranza/Comprobantes de Pago"
    updated_entries = []
    
    for entry in paymentEntries:
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

def save_proofOfPayment(proof_of_payments, receipt_id, payment_date, index):
    saved_file_paths = []
    formatted_date = payment_date.strftime('%Y-%m-%d')
    headers = get_onedrive_headers()

    folder_path = "/Recibos de Cobranza/Comprobantes de Pago"
    for file in proof_of_payments:
        if file:
            new_filename = f"{receipt_id}_{formatted_date}_{index}{os.path.splitext(file.filename)[1]}"
            upload_url = f"https://graph.microsoft.com/v1.0/users/desarrollo@grupogipsy.com/drive/root:/{folder_path}/{new_filename}:/content"

            file_content = file.read()

            response = requests.put(
                url = upload_url,
                headers=headers,
                data=file_content)
            
            if response.status_code == 201:
                print(f"Archivo {new_filename} subido correctamente.")
                saved_file_paths.append(new_filename)
            else:
                print(f"Error al subir el archivo {new_filename}: {response.status_code}")
                print(response.json())

    return saved_file_paths