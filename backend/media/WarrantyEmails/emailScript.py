import os
from email.message import EmailMessage
import ssl
import smtplib
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()


# Envío de correo, hay que adaptar esta función a la de Django
def send_email(subject, body_html, sender_email, email_password, receiver_emails, invoice_path=None, warranty_id=None):
    
    print("Datos para envío del correo:")
    print("subject: ", subject)
    print("sender_email: ", sender_email)
    print("receiver_email: ", receiver_emails)

    mail_server = os.environ.get("EMAIL_HOST")
    mail_port = os.environ.get("MAIL_PORT")

    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = ", ".join(receiver_emails)
    msg['Subject'] = subject

    msg.make_related()
    
    alternative_part = EmailMessage()
    alternative_part.set_content("Este es un correo con contenido HTML. Por favor, use un cliente de correo compatible para ver el contenido completo.")
    alternative_part.add_alternative(body_html, subtype='html')
    
    msg.attach(alternative_part)

    # Imagen Adjunta (de existir)
    if invoice_path and Path(invoice_path).exists():
        with open(invoice_path, "rb") as invoice_file:
            invoice_data = invoice_file.read()
            invoice_filename = f"invoice_{warranty_id}.png"
            msg.add_related(invoice_data, 'image', 'png', cid='invoice_image', filename=invoice_filename)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(mail_server, mail_port, context=context) as smtp:
            smtp.login(sender_email, email_password)
            smtp.sendmail(sender_email, receiver_emails, msg.as_string())
        print(f"Correo enviado exitosamente a {', '.join(receiver_emails)}!")
    except Exception as e:
        print(f"Error al enviar el correo a {', '.join(receiver_emails)}: {e}")


# NOTIFICACIÓN DE REGISTRO DE USUARIO

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
                    <li><strong>Dirección:</strong> {data["address"]}</li>
                    <li><strong>Correo Electrónico:</strong> {data["email_address"]}</li>
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
                        <th>ID de Garantía</th>
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
                        <td>{data["barcode"]}</td>
                    </tr>
                </table>
                <p>Para su referencia, se adjunta una copia de la factura de compra.</p>
                <div class="invoice-section">
                    <h3>Factura Adjunta</h3>
                    <img src="cid:invoice_image" alt="Factura del producto" />
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
                        <th>Nombre del Usuario</th>
                        <td>{data["user_name"]}</td>
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
                        <td>{data["barcode"]}</td>
                    </tr>
                </table>
                <p>La factura del producto se encuentra adjunta.</p>
            </div>
            <div class="footer">
                <p>Este es un correo automático.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


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
                        <th>Sucursal</th>
                        <td>{data["branch_name"]}</td>
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
                        <th>Usuario</th>
                        <td>{data["user_name"]}</td>
                    </tr>
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
                        <th>Sucursal</th>
                        <td>{data["branch_name"]}</td>
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
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no responda a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


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
                <p><strong>Hola, {data["user_name"]}.</strong></p>
                <p>Nos complace informarle que su caso de garantía ha sido cerrado. A continuación, se muestra el resumen de su caso y las acciones realizadas por nuestro equipo de servicio técnico:</p>
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
                        <th>Sucursal</th>
                        <td>{data["branch_name"]}</td>
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
                    <tr>
                        <th>Diagnóstico</th>
                        <td>{data["diagnostic"]}</td>
                    </tr>
                    <tr>
                        <th>Descripción de la Acción Realizada</th>
                        <td>{data["action_description"]}</td>
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
                <p>Se ha cerrado el caso de garantía #{data["case_number"]}. A continuación, se muestra el resumen y las acciones realizadas:</p>
                <table class="data-table">
                    <tr>
                        <th>Usuario</th>
                        <td>{data["user_name"]}</td>
                    </tr>
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
                        <th>Sucursal</th>
                        <td>{data["branch_name"]}</td>
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
                    <tr>
                        <th>Diagnóstico</th>
                        <td>{data["diagnostic"]}</td>
                    </tr>
                    <tr>
                        <th>Descripción de la Acción Realizada</th>
                        <td>{data["action_description"]}</td>
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


