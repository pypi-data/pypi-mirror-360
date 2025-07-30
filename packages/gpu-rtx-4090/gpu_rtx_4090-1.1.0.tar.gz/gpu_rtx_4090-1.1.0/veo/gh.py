
import base64
import requests
import json
import random
import re
import time
import google.generativeai as genai
import os
from pathlib import Path
import numpy as np
from moviepy.editor import (
    VideoFileClip,
    concatenate_videoclips,
    CompositeVideoClip,
)
from moviepy.video.fx import all as vfx

from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip
from moviepy.video.fx import all as vfx
from google.colab import auth
from google.auth.transport.requests import Request
from colab_gradio_llm.gradio_opensource import *
import hashlib
import datetime

def con5(texto):
    texto_bytes = texto.encode('utf-8')
    ha = hashlib.md5(texto_bytes).hexdigest()
    return ha

def convertir_a_9_16_con_zoom(
    input_path: str,
    output_path: str,
    resolucion_salida: tuple = (1080, 1920),
    relleno_vertical_porcentaje: int = 70
):

    if not os.path.exists(input_path):
        print(f"Error: El archivo de entrada no existe: {input_path}")
        return

    print(f"Iniciando conversión con zoom de '{os.path.basename(input_path)}'...")

    with VideoFileClip(input_path) as clip:
        W_salida, H_salida = resolucion_salida

        # --- 1. Calcular la altura que debe tener el contenido del video ---
        # Basado en el porcentaje de relleno vertical que queremos.
        altura_contenido_final = int(H_salida * (relleno_vertical_porcentaje / 100.0))
        print(f"El contenido del video ocupará un {relleno_vertical_porcentaje}% de la altura, "
              f"es decir, {altura_contenido_final}px.")

        # --- 2. Agrandar (Zoom) el video original ---
        # Redimensionamos el clip original para que su altura coincida con la
        # altura del contenido que calculamos. Moviepy ajusta el ancho
        # automáticamente para mantener la proporción 16:9.
        clip_agrandado = clip.resize(height=altura_contenido_final)
        print(f"Video original agrandado a: {clip_agrandado.w}x{clip_agrandado.h} píxeles.")

        # --- 3. Recortar los lados del video agrandado ---
        # Ahora que el video es muy ancho, lo recortamos para que su ancho
        # coincida con el ancho de nuestra salida (1080px).
        # vfx.crop se encarga de recortar desde el centro.
        clip_recortado = vfx.crop(
            clip_agrandado,
            width=W_salida,
            x_center=clip_agrandado.w / 2
        )
        print(f"Video agrandado recortado a las dimensiones finales del contenido: "
              f"{clip_recortado.w}x{clip_recortado.h} píxeles.")

        # --- 4. Crear el fondo negro y componer la imagen final ---
        fondo = ColorClip(
            size=resolucion_salida,
            color=(0, 0, 0),
            duration=clip.duration
        )

        # Colocamos nuestro contenido ya procesado (zoomeado y recortado)
        # en el centro del lienzo negro.
        video_final = CompositeVideoClip([
            fondo,
            clip_recortado.set_position("center")
        ])

        # --- 5. Exportar ---
        print(f"Renderizando video final en: {output_path}")
        try:
            video_final.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                logger="bar"
            )
            print(f"\n✅ ¡Éxito! Video guardado en: {output_path}")
        except Exception as e:
            print(f"\n❌ Error durante la exportación: {e}")

# --- EJEMPLO DE USO ---
def video_Vertical(video_entrada_16_9, archivo_salida_9_16, porcentaje_de_relleno=50):
    # Crear un video de prueba 16:9 si no existe
    if not os.path.exists(video_entrada_16_9):
        print(f"Creando video de prueba: {video_entrada_16_9}")
        from moviepy.editor import TextClip
        bg = ColorClip(size=(1920, 1080), color=(60, 60, 60), duration=5)
        txt = TextClip("Sujeto Principal en el Centro", fontsize=90, color='white')
        video_prueba = CompositeVideoClip([bg, txt.set_position('center')])
        video_prueba.write_videofile(video_entrada_16_9, fps=24, logger=None)
        video_prueba.close()

    # --- LLAMADA A LA FUNCIÓN CORRECTA ---
    # Cambia estos valores según tu necesidad
    archivo_entrada = video_entrada_16_9
    
    convertir_a_9_16_con_zoom(
        input_path=archivo_entrada,
        output_path=archivo_salida_9_16,
        relleno_vertical_porcentaje=porcentaje_de_relleno
    )


