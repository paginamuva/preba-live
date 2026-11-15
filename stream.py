import os
import subprocess
import glob
import random
import time

# Configuración principal
STREAM_KEY = os.environ.get("YOUTUBE_STREAM_KEY")
YOUTUBE_RTMP = f"rtmp://a.rtmp.youtube.com/live2/{STREAM_KEY}"
IMAGE_PATH = "fondo.jpg"  # Imagen estática de fondo
MUSIC_FOLDER = "musica"   # Carpeta donde guardaste tus archivos .mp3
MAX_DURATION = 5 * 3600   # Duración exacta: 5 horas (18,000 segundos)

def get_playlist():
    """Busca los archivos MP3 en la carpeta, los mezcla y crea la lista para FFmpeg."""
    files = glob.glob(f"{MUSIC_FOLDER}/*.mp3")
    random.shuffle(files)
    with open("playlist.txt", "w", encoding="utf-8") as f:
        for file in files:
            safe_path = os.path.abspath(file).replace("'", "'\\''")
            f.write(f"file '{safe_path}'\n")
    return len(files)

def start_stream():
    if not STREAM_KEY:
        print("Error: La variable YOUTUBE_STREAM_KEY no está configurada en los Secrets.")
        return

    if not os.path.exists(IMAGE_PATH):
        print(f"Error: No se encontró la imagen '{IMAGE_PATH}' en el repositorio.")
        return

    start_time = time.time()
    print("Iniciando transmisión en YouTube por 5 horas exactas...")

    while time.time() - start_time < MAX_DURATION:
        track_count = get_playlist()
        if track_count == 0:
            print(f"Error: No se encontraron archivos .mp3 dentro de la carpeta '{MUSIC_FOLDER}'.")
            break

        # Tiempo restante para completar las 5 horas
        elapsed = time.time() - start_time
        remaining = MAX_DURATION - elapsed

        print(f"Reproduciendo {track_count} pistas. Tiempo restante: {int(remaining)} segundos.")

        # Comando FFmpeg actualizado con el filtro de video para corregir el error de dimensiones
        command = [
            "ffmpeg",
            "-re",
            "-loop", "1",
            "-framerate", "1",
            "-i", IMAGE_PATH,
            "-f", "concat",
            "-safe", "0",
            "-i", "playlist.txt",
            "-t", str(int(remaining)),
            "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2", # <-- Corrección de resolución automática
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-tune", "stillimage",
            "-b:v", "1500k",
            "-maxrate", "1500k",
            "-bufsize", "3000k",
            "-pix_fmt", "yuv420p",
            "-g", "2",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-f", "flv",
            YOUTUBE_RTMP
        ]

        try:
            subprocess.run(command, check=True)
            break
        except subprocess.CalledProcessError as e:
            print(f"Interrupción detectada ({e}). Reconectando en 5 segundos...")
            time.sleep(5)

    print("Transmisión de 5 horas finalizada correctamente.")

if __name__ == "__main__":
    start_stream()
