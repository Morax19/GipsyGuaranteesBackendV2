import os
import ssl
import smtplib

from pathlib import Path
from django.core.mail import EmailMessage

from dotenv import load_dotenv
load_dotenv()

# Funciones para generar contenido de los correos
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
                <h2>¡Bienvenido a Gipsy Garantías!</h2>
            </div>
            <div class="body-content">
                <p><strong>Hola, {user_name}.</strong></p>
                <p>Su registro se ha completado exitosamente. Ahora tiene acceso a todas las funcionalidades de nuestra plataforma.</p>
                <p>Con Gipsy Garantías, puede registrar de manera eficiente las garantías de los productos que ha comprado, visualizar su historial de garantías y consultar la información sobre el Servicio Técnico disponible en caso de requerirlo.</p>
            </div>
            <div style="text-align: center;">
                 <a href="https://icy-tree-06332be0f.1.azurestaticapps.net" class="button">Ir a la aplicación</a>
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
        address_li = f"<li><strong>Dirección:</strong> {data["address"]}</li>"
    else:
        address_li = ""

    if data['phone_number'] != '':
        phone_li = f"<li><strong>Teléfono:</strong> {data["phone_number"]}</li>"
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
                <p>Se ha registrado un nuevo usuario en la plataforma Gipsy Garantías.</p>
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
            "Nuevo Registro en Gipsy Garantías",
            email_content_user,
            os.environ.get('EMAIL_HOST_USER'),
            [data['email_address']]
        )

        msg.content_subtype = "html"
        msg.send()

        email_content_intern = create_registration_company_html(data)

        msg_intern = EmailMessage(
            "Nuevo Registro de Usuario - Gipsy Garantías",
            email_content_intern,
            os.environ.get('EMAIL_HOST_USER'),
            #[os.environ.get('EMAIL_WARRANTY_GIPSYCORP')]
            [os.environ.get('EMAIL_WARRANTY_TEST')]
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
                    <img src="{data['invoice_img_path']}" alt="Factura del producto" />
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
                    <img src="{data['invoice_img_path']}" alt="Factura del producto" />
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
            "Nueva garantía registrada en Gipsy Garantías",
            email_content_user,
            os.environ.get('EMAIL_HOST_USER'),
            [data['email_address']]
        )

        msg.content_subtype = "html"
        msg.send()

        email_content_intern = create_warranty_registration_company_html(data)

        msg_intern = EmailMessage(
            "Nuevo Registro de Garantía - Gipsy Garantías",
            email_content_intern,
            os.environ.get('EMAIL_HOST_USER'),
            #[os.environ.get('EMAIL_WARRANTY_GIPSYCORP')]
            [os.environ.get('EMAIL_WARRANTY_TEST')]
        )

        msg_intern.content_subtype = "html"
        msg_intern.send()
        return True

    except Exception as e:
        print(f"Error sending registration email: {e}")
        return False    