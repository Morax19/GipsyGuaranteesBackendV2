import os
import pyodbc
import requests
import time
from urllib.parse import quote
from django.core.management.base import BaseCommand, CommandError

# IMPORTANTE: Ajusta esta ruta para importar tu función real según la estructura de tu proyecto
from api.onedrive import get_onedrive_headers 

class Command(BaseCommand):
    help = 'Busca y repara los enlaces rotos de facturas de OneDrive en la tabla Warranty.warranty'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando reparación masiva de enlaces de OneDrive...")
        
        connection = None
        cursor = None

        try:
            # Puedes usar pyodbc directamente como lo venías haciendo, 
            connection = pyodbc.connect(
                f'Driver={{ODBC Driver 18 for SQL Server}};'
                f'Server={os.environ.get("DB_SERVER")};'
                f'Database={os.environ.get("DB_NAME")};'
                f'UID={os.environ.get("DB_USER")};'
                f'PWD={os.environ.get("DB_PASSWORD")};'
            )
            cursor = connection.cursor()

            # 1. Buscar todos los registros que necesitan reparación
            search_sql = """
                SELECT WarrantyNumber, invoiceFileName 
                FROM Warranty.warranty 
                WHERE (invoiceCopyPath IN ('', '*') OR invoiceCopyPath IS NULL)
                  AND invoiceFileName IS NOT NULL
            """
            cursor.execute(search_sql)
            broken_records = cursor.fetchall()
            
            if not broken_records:
                self.stdout.write(self.style.SUCCESS("No se encontraron enlaces rotos para reparar. ¡Todo está en orden!"))
                return

            self.stdout.write(self.style.WARNING(f"Se encontraron {len(broken_records)} garantías con enlaces rotos. Procesando..."))
            
            headers = get_onedrive_headers()
            user_email = "desarrollo@grupogipsy.com"
            folder_path = "GARANTIAS/Facturas"
            valid_extensions = ('.pdf', '.jpg', '.jpeg', '.png', '.heic')
            
            reparados = 0
            errores = 0

            # 2. Iterar y reparar cada uno
            for record in broken_records:
                warranty_number = record.WarrantyNumber
                invoice_file_name = record.invoiceFileName
                file_id = None
                real_file_name = invoice_file_name
                
                self.stdout.write(f"Reparando Garantía {warranty_number} (Archivo: {invoice_file_name})...")
                
                try:
                    clean_name = invoice_file_name.strip()
                    base_name = clean_name
                    
                    # 1. Averiguamos si tiene una extensión conocida y se la quitamos para tener el "nombre base"
                    for ext in valid_extensions:
                        if clean_name.lower().endswith(ext):
                            base_name = clean_name[: -len(ext)]
                            break
                    
                    # 2. Armamos la lista de intentos. 
                    # PRIMERO ponemos el nombre exacto de la BD, luego agregamos las otras variaciones
                    files_to_try = [clean_name]
                    for ext in valid_extensions:
                        possible = f"{base_name}{ext}"
                        if possible not in files_to_try:
                            files_to_try.append(possible)

                    # 3. Probamos todas las combinaciones en OneDrive
                    file_id = None
                    real_file_name = None
                    
                    for possible_name in files_to_try:
                        encoded_name = quote(possible_name)
                        file_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/root:/{folder_path}/{encoded_name}"
                        response = requests.get(file_url, headers=headers)
                        
                        if response.status_code == 200:
                            file_id = response.json().get('id')
                            real_file_name = possible_name
                            break # ¡Lo encontramos! Salimos de la búsqueda

                    # 4. Generamos el enlace
                    if file_id:
                        create_link_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/drive/items/{file_id}/createLink"
                        link_response = requests.post(create_link_url, headers=headers, json={'type': 'view', 'scope': 'anonymous'})
                        
                        if link_response.status_code in (200, 201):
                            new_public_url = link_response.json()['link']['webUrl']
                            new_public_url += "&action=embedview" if "?" in new_public_url else "?action=embedview"
                            
                            update_sql = "UPDATE Warranty.warranty SET invoiceCopyPath = ?, invoiceFileName = ? WHERE WarrantyNumber = ?"
                            cursor.execute(update_sql, (new_public_url, real_file_name, warranty_number))
                            connection.commit()
                            
                            self.stdout.write(self.style.SUCCESS(f"  [OK] Garantía {warranty_number} reparada (Encontrado como: {real_file_name})"))
                            reparados += 1
                        else:
                            self.stdout.write(self.style.ERROR(f"  [ERROR] Se encontró el archivo, pero falló la creación del link."))
                            errores += 1
                    else:
                        self.stdout.write(self.style.ERROR(f"  [ERROR] No se encontró el archivo en OneDrive tras probar {len(files_to_try)} combinaciones."))
                        errores += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  [ERROR API] Fallo al procesar: {str(e)}"))
                    errores += 1

                time.sleep(0.5)

            # Resumen final
            self.stdout.write("\n" + "="*40)
            self.stdout.write(self.style.SUCCESS("RESUMEN DE REPARACIÓN"))
            self.stdout.write("="*40)
            self.stdout.write(f"Total procesados: {len(broken_records)}")
            self.stdout.write(self.style.SUCCESS(f"Reparados con éxito: {reparados}"))
            if errores > 0:
                self.stdout.write(self.style.ERROR(f"Errores: {errores}"))

        except Exception as e:
            raise CommandError(f"Error crítico conectando a BD: {str(e)}")
        finally:
            if cursor: cursor.close()
            if connection: connection.close()