if __name__ == "__main__":
    print("Script de prueba de envío de correos de garantías")
    receiver_email_test = os.environ.get("MAIL_RECIPIENT_TEST") #RECEPTOR DE PRUEBA

    sender_email = os.environ.get("MAIL_USERNAME_RECEIPT_REMBD")
    email_password = os.environ.get("MAIL_PASSWORD_RECEIPT_REMBD")
    
    
    # ---REGISTRO DE USUARIO---

    registration_data = {
        "user_name": "Pepe",
        "first_name": "Pedro",
        "last_name": "Pérez",
        "address": "Su casa",
        "email_address": "pepe@user.com"
    }

    # Versión Cliente
    subject = "Usted se ha registrado exitosamente en Gipsy Garantías"
    body_html = create_registration_html(registration_data['user_name'])
    recipient_emails = [receiver_email_test]
    send_email(subject, body_html, sender_email, email_password, recipient_emails)

    # Versión Admin
    subject = f"Nuevo Usuario {registration_data['user_name']} Registrado"
    body_html = create_registration_company_html(registration_data)
    recipient_emails = [receiver_email_test]
    send_email(subject, body_html, sender_email, email_password, recipient_emails)


    # ---REGISTRO DE GARANTÍA---

    warranty_id = 1234
    warranty_data = {
        "warranty_id": warranty_id,
        "user_name": "Pepe",
        "store_name": "Tienda Ejemplo S.A.",
        "branch_name": "TecnoGlobal Caracas",
        "store_rif": "J-12345678-9",
        "purchase_date": "19/08/2025",
        "invoice_number": "0000-0012345",
        "product_brand": "MarcaEjemplo",
        "product_model": "ModeloXYZ",
        "barcode": "1234567890123"
    }
    invoice_file_path = "invoiceSample.png"

    # Versión Cliente
    subject = f"Usted ha registrado exitosamente la Garantía #{warranty_id}"
    body_html = create_warranty_registration_html(warranty_data)
    recipient_emails = [receiver_email_test]
    send_email(subject, body_html, sender_email, email_password, recipient_emails, invoice_file_path, warranty_id)

    # Versión Admin
    subject = f"Se ha registrado la Garantía #{warranty_id}"
    body_html = create_warranty_registration_company_html(warranty_data)
    recipient_emails = [receiver_email_test]
    send_email(subject, body_html, sender_email, email_password, recipient_emails, invoice_file_path, warranty_id)


    # ---APERTURA DE CASO DE GARANTÍA---

    open_case_data = {
        "user_name": "Pepe",
        "case_number": 123,
        "warranty_code": warranty_id,
        "store_name": "TecnoGlobal",
        "branch_name": "TecnoGlobal Caracas",
        "product_name": "Televisor QLED",
        "reception_date": "2024-07-05",
        "case_status": "Abierto",
    }

    # Versión Cliente
    subject = f"Garantía #{warranty_id}: Se ha abierto el caso #{open_case_data['case_number']}"
    body_html = create_open_case_html(open_case_data)
    recipient_emails = [receiver_email_test]
    send_email(subject, body_html, sender_email, email_password, recipient_emails)

    # Versión Admin
    subject = f"Garantía #{warranty_id}: Se ha abierto el caso #{open_case_data['case_number']}"
    body_html = create_open_case_company_html(open_case_data)
    recipient_emails = [receiver_email_test]
    send_email(subject, body_html, sender_email, email_password, recipient_emails)


    # ---CIERRE DE CASO DE GARANTÍA---

    closed_case_data = {
        "user_name": "Pepe",
        "case_number": 123,
        "warranty_code": warranty_id,
        "store_name": "TecnoGlobal",
        "branch_name": "TecnoGlobal Caracas",
        "product_name": "Televisor QLED",
        "reception_date": "2024-07-05",
        "case_status": "Cerrado",
        "diagnostic": "Falla de encendido",
        "action_description": "Se reemplazó la tarjeta principal. El equipo se probó y funciona correctamente."
    }

    # Versión Cliente
    subject_closed_case = f"Garantía #{warranty_id}: Se ha cerrado el caso #{closed_case_data['case_number']}"
    body_html_closed_case = create_closed_case_html(closed_case_data)
    recipient_emails = [receiver_email_test]
    send_email(subject_closed_case, body_html_closed_case, sender_email, email_password, recipient_emails)

    # Versión Admin
    subject_closed_case = f"Garantía #{warranty_id}: Se ha cerrado el caso #{closed_case_data['case_number']}"
    body_html_closed_case = create_closed_case_company_html(closed_case_data)
    recipient_emails = [receiver_email_test]
    send_email(subject_closed_case, body_html_closed_case, sender_email, email_password, recipient_emails)

    print("Prueba de envío de correo completada.")