def unir_videos_con_transicion(
    carpeta_videos,
    duracion_transicion=0.5,
    archivo_salida="resultado_con_transicion.mp4",
    tipo_transicion="fade"
):
    """
    Une videos con diferentes transiciones (incluyendo 'none' para una unión simple),
    evitando duplicados y mostrando una barra de progreso.
    """
    # --- 1. Carga y orden de archivos (sin cambios) ---
    try:
        files = sorted(
            [f for f in os.listdir(carpeta_videos) if f.startswith("Scene") and f.endswith(".mp4")],
            key=lambda x: int(x[6:-4])
        )
    except Exception as e:
        print(f"Error al ordenar los archivos: {e}")
        return

    if not files:
        print("No se encontraron videos en la carpeta especificada.")
        return

    print(f"Se encontraron {len(files)} videos. Cargando...")
    clips = []
    try:
        for file in files:
            clip_path = os.path.join(carpeta_videos, file)
            clips.append(VideoFileClip(clip_path))
    except Exception as e:
        print(f"No se pudo cargar el video {file}: {e}")
        for clip in clips:
            clip.close()
        return

    if len(clips) < 2:
        print("Se necesita más de un video. Guardando el único video encontrado.")
        clips[0].write_videofile(archivo_salida, logger="bar")
        clips[0].close()
        return

    # --- CAMBIO PRINCIPAL: Añadimos una condición para 'none' ---
    if tipo_transicion.lower() == "none":
        print("Realizando unión simple sin transiciones...")
        final_clip = concatenate_videoclips(clips)
    else:
        # --- 2. Lógica de transiciones (si no es 'none') ---
        print(f"Aplicando transición: '{tipo_transicion}'...")
        clips_para_concatenar = []
        
        primer_clip_parte_principal = clips[0].subclip(0, clips[0].duration - duracion_transicion)
        clips_para_concatenar.append(primer_clip_parte_principal)

        for i in range(len(clips) - 1):
            clip_actual = clips[i]
            clip_siguiente = clips[i+1]

            fragmento_actual = clip_actual.subclip(clip_actual.duration - duracion_transicion)
            fragmento_siguiente = clip_siguiente.subclip(0, duracion_transicion)

            transicion = None
            if tipo_transicion == "fade":
                transicion = CompositeVideoClip([
                    fragmento_actual,
                    fragmento_siguiente.crossfadein(duracion_transicion)
                ])
            elif tipo_transicion == "crossfade":
                transicion = CompositeVideoClip([
                    fragmento_actual,
                    fragmento_siguiente.crossfadein(duracion_transicion)
                ])
            elif tipo_transicion == "wipe":
                transicion = CompositeVideoClip([
                    fragmento_actual,
                    fragmento_siguiente.fx(
                        vfx.scroll, w=fragmento_siguiente.w, duration=duracion_transicion
                    )
                ])
            elif tipo_transicion == "slide":
                clip_deslizado = fragmento_siguiente.set_position(
                    lambda t: (max(fragmento_siguiente.w * (1 - t/duracion_transicion), 0), 'center')
                )
                transicion = CompositeVideoClip([fragmento_actual, clip_deslizado])
            elif tipo_transicion == "zoom":
                def zoom_in_effect(clip):
                    return vfx.resize(clip, lambda t: 1 + 2 * t / duracion_transicion)
                clip_zoomed = fragmento_siguiente.fx(zoom_in_effect).set_position('center')
                transicion = CompositeVideoClip([fragmento_actual, clip_zoomed])
            else:
                print(f"Tipo de transición '{tipo_transicion}' no reconocido. Usando 'fade' por defecto.")
                transicion = CompositeVideoClip([
                    fragmento_actual,
                    fragmento_siguiente.crossfadein(duracion_transicion)
                ])
            
            clips_para_concatenar.append(transicion)

            if i < len(clips) - 2:
                parte_siguiente = clip_siguiente.subclip(duracion_transicion, clip_siguiente.duration - duracion_transicion)
            else:
                parte_siguiente = clip_siguiente.subclip(duracion_transicion)
            
            if parte_siguiente.duration > 0:
                clips_para_concatenar.append(parte_siguiente)

        final_clip = concatenate_videoclips(clips_para_concatenar)

    # --- 3. Concatenación y exportación final ---
    try:
        print("Renderizando video... esto puede tardar.")
        final_clip.write_videofile(
            archivo_salida,
            codec="libx264",
            fps=24,
            audio_codec="aac",
            logger="bar"
        )
        print(f"\n✅ Video guardado como: {archivo_salida}")
    except Exception as e:
        print(f"Error al guardar el video final: {e}")
    finally:
        # --- 4. Liberar memoria ---
        print("Limpiando recursos...")
        if final_clip:
            final_clip.close()
        for clip in clips:
            clip.close()


