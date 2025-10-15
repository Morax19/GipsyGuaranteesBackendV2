import os

from pathlib import Path
from django.core.mail import EmailMessage

from dotenv import load_dotenv
load_dotenv()

# Versión Cliente
def create_registration_html(user_name):
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"/>
        <style>
            body {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
                color: black !important;
                background: white !important;
                font-family: Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #6c757d;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .header h2 {{
                margin: 0;
                color: #333;
            }}
            .body-content {{
                color: #555;
            }}
            .body-content p {{
                margin: 0 0 15px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
                font-size: 0.9em;
                color: #888;
            }}
            .button {{
                display: inline-block;
                padding: 10px 20px;
                margin-top: 20px;
                background-color: #619990;
                color: white !important;
                text-decoration: none;
                border-radius: 5px;
            }}
            .button:hover{{
                background-color: #4e867c;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Bienvenido al Servicio de Garantías</h2>
            </div>
            <div class="body-content">
                <p><strong>Hola, {user_name}.</strong></p>
                <p>Su registro se ha completado exitosamente. Ahora tiene acceso a todas las funcionalidades de nuestra plataforma.</p>
                <p>Con el Servicio de Garantías, puede registrar de manera eficiente las garantías de los productos que ha comprado, visualizar su historial de garantías y consultar la información sobre el Servicio Técnico disponible en caso de requerirlo.</p>
            </div>
            <div style="text-align: center;">
                 <a href="https://www.garantiasservicio.com/" class="button"><strong>Ir a la aplicación</strong></a>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no responda a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

# Versión Admin
def create_registration_company_html(data):
    if data['address'] != '':
        address_li = f"<li><strong>Dirección:</strong> {data['address']}</li>"
    else:
        address_li = ""

    if data['phone_number'] != '':
        phone_li = f"<li><strong>Teléfono:</strong> {data['phone_number']}</li>"
    else:
        phone_li = ""

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"/>
        <style>
            body {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
                color: black !important;
                background: white !important;
                font-family: Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #6c757d;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .header h2 {{
                margin: 0;
                color: #333;
            }}
            .body-content {{
                color: #555;
            }}
            .body-content p {{
                margin: 0 0 15px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
                font-size: 0.9em;
                color: #888;
            }}
            .button {{
                display: inline-block;
                padding: 10px 20px;
                margin-top: 20px;
                background-color: #007bff;
                color: white !important;
                text-decoration: none;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Nuevo Registro de Usuario</h2>
            </div>
            <div class="body-content">
                <p>Se ha registrado un nuevo usuario en la plataforma Servicio de Garantías.</p>
                <p><strong>Detalles del usuario:</strong></p>
                <ul>
                    <li><strong>Nombre de Usuario:</strong> {data["user_name"]}</li>
                    <li><strong>Nombre y Apellido:</strong> {data["first_name"]} {data["last_name"]}</li>
                    <li><strong>Correo Electrónico:</strong> {data["email_address"]}</li>
                    {address_li}
                    {phone_li}            
                </ul>
            </div>
            <div class="footer">
                <p>Este es un correo automático.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def send_user_register_email(data):
    try:
        email_content_user = create_registration_html(data['first_name'])

        msg = EmailMessage(
            "Servicio de Garantías - Nuevo Registro de Usuario",
            email_content_user,
            os.environ.get('EMAIL_HOST_USER'),
            [data['email_address']]
        )

        msg.content_subtype = "html"
        msg.send()

        email_content_intern = create_registration_company_html(data)

        msg_intern = EmailMessage(
            "Servicio de Garantías - Nuevo Registro de Usuario",
            email_content_intern,
            os.environ.get('EMAIL_HOST_USER'),
            [os.environ.get('EMAIL_WARRANTY_GIPSYCORP')]
        )

        msg_intern.content_subtype = "html"
        msg_intern.send()
        return True

    except Exception as e:
        print(f"Error sending registration email: {e}")
        return False

# NOTIFICACIÓN DE REGISTRO DE GARANTÍA

# Versión Cliente
def create_warranty_registration_html(data):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8" />
        <style>
            body {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
                color: black !important;
                background: white !important;
                font-family: Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #6c757d;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .header h2 {{
                margin: 0;
                color: #333;
            }}
            .body-content {{
                color: #555;
            }}
            .body-content p {{
                margin: 0 0 15px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
                font-size: 0.9em;
                color: #888;
            }}
            .data-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            .data-table th, .data-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            .data-table th {{
                background-color: #f2f2f2;
                color: #333;
                width: 40%;
            }}
            .data-table td {{
                word-wrap: break-word;
            }}
            .invoice-section {{
                text-align: left;
                margin-top: 20px;
            }}
            .invoice-section img {{
                max-width: 100%;
                height: auto;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Registro de Garantía Exitoso</h2>
            </div>
            <div class="body-content">
                <p><strong>Hola, {data["user_name"]}.</strong></p>
                <p>Se ha registrado exitosamente la garantía para su producto. A continuación, se detallan los datos de la garantía:</p>
                <table class="data-table">
                    <tr>
                        <th>Número de Garantía</th>
                        <td>{data["warranty_id"]}</td>
                    </tr>
                    <tr>
                        <th>Compañía Asociada</th>
                        <td>{data["store_name"]}</td>
                    </tr>
                    <tr>
                        <th>Sucursal</th>
                        <td>{data["branch_name"]}</td>
                    </tr>
                    <tr>
                        <th>RIF de la tienda</th>
                        <td>{data["store_rif"]}</td>
                    </tr>
                    <tr>
                        <th>Fecha de compra</th>
                        <td>{data["purchase_date"]}</td>
                    </tr>
                    <tr>
                        <th>Número de Factura</th>
                        <td>{data["invoice_number"]}</td>
                    </tr>
                    <tr>
                        <th>Marca del producto</th>
                        <td>{data["product_brand"]}</td>
                    </tr>
                    <tr>
                        <th>Modelo del producto</th>
                        <td>{data["product_model"]}</td>
                    </tr>
                    <tr>
                        <th>Código de Barras</th>
                        <td>{data["product_barcode"]}</td>
                    </tr>
                </table>
                <p>Para su referencia, se adjunta una copia de la factura de compra.</p>
                <div class="invoice-section">
                    <h3>Factura Adjunta</h3>
                    <a href="{data['invoice_img_path']}" target="_blank">
                        <img src="{data['invoice_img_path']}" alt="Presione para visualizar la Factura del Producto">
                    </a>
                </div>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no responda a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

# Versión Admin
def create_warranty_registration_company_html(data):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8" />
        <style>
            body {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
                color: black !important;
                background: white !important;
                font-family: Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #6c757d;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .header h2 {{
                margin: 0;
                color: #333;
            }}
            .body-content {{
                color: #555;
            }}
            .body-content p {{
                margin: 0 0 15px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
                font-size: 0.9em;
                color: #888;
            }}
            .data-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            .data-table th, .data-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            .data-table th {{
                background-color: #f2f2f2;
                color: #333;
                width: 40%;
            }}
            .data-table td {{
                word-wrap: break-word;
            }}
            .invoice-section {{
                text-align: left;
                margin-top: 20px;
            }}
            .invoice-section img {{
                max-width: 100%;
                height: auto;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Nueva Garantía Registrada</h2>
            </div>
            <div class="body-content">
                <p>Se ha registrado una nueva garantía con los siguientes detalles:</p>
                <table class="data-table">
                    <tr>
                        <th>ID de Garantía</th>
                        <td>{data["warranty_id"]}</td>
                    </tr>
                    <tr>
                        <th>Correo electrónico del Usuario</th>
                        <td>{data["email_address"]}</td>
                    </tr>
                    <tr>
                        <th>Compañía Asociada</th>
                        <td>{data["store_name"]}</td>
                    </tr>
                    <tr>
                        <th>Sucursal</th>
                        <td>{data["branch_name"]}</td>
                    </tr>
                    <tr>
                        <th>RIF de la tienda</th>
                        <td>{data["store_rif"]}</td>
                    </tr>
                    <tr>
                        <th>Fecha de compra</th>
                        <td>{data["purchase_date"]}</td>
                    </tr>
                    <tr>
                        <th>Número de Factura</th>
                        <td>{data["invoice_number"]}</td>
                    </tr>
                    <tr>
                        <th>Marca del producto</th>
                        <td>{data["product_brand"]}</td>
                    </tr>
                    <tr>
                        <th>Modelo del producto</th>
                        <td>{data["product_model"]}</td>
                    </tr>
                    <tr>
                        <th>Código de Barras</th>
                        <td>{data["product_barcode"]}</td>
                    </tr>
                </table>
                <p>La factura del producto se encuentra adjunta.</p>
                <div class="invoice-section">
                    <h3>Factura Adjunta</h3>
                    <a href="{data['invoice_img_path']}" target="_blank">
                        <img src="{data['invoice_img_path']}" alt="Presione para visualizar la Factura del Producto">
                    </a>
                </div>
            </div>
            <div class="footer">
                <p>Este es un correo automático.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def send_warranty_register_email(data):
    try:
        email_content_user = create_warranty_registration_html(data)

        msg = EmailMessage(
            f"Servicio de Garantías - Nuevo Registro de Garantía #{data['warranty_id']}",
            email_content_user,
            os.environ.get('EMAIL_HOST_USER'),
            [data['email_address']]
        )

        msg.content_subtype = "html"
        msg.send()

        email_content_intern = create_warranty_registration_company_html(data)

        msg_intern = EmailMessage(
            f"Servicio de Garantías - Nuevo Registro de Garantía #{data['warranty_id']}",
            email_content_intern,
            os.environ.get('EMAIL_HOST_USER'),
            [os.environ.get('EMAIL_WARRANTY_GIPSYCORP')]
        )

        msg_intern.content_subtype = "html"
        msg_intern.send()
        return True

    except Exception as e:
        print(f"Error sending registration email: {e}")
        return False

# NOTIFICACIÓN DE APERTURA DE CASO DE GARANTÍA

# Versión Cliente
def create_open_case_html(data):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"/>
        <style>
            body {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
                color: black !important;
                background: white !important;
                font-family: Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #6c757d;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .header h2 {{
                margin: 0;
                color: #333;
            }}
            .body-content {{
                color: #555;
            }}
            .body-content p {{
                margin: 0 0 15px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
                font-size: 0.9em;
                color: #888;
            }}
            .data-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            .data-table th, .data-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            .data-table th {{
                background-color: #f2f2f2;
                color: #333;
                width: 40%;
            }}
            .data-table td {{
                word-wrap: break-word;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Apertura de Caso de Garantía</h2>
            </div>
            <div class="body-content">
                <p><strong>Hola, {data["user_name"]}.</strong></p>
                <p>Su solicitud de servicio ténico ha sido recibida exitosamente. Se ha aperturado un nuevo caso de garantía para su producto y nuestro equipo se encuentra en proceso de revisión.</p>
                <p>A continuación, se muestra el resumen de su caso:</p>
                <table class="data-table">
                    <tr>
                        <th>Número de Caso</th>
                        <td>{data["case_number"]}</td>
                    </tr>
                    <tr>
                        <th>Código de Garantía</th>
                        <td>{data["warranty_code"]}</td>
                    </tr>
                    <tr>
                        <th>Tienda</th>
                        <td>{data["store_name"]}</td>
                    </tr>
                    <tr>
                        <th>Producto</th>
                        <td>{data["product_name"]}</td>
                    </tr>
                    <tr>
                        <th>Fecha de Recepción</th>
                        <td>{data["reception_date"]}</td>
                    </tr>
                    <tr>
                        <th>Estado del Caso</th>
                        <td>{data["case_status"]}</td>
                    </tr>
                </table>
                <p>Le notificaremos tan pronto como haya una actualización en el estado de su caso.</p>
                <p>Si tiene alguna pregunta, no dude en contactar a nuestro equipo de soporte técnico.</p>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no responda a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

# Versión admin
def create_open_case_company_html(data):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"/>
        <style>
            body {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
                color: black !important;
                background: white !important;
                font-family: Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #6c757d;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .header h2 {{
                margin: 0;
                color: #333;
            }}
            .body-content {{
                color: #555;
            }}
            .body-content p {{
                margin: 0 0 15px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
                font-size: 0.9em;
                color: #888;
            }}
            .data-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            .data-table th, .data-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            .data-table th {{
                background-color: #f2f2f2;
                color: #333;
                width: 40%;
            }}
            .data-table td {{
                word-wrap: break-word;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Apertura de Caso de Garantía</h2>
            </div>
            <div class="body-content">
                <p>Se ha aperturado un nuevo caso de garantía con los siguientes datos:</p>
                <table class="data-table">
                    <tr>
                        <th>Cliente</th>
                        <td>{data['user_name']}</td>
                    </tr>
                    <tr>
                        <th>Correo Electrónico</th>
                        <td>{data['email_address']['customer']}</td>
                    </tr>
                    <tr>
                        <th>Número de Caso</th>
                        <td>{data['case_number']}</td>
                    </tr>
                    <tr>
                        <th>Código de Garantía</th>
                        <td>{data['warranty_code']}</td>
                    </tr>
                    <tr>
                        <th>Tienda</th>
                        <td>{data['store_name']}</td>
                    </tr>
                    <tr>
                        <th>Producto</th>
                        <td>{data['product_name']}</td>
                    </tr>
                    <tr>
                        <th>Fecha de Recepción</th>
                        <td>{data['reception_date']}</td>
                    </tr>
                    <tr>
                        <th>Estado del Caso</th>
                        <td>{data['case_status']}</td>
                    </tr>
                </table>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no responda a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def send_warranty_open_case_email(data):
    try:
        email_content_user = create_open_case_html(data)

        msg = EmailMessage(
            f"Servicio de Garantías - Apertura de Caso Servicio Técnico #{data['case_number']}",
            email_content_user,
            os.environ.get('EMAIL_HOST_USER'),
            [data['email_address']['customer']]
        )

        msg.content_subtype = "html"
        msg.send()

        email_content_intern = create_open_case_company_html(data)

        msg_intern = EmailMessage(
            f"Servicio de Garantías - Apertura de Caso Servicio Técnico #{data['case_number']}",
            email_content_intern,
            os.environ.get('EMAIL_HOST_USER'),
            [
                os.environ.get('EMAIL_WARRANTY_GIPSYCORP'),
                data['email_address']['technical_service']
            ]
        )

        msg_intern.content_subtype = 'html'
        msg_intern.send()
        return True

    except Exception as e:
        print(f'Error sending registration email: {e}')
        return False

# NOTIFICACIÓN DE ACTUALIZACIÓN DE UN CASO

# Versión Cliente
def create_update_case_html(data):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"/>
        <style>
            body {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
                color: black !important;
                background: white !important;
                font-family: Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #6c757d;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .header h2 {{
                margin: 0;
                color: #333;
            }}
            .body-content {{
                color: #555;
            }}
            .body-content p {{
                margin: 0 0 15px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
                font-size: 0.9em;
                color: #888;
            }}
            .data-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            .data-table th, .data-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            .data-table th {{
                background-color: #f2f2f2;
                color: #333;
                width: 40%;
            }}
            .data-table td {{
                word-wrap: break-word;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Actualización de Caso de Garantía</h2>
            </div>
            <div class="body-content">
                <p><strong>Hola, {data['user_name']}.</strong></p>
                <p>Se ha actualizado su caso de garantía para su producto por parte de nuestro equipo.</p>
                <p>A continuación, se muestra el resumen de su caso:</p>
                <table class="data-table">
                    <tr>
                        <th>Número de Caso</th>
                        <td>{data['case_number']}</td>
                    </tr>
                    <tr>
                        <th>Código de Garantía</th>
                        <td>{data['warranty_code']}</td>
                    </tr>
                    <tr>
                        <th>Tienda</th>
                        <td>{data['store_name']}</td>
                    </tr>
                    <tr>
                        <th>Producto</th>
                        <td>{data['product_name']}</td>
                    </tr>
                    <tr>
                        <th>Fecha de Recepción</th>
                        <td>{data['reception_date']}</td>
                    </tr>
                    <tr>
                        <th>Estado del Caso</th>
                        <td>{data['case_status']}</td>
                    </tr>
                    <tr>
                        <th>Diagnóstico</th>
                        <td>{data['issue_description']}</td>
                    </tr>
                    <tr>
                        <th>Acción Realizada</th>
                        <td>{data['issue_resolution_details']}</td>
                    </tr>
                </table>
                <p>Le notificaremos tan pronto como haya una actualización en el estado de su caso.</p>
                <p>Si tiene alguna pregunta, no dude en contactar a nuestro equipo de soporte técnico.</p>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no responda a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

# Versión admin
def create_update_case_company_html(data):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"/>
        <style>
            body {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
                color: black !important;
                background: white !important;
                font-family: Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #6c757d;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .header h2 {{
                margin: 0;
                color: #333;
            }}
            .body-content {{
                color: #555;
            }}
            .body-content p {{
                margin: 0 0 15px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
                font-size: 0.9em;
                color: #888;
            }}
            .data-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            .data-table th, .data-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            .data-table th {{
                background-color: #f2f2f2;
                color: #333;
                width: 40%;
            }}
            .data-table td {{
                word-wrap: break-word;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Actualización de Caso de Garantía</h2>
            </div>
            <div class="body-content">
                <p>Se ha actualizado un caso de garantía con los siguientes datos:</p>
                <table class="data-table">
                    <tr>
                        <th>Cliente</th>
                        <td>{data['user_name']}</td>
                    </tr>
                    <tr>
                        <th>Correo Electrónico</th>
                        <td>{data['email_address']['customer']}</td>
                    </tr>
                    <tr>
                        <th>Número de Caso</th>
                        <td>{data['case_number']}</td>
                    </tr>
                    <tr>
                        <th>Código de Garantía</th>
                        <td>{data['warranty_code']}</td>
                    </tr>
                    <tr>
                        <th>Tienda</th>
                        <td>{data['store_name']}</td>
                    </tr>
                    <tr>
                        <th>Producto</th>
                        <td>{data['product_name']}</td>
                    </tr>
                    <tr>
                        <th>Fecha de Recepción</th>
                        <td>{data['reception_date']}</td>
                    </tr>
                    <tr>
                        <th>Estado del Caso</th>
                        <td>{data['case_status']}</td>
                    </tr>
                    <tr>
                        <th>Diagnóstico</th>
                        <td>{data['issue_description']}</td>
                    </tr>
                    <tr>
                        <th>Acción Realizada</th>
                        <td>{data['issue_resolution_details']}</td>
                    </tr>
                </table>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no responda a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def send_warranty_update_case_email(data):
    try:
        email_content_user = create_update_case_html(data)

        msg = EmailMessage(
            f"Servicio de Garantías - Actualización de Caso Servicio Técnico #{data['case_number']}",
            email_content_user,
            os.environ.get('EMAIL_HOST_USER'),
            [data['email_address']['customer']]
        )

        msg.content_subtype = "html"
        msg.send()

        email_content_intern = create_update_case_company_html(data)

        msg_intern = EmailMessage(
            f"Servicio de Garantías - Actualización de Caso Servicio Técnico #{data['case_number']}",
            email_content_intern,
            os.environ.get('EMAIL_HOST_USER'),
            [
                os.environ.get('EMAIL_WARRANTY_GIPSYCORP'),
                data['email_address']['technical_service']
            ]
        )

        msg_intern.content_subtype = 'html'
        msg_intern.send()
        return True

    except Exception as e:
        print(f'Error sending registration email: {e}')
        return False

# NOTIFICACIÓN DE CIERRE DE CASO DE GARANTÍA

# Versión Cliente
def create_closed_case_html(data):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"/>
        <style>
            body {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
                color: black !important;
                background: white !important;
                font-family: Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #6c757d;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .header h2 {{
                margin: 0;
                color: #333;
            }}
            .body-content {{
                color: #555;
            }}
            .body-content p {{
                margin: 0 0 15px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
                font-size: 0.9em;
                color: #888;
            }}
            .data-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            .data-table th, .data-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            .data-table th {{
                background-color: #f2f2f2;
                color: #333;
                width: 40%;
            }}
            .data-table td {{
                word-wrap: break-word;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Actualización de Garantía - Caso Cerrado</h2>
            </div>
            <div class="body-content">
                <p><strong>Hola, {data['user_name']}.</strong></p>
                <p>Nos complace informarle que su caso de garantía ha sido cerrado. A continuación, se muestra el resumen de su caso y las acciones realizadas por nuestro equipo de servicio técnico:</p>
                <table class="data-table">
                    <tr>
                        <th>Número de Caso</th>
                        <td>{data['case_number']}</td>
                    </tr>
                    <tr>
                        <th>Código de Garantía</th>
                        <td>{data['warranty_code']}</td>
                    </tr>
                    <tr>
                        <th>Tienda</th>
                        <td>{data['store_name']}</td>
                    </tr>
                    <tr>
                        <th>Producto</th>
                        <td>{data['product_name']}</td>
                    </tr>
                    <tr>
                        <th>Fecha de Recepción</th>
                        <td>{data['reception_date']}</td>
                    </tr>
                    <tr>
                        <th>Estado del Caso</th>
                        <td>{data['case_status']}</td>
                    </tr>
                    <tr>
                        <th>Diagnóstico</th>
                        <td>{data['issue_description']}</td>
                    </tr>
                    <tr>
                        <th>Descripción de la Acción Realizada</th>
                        <td>{data['issue_resolution_details']}</td>
                    </tr>
                    <tr>
                        <th>El producto requiere cambio</th>
                        <td>{'Sí' if data['required_change'] == 'true' else 'No'}</td>
                    </tr>
                </table>
                <p>Si tiene alguna pregunta, no dude en contactar a nuestro equipo de soporte técnico.</p>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no responda a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

# Versión Cliente
def create_closed_case_company_html(data):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"/>
        <style>
            body {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
                color: black !important;
                background: white !important;
                font-family: Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #6c757d;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .header h2 {{
                margin: 0;
                color: #333;
            }}
            .body-content {{
                color: #555;
            }}
            .body-content p {{
                margin: 0 0 15px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
                font-size: 0.9em;
                color: #888;
            }}
            .data-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            .data-table th, .data-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            .data-table th {{
                background-color: #f2f2f2;
                color: #333;
                width: 40%;
            }}
            .data-table td {{
                word-wrap: break-word;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Actualización de Garantía - Caso Cerrado</h2>
            </div>
            <div class="body-content">
                <p>Se ha cerrado el caso de garantía #{data['case_number']}. A continuación, se muestra el resumen y las acciones realizadas:</p>
                <table class="data-table">
                    <tr>
                        <th>Cliente</th>
                        <td>{data['user_name']}</td>
                    </tr>
                    <tr>
                        <th>Correo Electrónico</th>
                        <td>{data['email_address']['customer']}</td>
                    </tr>
                    <tr>
                        <th>Número de Caso</th>
                        <td>{data['case_number']}</td>
                    </tr>
                    <tr>
                        <th>Código de Garantía</th>
                        <td>{data['warranty_code']}</td>
                    </tr>
                    <tr>
                        <th>Tienda</th>
                        <td>{data['store_name']}</td>
                    </tr>
                    <tr>
                        <th>Producto</th>
                        <td>{data['product_name']}</td>
                    </tr>
                    <tr>
                        <th>Fecha de Recepción</th>
                        <td>{data['reception_date']}</td>
                    </tr>
                    <tr>
                        <th>Estado del Caso</th>
                        <td>{data['case_status']}</td>
                    </tr>
                    <tr>
                        <th>Diagnóstico</th>
                        <td>{data['issue_description']}</td>
                    </tr>
                    <tr>
                        <th>Descripción de la Acción Realizada</th>
                        <td>{data['issue_resolution_details']}</td>
                    </tr>
                    <tr>
                        <th>El producto requiere cambio</th>
                        <td>{'Sí' if data['required_change'] == 'true' else 'No'}</td>
                    </tr>
                </table>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no responda a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def send_warranty_close_case_email(data):
    try:
        email_content_user = create_closed_case_html(data)

        msg = EmailMessage(
            f"Servicio de Garantías - Cierre de Caso Servicio Técnico #{data['case_number']}",
            email_content_user,
            os.environ.get('EMAIL_HOST_USER'),
            [data['email_address']['customer']]
        )

        msg.content_subtype = "html"
        msg.send()

        email_content_intern = create_closed_case_company_html(data)

        msg_intern = EmailMessage(
            f"Servicio de Garantías - Cierre de Caso Servicio Técnico #{data['case_number']}",
            email_content_intern,
            os.environ.get('EMAIL_HOST_USER'),
            [
                os.environ.get('EMAIL_WARRANTY_GIPSYCORP'),
                data['email_address']['technical_service'],
            ]
        )

        msg_intern.content_subtype = 'html'
        msg_intern.send()
        return True

    except Exception as e:
        print(f'Error sending registration email: {e}')
        return False    

# NOTIFICACIÓN DE CAMBIO DE CLAVE

def create_password_reset_html(data):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"/>
        <style>
            body {{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
                color: black !important;
                background: white !important;
                font-family: Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 20px 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #6c757d;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .header h2 {{
                margin: 0;
                color: #333;
            }}
            .body-content {{
                color: #555;
            }}
            .body-content p {{
                margin: 0 0 15px;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
                font-size: 0.9em;
                color: #888;
            }}
            .password-section {{
                text-align: center;
                margin: 30px 0;
            }}
            .password-box {{
                display: inline-block;
                padding: 15px 30px;
                background-color: #e9ecef;
                border: 1px dashed #adb5bd;
                border-radius: 5px;
                font-size: 1.5em;
                font-weight: bold;
                color: #333;
                word-break: break-all;
            }}
            .button {{
                display: inline-block;
                padding: 10px 20px;
                margin-top: 20px;
                background-color: #619990;
                color: white !important;
                text-decoration: none;
                border-radius: 5px;
            }}
            .button:hover{{
                background-color: #4e867c;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Restablecimiento de Contraseña</h2>
            </div>
            <div class="body-content">
                <p><strong>Hola, {data['user_name']}.</strong></p>
                <p>Hemos recibido una solicitud para restablecer su contraseña. Su código de verificación es el siguiente:</p>
                <div class="password-section">
                    <span class="password-box">{data['temp_password']}</span>
                </div>
                <p>
                    Este código es válido durante 30 minutos, una vez expirado deberá solicitar uno nuevo.
                    Para su seguridad, le recomendamos encarecidamente que reestablezca su contraseña en la aplicación lo más pronto posible.
                </p>
            </div>
            <div style="text-align: center;">
                 <a href="https://www.garantiasservicio.com/set-new-password" class="button"><strong>Reestablecer mi contraseña</strong></a>
            </div>
            <div class="footer">
                <p>Este es un correo automático, no responda a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def send_temp_password_email(data):
    try:
        email_content = create_password_reset_html(data)

        msg = EmailMessage(
            'Servicio de Garantías - Recuperación de contraseña',
            email_content,
            os.environ.get('EMAIL_HOST_USER'),
            [data['email_address']]
        )

        msg.content_subtype = "html"
        msg.send()

        return True

    except Exception as e:
        print(f'Error sending registration email: {e}')
        return False 