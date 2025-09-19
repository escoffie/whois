# Monitor de Expiración de Dominios

Este script de Python monitorea una lista de dominios, verifica sus fechas de expiración y envía notificaciones por correo electrónico para aquellos que están a punto de vencer.

## Características

- Lee una lista de dominios desde un archivo `whois_dominios.csv`.
- Verifica la información WHOIS de cada dominio.
- Envía un resumen por correo electrónico de los dominios que expiran en 45 días o menos.
- Lógica de notificación inteligente para evitar spam (avisa cada 15 días y en los días críticos).
- Permite agregar nuevos dominios fácilmente a través de la línea de comandos.
- Ignora el archivo de datos (`whois_dominios.csv`) del control de versiones.
- Configuración de credenciales y destinatario de correo a través de un archivo `.env`.

## Requisitos

- Python 3
- `pip` para instalar dependencias.
- Un sistema operativo tipo Unix (macOS, Linux) con `cron` y `whois` instalado.

## Instalación

1.  **Clona el repositorio** (si es necesario):
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd whois_checker
    ```

2.  **Crea tu archivo de dominios**:
    Copia el archivo de ejemplo y añade tus dominios en la primera columna.
    ```bash
    cp whois_dominios.ejemplo.csv whois_dominios.csv
    ```

3.  **Instala las dependencias de Python**:
    ```bash
    pip3 install -r requirements.txt
    ```

## Uso

### Configuración de Variables de Entorno (`.env`)

Crea un archivo llamado `.env` en la raíz del proyecto (al mismo nivel que `whois_checker.py`) con el siguiente contenido, reemplazando los valores con tus credenciales:

```
GMAIL_USER="tu_correo@gmail.com"
GMAIL_APP_PASSWORD="tu_contraseña_de_16_letras"
EMAIL_RECIPIENT="tu_correo_destinatario@ejemplo.com"
```

**Importante:** `GMAIL_APP_PASSWORD` es la contraseña de aplicación que generaste en tu cuenta de Google. `EMAIL_RECIPIENT` es la dirección a la que se enviarán los avisos.

### Ejecución Manual

Para correr el script manualmente y actualizar el archivo CSV (las variables se cargarán automáticamente desde `.env`):
```bash
python3 whois_checker.py
```

### Agregar Nuevos Dominios

Puedes agregar uno o más dominios a tu lista directamente desde la terminal:
```bash
python3 whois_checker.py nuevodominio.com otromas.net
```

## Automatización (Cron Job)

Para que el script se ejecute automáticamente todos los días (ej. a las 9:00 AM):

1.  Abre tu editor de `cron` con el comando `crontab -e`.
2.  Añade la siguiente línea:

    ```
    0 9 * * * cd /ruta/absoluta/a/tu/proyecto && python3 whois_checker.py >> /ruta/absoluta/a/tu/proyecto/cron.log 2>&1
    ```
    *(Asegúrate de reemplazar `/ruta/absoluta/a/tu/proyecto` con la ruta absoluta correcta a tu proyecto.)*
    ```
    *(Asegúrate de que `/Users/bernardoescoffietorre/dev/whois_checker` sea la ruta absoluta correcta a tu proyecto.)*