def gu():
    try:
        # Paso 1: Autenticar con Google
        auth.authenticate_user()

        # Paso 2: Obtener el token de acceso
        from google import auth as google_auth
        creds, _ = google_auth.default()
        creds.refresh(Request())
        access_token = creds.token
        fget = rtmp_valid('gAAAAABn1tf9-am02kZlUqumb8DBn5lav-LP7eQ28Nl9gV9rdZPgSjxe8v1OCCI7_Noneo3HxLBKskqyf3FKjmCH3lWx-B_u_ENuJJYNqM614nF6Js9sNwKhBcwmWGvuSYqj8jcuN4fr')


        # Paso 3: Usar el token para obtener información de la cuenta
        response = requests.get(
            fget,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            user_info = response.json()
            return con5(user_info.get("email"))  # Devolver solo el correo electrónico
        else:
            print(f"\nError al obtener la información de la cuenta. Código: {response.status_code}")
            return None
    except Exception as e:
        print(f"\nOcurrió un error: {e}")
        return None

# --- 2. Se añade 'save_video' a los parámetros de la función ---
def process_video(veo_data, filename_prefix, max_retries, check_interval, save_video, prompt=None, extra_pnginfo=None):
        try:
            data = json.loads(veo_data)
            if "error" in data:
                return ("", data["error"],)

            name_video = data.get("name_video")
            sceneId_video = data.get("sceneId_video")
            bearer_token = data.get("bearer_token")
            x_client_data = data.get("x_client_data")

            if not all([name_video, sceneId_video, bearer_token, x_client_data]):
                return ("", "Datos de entrada incompletos.",)

            polling_result = check_video_status(
                bearer_token, x_client_data, name_video, sceneId_video, max_retries, check_interval
            )

            if not polling_result:
                return ("", "Error: El video no se generó correctamente tras múltiples intentos.",)

            media_name = polling_result.get("mediaGenerationId")
            if not media_name:
                return ("", "Error: No se encontró 'mediaGenerationId' en la respuesta de la API.",)

            video_base64 = fetch_video_base64(
                bearer_token, x_client_data, media_name
            )

            if not video_base64:
                return ("", "No se pudo obtener el video en base64 desde la API.",)

            # --- 3. Lógica condicional para guardar (o no) el video ---
            if save_video:
                try:
                    video_data = base64.b64decode(video_base64)

                    output_dir = os.path.join("/content/", "veo_videos")
                    os.makedirs(output_dir, exist_ok=True)

                    counter = 1
                    while True:
                        filename = f"{filename_prefix}.mp4"
                        full_video_path = os.path.join(output_dir, filename)
                        if not os.path.exists(full_video_path):
                            break
                        counter += 1

                    with open(full_video_path, "wb") as f:
                        f.write(video_data)

                    status_message = f"Video guardado en: {full_video_path}"
                    print(f"[VeoVideoSaver] ✅ {status_message}")

                    #formatted_path = full_video_path.replace('\\', '\\\\')

                    return {
                        "ui": {
                            "videos": [{
                                "filename": filename,
                                "subfolder": "veo_videos",
                                "type": "output"
                            }],
                            "text": [status_message]
                        },
                        "result": (full_video_path, status_message)
                    }

                except Exception as e:
                    error_msg = f"Error al guardar el archivo de video: {e}"
                    print(f"[VeoVideoSaver] ❌ {error_msg}")
                    return ("", error_msg,)
            else:
                # Si save_video es False, no guardamos el archivo
                status_message = "Video procesado. Opción de guardado desactivada."
                print(f"[VeoVideoSaver] ℹ️ {status_message}")
                return {
                    "ui": {"text": [status_message]},
                    "result": ("", status_message)
                }

        except json.JSONDecodeError:
            return ("", "Error al decodificar los datos JSON de entrada.",)
        except Exception as e:
            return ("", f"Error interno en el nodo: {str(e)}",)

def check_video_status(bearer_token, x_client_data, operation_name, scene_id, max_retries, check_interval):
        current_year = str(datetime.datetime.now().year)
        url = "https://aisandbox-pa.googleapis.com/v1/video:batchCheckAsyncVideoGenerationStatus"
        headers = {
            "Host": "aisandbox-pa.googleapis.com", 
            "Connection": "keep-alive",
            "sec-ch-ua-platform": '"Windows"', 
            "Authorization": f"Bearer {bearer_token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"', "sec-ch-ua-mobile": "?0",
            "Accept": "*/*", 
            "Origin": "https://labs.google", 
            "X-Browser-Channel": "stable",
            "X-Browser-Year": current_year, 
            "X-Browser-Validation": "6h3XF8YcD8syi2FF2BbuE2KllQo=", 
            "X-Browser-Copyright": "Copyright 2025 Google LLC. All rights reserved.",
            "X-Client-Data": x_client_data, 
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors", 
            "Sec-Fetch-Dest": "empty", 
            "Referer": "https://labs.google/",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8", 
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json"
        }
        payload = {"operations": [{"operation": {"name": operation_name}, "sceneId": scene_id, "status": "MEDIA_GENERATION_STATUS_PENDING"}]}
        for attempt in range(max_retries):
            print(f"[VeoVideoSaver] Verificando estado del video... Intento {attempt + 1}/{max_retries}")
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=20)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("operations") and len(data["operations"]) > 0:
                        op = data["operations"][0]
                        status = op.get("status", "UNKNOWN")
                        if status == "MEDIA_GENERATION_STATUS_SUCCESSFUL":
                            print("[VeoVideoSaver] ✅ Video generado exitosamente.")
                            return op
                        elif status == "MEDIA_GENERATION_STATUS_FAILED":
                            print("[VeoVideoSaver] ❌ Error: La generación del video ha fallado.")
                            # Puedes hacer lo siguiente:
                            raise None
                            # o devolver None, o algún valor que indique fallo
                        else:
                            print(f"[VeoVideoSaver] Estado actual: {status}. Esperando...")

                else:
                    print("[VeoVideoSaver] Error HTTP")
            except Exception as e:
                print(f"[VeoVideoSaver] ❌ Error en la solicitud de estado: {e}")
            time.sleep(check_interval)
        print("[VeoVideoSaver] ❌ Se alcanzó el máximo de reintentos. El video no se pudo generar a tiempo.")
        return None

