import whois
import csv
import sys
import smtplib
import ssl
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# --- CONFIGURACIÓN ---
# EMAIL_RECIPIENT, GMAIL_USER, GMAIL_APP_PASSWORD ahora se leen de las variables de entorno
DAYS_THRESHOLD = 45
NOTIFICATION_INTERVAL = 15

# --- SCRIPT ---

archivo_csv = "whois_dominios.csv"
encabezados = [
    "Dominio", "Fecha de Registro", "Fecha de Expiración", "Registrar",
    "Contacto Registrante", "NameServers", "UltimoAviso"
]

def format_date(date_obj):
    if not date_obj: return None
    if isinstance(date_obj, list): date_obj = date_obj[0]
    if isinstance(date_obj, datetime): return date_obj.strftime('%Y-%m-%d')
    return str(date_obj)

def obtener_datos_whois(dominio):
    try:
        info = whois.whois(dominio)
        if not info or not info.domain_name:
            raise Exception("No se pudo obtener info WHOIS.")
        return {
            "Dominio": dominio,
            "Fecha de Registro": format_date(info.creation_date),
            "Fecha de Expiración": format_date(info.expiration_date),
            "Registrar": info.registrar,
            "Contacto Registrante": getattr(info, "name", None) or getattr(info, "registrant_name", None),
            "NameServers": ", ".join(info.name_servers) if info.name_servers else None
        }
    except Exception:
        return {"Dominio": dominio, "Fecha de Expiración": "Error"}

def send_email_notification(domains_to_notify):
    sender_email = os.environ.get('GMAIL_USER')
    app_password = os.environ.get('GMAIL_APP_PASSWORD')
    email_recipient = os.environ.get('EMAIL_RECIPIENT')

    if not sender_email or not app_password or not email_recipient:
        print("❌ Error: Las variables de entorno GMAIL_USER, GMAIL_APP_PASSWORD o EMAIL_RECIPIENT no están configuradas. No se puede enviar el correo.")
        return

    body = "Hola,\n\nLos siguientes dominios requieren tu atención por su próxima fecha de expiración:\n"
    for item in domains_to_notify:
        body += "\n------------------------------------\n"
        body += f"Dominio: {item.get('Dominio', 'N/A')}\n"
        body += f"  Expira: {item.get('Fecha de Expiración', 'N/A')}\n"
        body += f"  Registrar: {item.get('Registrar', 'N/A')}\n"
        body += f"  Registrante: {item.get('Contacto Registrante', 'N/A')}\n"
        body += f"  NameServers: {item.get('NameServers', 'N/A')}\n"
    
    body += "\n\nSaludos,\nTu script de monitoreo de dominios."

    subject = "Aviso de Expiración de Dominios"
    
    message = f"Subject: {subject}\nTo: {email_recipient}\nFrom: {sender_email}\n\n{body}"

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, email_recipient, message.encode('utf-8'))
        print(f"📧 Correo de notificación enviado a {email_recipient}")
    except Exception as e:
        print(f"❌ Error al enviar correo con SMTP: {e}")

# --- LÓGICA PRINCIPAL ---

dominios_existentes = []
try:
    with open(archivo_csv, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for header in encabezados:
                row.setdefault(header, None)
            dominios_existentes.append(row)
except FileNotFoundError:
    print(f"⚠️  No se encontró el archivo {archivo_csv}. Se creará uno nuevo.")

dominios_nuevos_nombres = sys.argv[1:]
if dominios_nuevos_nombres:
    print(f"➕ Dominios para agregar: {', '.join(dominios_nuevos_nombres)}")
    nombres_existentes = {d['Dominio'] for d in dominios_existentes}
    for new_domain in dominios_nuevos_nombres:
        if new_domain not in nombres_existentes:
            dominios_existentes.append({"Dominio": new_domain})

resultados_actualizados = []
for dominio_data in dominios_existentes:
    nombre_dominio = dominio_data['Dominio']
    print(f"🔎 Verificando {nombre_dominio}...")
    datos_nuevos = obtener_datos_whois(nombre_dominio)
    dominio_data.update(datos_nuevos)
    resultados_actualizados.append(dominio_data)

dominios_para_notificar = []
today = datetime.now()

for item in resultados_actualizados:
    exp_date_str = item.get("Fecha de Expiración")
    if not exp_date_str or "Error" in exp_date_str:
        continue

    try:
        exp_date = datetime.strptime(exp_date_str, '%Y-%m-%d')
        days_until_expiry = (exp_date - today).days

        if days_until_expiry <= DAYS_THRESHOLD:
            should_notify = False
            last_notice_str = item.get("UltimoAviso")
            last_notice_date = None
            if last_notice_str:
                last_notice_date = datetime.strptime(last_notice_str, '%Y-%m-%d')

            if days_until_expiry <= 1:
                should_notify = True
            elif not last_notice_date:
                should_notify = True
            elif (today - last_notice_date).days >= NOTIFICATION_INTERVAL:
                should_notify = True

            if should_notify:
                dominios_para_notificar.append(item)
                item["UltimoAviso"] = today.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        continue

if dominios_para_notificar:
    send_email_notification(dominios_para_notificar)
else:
    print("👍 No hay dominios que requieran notificación hoy.")

def sort_key(item):
    exp_date_str = item.get("Fecha de Expiración")
    if exp_date_str and "Error" not in exp_date_str:
        try:
            return datetime.strptime(exp_date_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            return datetime.max
    return datetime.max

resultados_actualizados.sort(key=sort_key)

with open(archivo_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=encabezados)
    writer.writeheader()
    writer.writerows(resultados_actualizados)

print(f"✅ Proceso completado. Archivo guardado en {archivo_csv}")