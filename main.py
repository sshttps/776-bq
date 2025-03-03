import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from PIL import Image, ImageDraw, ImageFont
import pytz
from datetime import datetime

# Token del bot
TOKEN = "7699996224:AAGRK31aHgxUQwgkdtfAOXXEWArEy-0WPnA"  # Reemplaza con tu token seguro

# Rutas de plantillas y fuentes
TEMPLATE_PATH = "plantilla.jpeg"  # Plantilla existente
TEMPLATE_PATH_C2 = "plantilla_c2.jpeg"  # Nueva plantilla para el comando /c2
FONT_PATH = "fuente.ttf"  # Fuente para número y valor
FONT_PATH_CEROS = "fuente.ttf"  # Fuente específica para los ceros
DATE_FONT_PATH = "fuente_fecha.ttf"  # Fuente para la fecha

# Tamaño de la fuente para el número, valor y los ceros
TAMANO_NUMERO = 23
TAMANO_VALOR = 27
TAMANO_CEROS = 20  # Tamaño de fuente para los ceros

# Separación entre la parte entera y los ceros (espaciado horizontal)
SEPARACION_DECIMAL = -1  # Ajuste de separación más pequeño

# Función para formatear la fecha y hora
# Función para formatear la fecha y hora
def obtener_fecha_hora():
    colombia_tz = pytz.timezone('America/Bogota')
    fecha_actual = datetime.now(colombia_tz)
    # Formatear la fecha, obteniendo la abreviatura del mes en minúsculas
    fecha_formateada = fecha_actual.strftime("%d %b %Y - %I:%m %p.")
    # Convertir la primera letra de la abreviatura del mes a mayúscula
    fecha_formateada = fecha_formateada.replace(fecha_formateada.split()[1], fecha_formateada.split()[1].capitalize())
    return fecha_formateada
    
# Función para formatear el valor
def formatear_valor(valor: str) -> str:
    entero = int(valor)
    entero_formateado = f"{entero:,}".replace(",", ".")  # Usar puntos para separar los miles
    return f"{entero_formateado},00"  # Se asegura que los valores tengan ",00"

# Función para formatear el número con guiones
def formatear_numero(numero: str) -> str:
    numero = numero.zfill(10)  # Rellenar con ceros a la izquierda si es necesario
    return f"{numero[:3]} - {numero[3:9]} - {numero[9:]}"  # Añadir guiones

# Función para generar comprobante con /c
def generar_comprobante(numero: str, valor: str) -> str:
    img = Image.open(TEMPLATE_PATH)
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(FONT_PATH, TAMANO_NUMERO)  # Tamaño del número
    font_valor = ImageFont.truetype(FONT_PATH, TAMANO_VALOR)  # Fuente para el valor
    small_font = ImageFont.truetype(FONT_PATH_CEROS, TAMANO_CEROS)  # Fuente más pequeña para los ceros
    date_font = ImageFont.truetype(DATE_FONT_PATH, 21)  # Fuente para la fecha
    color_numero_valor = (0, 0, 0)  # Color negro para el número y el valor
    color_fecha = (62, 62, 62, 255)  # Color gris para la fecha

    numero_pos = (50, 970)
    valor_pos = (70, 555)
    fecha_pos = (180, 335)

    # Obtener la fecha y hora actual
    fecha_hora = obtener_fecha_hora()

    # Formatear el valor (por ejemplo 20000 -> 20.000,00)
    valor_formateado = formatear_valor(valor)

    # Formatear el número
    numero_formateado = formatear_numero(numero)

    # Dividir el valor en la parte entera y los ceros
    parte_entera, parte_decimal = valor_formateado.split(',')

    # Escribir el número
    draw.text(numero_pos, f"{numero_formateado}", font=font, fill=color_numero_valor)

    # Escribir la parte entera del valor
    draw.text(valor_pos, parte_entera, font=font_valor, fill=color_numero_valor)

    # Ajuste de la posición de los ceros para alinearlos
    # Desplazamos a la derecha de la parte entera del valor
    x_offset_ceros = valor_pos[0] + draw.textlength(parte_entera, font=font_valor) + 2  # Ajuste fino de los ceros
    y_offset_ceros = valor_pos[1] + 6  # Ajuste de la altura

    # Escribir ",00" con el ajuste
    draw.text((x_offset_ceros, y_offset_ceros), f",{parte_decimal}", font=small_font, fill=color_numero_valor)

    # Escribir la fecha
    draw.text(fecha_pos, f"{fecha_hora}", font=date_font, fill=color_fecha)

    # Guardar la imagen
    output_path = "comprobante.png"
    img.save(output_path)
    return output_path

# Función para generar comprobante con /c2
def generar_comprobante_c2(nombre: str, nequi: str, valor: str, font_size: int = 28) -> str:
    img = Image.open(TEMPLATE_PATH_C2)
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(FONT_PATH_C2, font_size)
    color = (0, 0, 0)  # Color negro para todo

    nombre_pos = (50, 300)
    nequi_pos = (50, 400)
    valor_pos = (50, 500)
    fecha_pos = (50, 600)

    # Obtener la fecha y hora actual
    fecha_hora = obtener_fecha_hora()

    draw.text(nombre_pos, f"{nombre.upper()}", font=font, fill=color)
    draw.text(nequi_pos, f"{nequi}", font=font, fill=color)
    draw.text(valor_pos, f"${valor},00", font=font, fill=color)
    draw.text(fecha_pos, f"{fecha_hora}", font=font, fill=color)

    # Guardar la imagen
    output_path = "comprobante_c2.png"
    img.save(output_path)
    return output_path

# Comando /c
async def comando_c(update: Update, context: CallbackContext) -> None:
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Formato incorrecto. Usa: /c [número] [valor]")
            return

        numero, valor = args

        if not valor.isdigit():
            await update.message.reply_text("El valor debe ser un número.")
            return

        comprobante_path = generar_comprobante(numero, valor)

        with open(comprobante_path, "rb") as img:
            await update.message.reply_photo(img, caption="Aquí está tu comprobante.")

    except Exception as e:
        await update.message.reply_text(f"Hubo un error: {e}")

# Comando /c2
async def comando_c2(update: Update, context: CallbackContext) -> None:
    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text("Formato incorrecto. Usa: /c2 [nombre personalizado] [nequi] [valor]")
            return

        nombre, nequi, valor = args

        if not valor.isdigit():
            await update.message.reply_text("El valor debe ser un número.")
            return

        comprobante_path = generar_comprobante_c2(nombre, nequi, valor)

        with open(comprobante_path, "rb") as img:
            await update.message.reply_photo(img, caption="Aquí está tu comprobante.")

    except Exception as e:
        await update.message.reply_text(f"Hubo un error: {e}")

# Comando /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("¡Hola! Usa los comandos /c o /c2 para generar un comprobante.")

# Función principal
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("c", comando_c))
    application.add_handler(CommandHandler("c2", comando_c2))
    application.run_polling()

if __name__ == "__main__":
    main()