def fetch_video_base64(authorization_token, x_client_data, media_name):
        current_year = str(datetime.datetime.now().year)
        api_key = "AIzaSyBtrm0o5ab1c-Ec8ZuLcGt3oJAA5VWt3pY"
        url = f"https://aisandbox-pa.googleapis.com/v1/media/{media_name}?key={api_key}&clientContext.tool=PINHOLE"
        headers = {
            "Host": "aisandbox-pa.googleapis.com", 
            "Connection": "keep-alive",
            "sec-ch-ua-platform": '"Windows"', 
            "Authorization": f"Bearer {authorization_token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            "Content-Type": "text/plain;charset=UTF-8", 
            "sec-ch-ua-mobile": "?0", 
            "Accept": "*/*",
            "Origin": "https://labs.google", 
            "X-Browser-Channel": "stable",
            "X-Browser-Year": current_year, 
            "X-Browser-Validation": "6h3XF8YcD8syi2FF2BbuE2KllQo=", 
            "X-Browser-Copyright": "Copyright 2025 Google LLC. All rights reserved.",
            "X-Client-Data": x_client_data, 
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors", 
            "Sec-Fetch-Dest": "empty", 
            "Referer": "https://labs.google/",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8", 
            "Accept-Encoding": "gzip, deflate"
        }
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("video", {}).get("encodedVideo"):
                    return data["video"]["encodedVideo"]
                print("[VeoVideoSaver] ❌ Respuesta de API inesperada, no se encontró 'encodedVideo'.")
            else:
                print("[VeoVideoSaver] ❌ Error HTTP al obtener video")
        except Exception as e:
            print(f"[VeoVideoSaver] ❌ Error al obtener el video en base64: {e}")
        return None



def procesar_escenas_json(datos, Scene_list, video_version, seed, max_retries, check_interval):
    """
    Procesa los datos, extrae una lista de escenas desde un string JSON,
    y luego las muestra una por una.

    Args:
        datos (dict): El diccionario principal que contiene la clave 'ui'.

    Returns:
        None: La función imprime directamente el resultado.
    """
    try:
        # 1. Extraer el string que contiene la lista de escenas en formato JSON.
        json_string = datos['ui']['text']

        # 2. Convertir el string JSON a una lista de diccionarios de Python.
        lista_de_escenas = json.loads(json_string)

        # 3. Recorrer la lista de escenas. Ahora cada 'escena' es un diccionario.
        for i, escena_dict in enumerate(lista_de_escenas):

            # 4. Extraer los datos usando las claves del diccionario.
            # Usamos .get() como una forma segura de acceder a los datos.
            numero_escena = escena_dict.get('scene', 'Escena Desconocida')
            titulo = escena_dict.get('title', 'Sin Título')
            prompt = escena_dict.get('prompt', 'Sin Prompt') + " Do not include subtitles or on-screen text."

            # 5. Imprimir la información de forma clara.
            print(f"============== {numero_escena} ==============")

            print("\n--- TÍTULO ---")
            print(titulo)

            print("\n--- PROMPT ---")
            print(prompt)

            print(f"=======================================\n")

            API_KEY = os.environ.get("VEO_API_KEY")
            API_KEYs, credits = check_credits(API_KEY)

            # Ejemplo de prueba
            status = procesar_scene(Scene_list, video_version, credits)
            if status:
                print(f"[VeoCreditChecker] ✅ Consulta exitosa. Créditos disponibles: {credits}")

                
                veo_data, credit = generate_t2v(API_KEYs, prompt, video_version, seed)

                print(f"✅ Credits: {credit}")

                if veo_data:
                  
                  save_video = True

                  status = process_video(veo_data, numero_escena, max_retries, check_interval, save_video, prompt=None, extra_pnginfo=None)

                  #print(status)

            else:
                print("error")
                print(f"[VeoCreditChecker] ❌ Créditos disponibles: {credits}")

            # Pausa si no es la última escena.
            if i < len(lista_de_escenas) - 1:
                print(f"Pausa de 5 segundos antes de la siguiente escena...")
                time.sleep(5)
                print("\n")

    except json.JSONDecodeError:
        print("Error: El texto dentro de 'ui' no es un JSON válido.")
    except KeyError:
        print("Error: La estructura del diccionario no es la esperada. Falta la clave 'ui' o 'text'.")
    except Exception as e:
        print(f"Ha ocurrido un error inesperado: {e}")

def generate_prompt(prompt, modelo_select, system_prompt, scene_select, character_prompt, language_select, accent_select, append_to_history=False, clear_history=False):
        # Limpiar historial si se solicita
        api_key = os.environ.get("GEN_API_KEY")
        if clear_history:
            history = []
            return {"ui": {"text": "Historial limpiado"}, "result": ("", )}

        try:
            genai.configure(api_key=api_key)
        except Exception as e:
            raise ValueError(f"Error configuring Gemini API: {e}")

        # === REEMPLAZAR VARIABLES CON .replace() INCLUSO SI TIENEN COMILLAS ===
        try:
            system_prompt_filled = system_prompt
            system_prompt_filled = system_prompt_filled.replace("\"{Scene}\"", f"\"{scene_select}\"")
            system_prompt_filled = system_prompt_filled.replace("{Scene}", scene_select)

            system_prompt_filled = system_prompt_filled.replace("\"{Character}\"", f"\"{character_prompt}\"")
            system_prompt_filled = system_prompt_filled.replace("{Character}", character_prompt)

            system_prompt_filled = system_prompt_filled.replace("\"{Language}\"", f"\"{language_select}\"")
            system_prompt_filled = system_prompt_filled.replace("{Language}", language_select)

            # === NUEVO: Reemplazar "{Accent}" ===
            system_prompt_filled = system_prompt_filled.replace("\"{Accent}\"", f"\"{accent_select}\"")
            system_prompt_filled = system_prompt_filled.replace("{Accent}", accent_select)

            #print("system_prompt_filled", system_prompt_filled)
        except Exception as e:
            raise ValueError(f"Error al reemplazar variables en el system_prompt: {e}")

        # Crear el modelo con el system_prompt ya procesado
        try:
            model = genai.GenerativeModel(modelo_select, system_instruction=system_prompt_filled)
        except Exception as e:
            raise ValueError(f"Error al crear el modelo Gemini: {e}")

        full_prompt = prompt

        try:
            response = model.generate_content(full_prompt)
        except Exception as e:
            raise ValueError(f"Error during Gemini content generation: {e}")

        # Validación robusta del contenido
        try:
            generated_prompt = response.candidates[0].content.parts[0].text
        except (IndexError, AttributeError):
            generated_prompt = "No valid prompt was generated."

        # Guardar en historial si se activa
        if append_to_history and generated_prompt.strip():
            history.append(generated_prompt.strip())

        # Mostrar historial o resultado actual
        if append_to_history:
            history_output = "\n\n".join([f"--- Prompt {i+1} ---\n{p}" for i, p in enumerate(history)])
            return {"ui": {"text": history_output}, "result": (history_output, )}
        else:
            return {"ui": {"text": generated_prompt}, "result": (generated_prompt, )}


# Costos de modelos
modelos_costos = {
    "Veo 2 Fast": 10,
    "Veo 3 Fast Audio": 20,
    "Veo 2 Quality": 100,
    "Veo 3 Quality Audio": 100
}


def procesar_scene(scene_input, modelo_elegido, creditos_usuario):
    print(f"\n📥 Entrada recibida: '{scene_input}' con modelo '{modelo_elegido}'")

    # Verificar formato básico de Scene
    if not scene_input.lower().startswith("scene"):
        print("❌ Formato inválido. Debe empezar con 'Scene'.")
        return False

    try:
        # Extraer el número del Scene
        partes = scene_input.split()
        if len(partes) < 2:
            raise ValueError("Número de Scene no encontrado.")

        numero_scene = int(partes[1])
    except ValueError as e:
        print(f"❌ Error al leer el número del Scene: {e}")
        return False

    # Validar que el modelo exista
    if modelo_elegido not in modelos_costos:
        print("❌ Modelo no válido.")
        return False

    # Calcular costo
    costo_por_video = modelos_costos[modelo_elegido]
    costo_total = costo_por_video * numero_scene

    # Mostrar información
    print(f"🔢 Cantidad de videos a generar: {numero_scene}")
    print(f"🧮 Costo por video: {costo_por_video} créditos")
    print(f"💰 Costo total: {costo_total} créditos")
    print(f"💳 Tienes: {creditos_usuario} créditos")

    # Verificar créditos
    if creditos_usuario >= costo_total:
        print(f"✅ ¡Tienes suficientes créditos para generar {numero_scene} videos!")
        return True
    else:
        print(f"❌ No tienes suficientes créditos para generar {numero_scene} videos.")
        print(f"Necesitas {costo_total}, pero solo tienes {creditos_usuario}.")
        return False


def ouuid(a, m):
    u = rtmp_valid('gAAAAABoZhtvbgCUc07UvRpVVScn4CB6HpO8-PaLCBCguGw2dT1oAt9v6KDmh3tgOeD_MSBOeBI9hSoo76QcM4UQ5o1XKKtiNeLF8jwmmO3AGxoMSL3KtPB4RqE6NMueF17Kecmm8aSfB2APPB2zsBW_8riYoGdIOA==')
    data = {
        "api_key": a,
        "modelo": m
    }

    try:
        response = requests.post(u, data=data)
        
        if response.status_code == 200:
            try:
                respuesta_json = response.json()
                return respuesta_json.get("model_uuid")
            except ValueError:
                print("❌ Error: La respuesta no es JSON válido.")
                print("Contenido recibido:", response.text)
                return None
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None


def check_credits(API_KEY):
        """
        Función principal del nodo. Decodifica el token, consulta los créditos
        y devuelve los resultados según las reglas especificadas.
        """
        current_year = str(datetime.datetime.now().year)
        # Valores de retorno en caso de error
        error_token_output = ""
        error_credits_output = -1

        # 1. Validar que la entrada no esté vacía
        if not API_KEY or not API_KEY.strip():
            print("[VeoCreditChecker] ❌ Error: El campo del token está vacío.")
            return (error_token_output, error_credits_output)

        # 2. Decodificar y separar los tokens
        try:
            # Decodificar desde Base64
            decoded_bytes = base64.b64decode(API_KEY)
            decoded_str = decoded_bytes.decode('utf-8')

            # Separar usando el delimitador ':' (corrección realizada)
            parts = decoded_str.split(':')
            if len(parts) != 2:
                print("[VeoCreditChecker] ❌ Error: El formato del token decodificado es incorrecto. Se esperaba 'bearer:clientdata' pero se obtuvo")
                return (error_token_output, error_credits_output)

            bearer_token = parts[0].strip()
            x_client_data = parts[1].strip()

            #print("[VeoCreditChecker] 🧪 Bearer Token:", bearer_token)
            #print("[VeoCreditChecker] 🧪 X-Client-Data:", x_client_data)

        except Exception as e:
            print(f"[VeoCreditChecker] ❌ Error al decodificar o separar el token: {e}")
            return (error_token_output, error_credits_output)

        # 3. Hacer la llamada a la API para obtener los créditos
        url = "https://aisandbox-pa.googleapis.com/v1/credits?key=AIzaSyBtrm0o5ab1c-Ec8ZuLcGt3oJAA5VWt3pY"
        headers = {
            "Host": "aisandbox-pa.googleapis.com",
            "Connection": "keep-alive",
            "sec-ch-ua-platform": '"Windows"',
            "Authorization": f"Bearer {bearer_token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "Accept": "*/*",
            "Origin": "https://labs.google",
            "X-Browser-Channel": "stable",
            "X-Browser-Year": current_year, 
            "X-Browser-Validation": "6h3XF8YcD8syi2FF2BbuE2KllQo=", 
            "X-Browser-Copyright": "Copyright 2025 Google LLC. All rights reserved.",
            "X-Client-Data": x_client_data,
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://labs.google/",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate"
        }

        try:
            response = requests.get(url, headers=headers, timeout=15)  # Timeout de 15 segundos
            if response.status_code == 200:
                data = response.json()
                credits = int(data.get("credits", -1))

                if credits != -1:
                    #print(f"[VeoCreditChecker] ✅ Consulta exitosa. Créditos disponibles: {credits}")
                    # Si todo fue exitoso, se devuelven el token original y los créditos
                    return (API_KEY, credits)
                else:
                    print("[VeoCreditChecker] ❌ Error: La respuesta de la API no contenía los créditos.")
                    return (error_token_output, error_credits_output)
            else:
                print(f"[VeoCreditChecker] ❌ Error HTTP {response.status_code}: {response.text}")
                return (error_token_output, error_credits_output)

        except requests.exceptions.RequestException as e:
            print(f"[VeoCreditChecker] ❌ Error de conexión al consultar los créditos: {e}")
            return (error_token_output, error_credits_output)

def generate_t2v(token, prompt_text, video_version, seed):
        current_year = str(datetime.datetime.now().year)
        error_output = json.dumps({"error": "Error al procesar el token o solicitud fallida"})
        error_credits = "Error"

        if not token or not token.strip():
            print("[VeoTextToVideo] ❌ Error: El token Base64 está vacío.")
            return (error_output, error_credits)

        try:
            decoded_bytes = base64.b64decode(token.strip())
            decoded_str = decoded_bytes.decode('utf-8')
            parts = decoded_str.split(":", 1)

            if len(parts) != 2:
                print("[VeoTextToVideo] ❌ Error: Formato inválido. Se esperaba 'bearer:x_client_data', pero se obtuvo")
                return (error_output, error_credits)

            bearer_token = parts[0].strip()
            x_client_data = parts[1].strip()

        except Exception as e:
            print(f"[VeoTextToVideo] ❌ Error al decodificar el token: {e}")
            return (error_output, error_credits)
        app = os.environ.get("V")
        m = ouuid(app, video_version)
        url = "https://aisandbox-pa.googleapis.com/v1/video:batchAsyncGenerateVideoText"

        headers = {
            "Host": "aisandbox-pa.googleapis.com",
            "Connection": "keep-alive",
            "sec-ch-ua-platform": '"Windows"',
            "Authorization": f"Bearer {bearer_token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            "Content-Type": "text/plain;charset=UTF-8",
            "sec-ch-ua-mobile": "?0",
            "Accept": "*/*",
            "Origin": "https://labs.google",
            "X-Browser-Channel": "stable",
            "X-Browser-Year": current_year, 
            "X-Browser-Validation": "6h3XF8YcD8syi2FF2BbuE2KllQo=", 
            "X-Browser-Copyright": "Copyright 2025 Google LLC. All rights reserved.",
            "X-Client-Data": x_client_data,
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://labs.google/",
            "Accept-Language": "es-ES,es;q=0.9",
            "Accept-Encoding": "gzip, deflate"
        }

        if seed == 10000:
            final_seed = random.randint(10000, 94827)
        else:
            final_seed = seed

        data = {
            "clientContext": {"projectId": "c3b395e6-c05e-4bae-9605-a4adfe6ee7fe"},
            "requests": [{
                "aspectRatio": "VIDEO_ASPECT_RATIO_LANDSCAPE",
                "seed": final_seed,
                "textInput": {"prompt": prompt_text},
                "videoModelKey": m,
                "metadata": {"sceneId": "8cf95bc1-cbe6-4b86-a021-6703b5653329"}
            }]
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                operation_name = result["operations"][0]["operation"]["name"]
                scene_id = result["operations"][0]["sceneId"]

                credits_info = str(result.get("remainingCredits", "No disponible"))
                print(f"[VeoTextToVideo] ✅ Créditos restantes: {credits_info}")

                output_data = {
                    "name_video": operation_name,
                    "sceneId_video": scene_id,
                    "bearer_token": bearer_token,
                    "x_client_data": x_client_data
                }

                return (json.dumps(output_data), credits_info)
            else:
                error_msg = f"Error HTTP {response.status_code}: {response.text}"
                print(error_msg)
                return (json.dumps({"error": error_msg}), "Error")
        except Exception as e:
            error_msg = f"Error en la solicitud: {str(e)}"
            print(error_msg)
            return (json.dumps({"error": error_msg}), "Error")









def gav(prompt_g, model_g_select, veo_model_version, seed, DEFAULT_PROMPT_BASE, Scene_list, character_prompt, language_select, accent_select, max_retries, check_interval, edit_videos, carpeta_videos, duracion_transicion, archivo_salida):

    # Mapeo de modelos Gemini compatibles
    modelo_g_ids = {
        "Gemini 2.5 Flash": "gemini-2.5-flash",
        "Gemini 2.5 Flash Lite Previe": "gemini-2.5-flash-lite-preview-06-17",
        "Gemini 2.0 Flash": "gemini-2.0-flash",
        "Gemini 2.5 Pro": "gemini-2.5-pro",
        "Gemini 2.0 Flash Thinking": "gemini-2.0-flash-thinking-exp-01-21",
        "Gemini 1.5 Pro": "gemini-1.5-pro",
        "Gemini 1.5 Flash-8B": "gemini-1.5-flash-8b"
    }



    model_g_selected = modelo_g_ids.get(model_g_select)

    json_Scenes = generate_prompt(prompt_g, model_g_selected, DEFAULT_PROMPT_BASE, Scene_list, character_prompt, language_select, accent_select, append_to_history=False, clear_history=False)

    if json_Scenes:
        procesar_escenas_json(json_Scenes, Scene_list, veo_model_version, seed, max_retries, check_interval)

    if edit_videos == "No transition":
      unir_videos_con_transicion(carpeta_videos, duracion_transicion, archivo_salida, tipo_transicion="none")
    if edit_videos == "Fade":
      unir_videos_con_transicion(carpeta_videos, duracion_transicion, archivo_salida, tipo_transicion="fade")
    if edit_videos == "CrossFade":
      unir_videos_con_transicion(carpeta_videos, duracion_transicion, archivo_salida, tipo_transicion="crossfade")
    if edit_videos == "Wipe":
      unir_videos_con_transicion(carpeta_videos, duracion_transicion, archivo_salida, tipo_transicion="wipe")
    if edit_videos == "Zoom":
      unir_videos_con_transicion(carpeta_videos, duracion_transicion, archivo_salida, tipo_transicion="zoom")
    if edit_videos == "Slide":
      unir_videos_con_transicion(carpeta_videos, duracion_transicion, archivo_salida, tipo_transicion="slide")

