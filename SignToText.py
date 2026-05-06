#librerias
import cv2
import mediapipe as mp
import serial
import time
import math

# Outputs
PUERTO_ARDUINO = "COM4"       
BAUD_RATE      = 9600
CAMARA_INDEX   = 0           

# Colores para OpenCV
COLOR_FONDO    = (15, 15, 25)
COLOR_ACENTO   = (0, 230, 255)
COLOR_VERDE    = (80, 230, 80)
COLOR_ROJO     = (60, 60, 220)
COLOR_LETRA    = (255, 255, 255)

# Iniciar mediapipe
mp_hands   = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_styles  = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6
)

# Iniciar Arduino
arduino = None
try:
    arduino = serial.Serial(PUERTO_ARDUINO, BAUD_RATE, timeout=1)
    time.sleep(2)  # esperar a que Arduino arranque
    print(f"Arduino conectado en {PUERTO_ARDUINO}")
except Exception as e:
    print(f"Sin Arduino ({e}) — solo se mostrará en pantalla")

# Auxiliares para detectar dedos
def esta_doblado(puntos, dedo_tip, dedo_pip):
    """Compara Y del tip vs PIP — si tip está más arriba (menor Y), está estirado"""
    return puntos[dedo_tip].y > puntos[dedo_pip].y

def angulo_entre(a, b, c):
    """Ángulo en el punto b, formado por los puntos a-b-c"""
    ang = math.degrees(
        math.atan2(c.y - b.y, c.x - b.x) -
        math.atan2(a.y - b.y, a.x - b.x)
    )
    return abs(ang) % 360

def pulgar_doblado(puntos, es_mano_derecha):
    """El pulgar es especial — compara en eje X"""
    tip = puntos[4]
    mcp = puntos[2]
    if es_mano_derecha:
        return tip.x > mcp.x
    else:
        return tip.x < mcp.x

def detectar_seña(puntos, es_mano_derecha):
    """
    Detecta la letra según la posición de los dedos.
    Devuelve (letra, descripción)
    """
    # Estado de cada dedo (True = doblado)
    # Índices MediaPipe: 8=índice_tip, 6=índice_pip, 12=medio_tip, etc.
    indice  = esta_doblado(puntos, 8,  6)
    medio   = esta_doblado(puntos, 12, 10)
    anular  = esta_doblado(puntos, 16, 14)
    menique = esta_doblado(puntos, 20, 18)
    pulgar  = pulgar_doblado(puntos, es_mano_derecha)

    # True = doblado, False = estirado
    patron = (pulgar, indice, medio, anular, menique)

    # Diccionario Temporal de prueba
    senas = {
        (True,  True,  True,  True,  True ): ("H", "Todos doblados"),
        (False, True,  True,  True,  True ): ("O", "Pulgar dentro, dedos arriba"),
        (True,  True,  True,  True,  False): ("L", "Puño con pulgar al lado"),
        (False, False, False, False, False): ("A", "Mano abierta / C curva"),
        (True,  False, True,  True,  True ): ("M", "Índice arriba"),
        (False, False, True,  True,  True ): ("U", "Índice y pulgar tocándose"),
        (True,  False, False, True,  True ): ("N", "L: índice y pulgar"),
        (False, False, False, True,  False): ("D", "Índice y medio arriba"),
        (False, True,  True,  False, False): ("N", "Meñique y pulgar arriba"),
        (False, False, True,  True,  False): ("I", "Índice y medio juntos arriba"),
        (False, True,  False, False, False): ("P", "Índice apuntando al lado"),
        (True,  False, False, False, False): ("I", "Solo meñique arriba"),
        (True,  True,  False, False, False): ("X", "Tres dedos arriba"),
    }

    resultado = senas.get(patron)
    if resultado:
        return resultado
    return ("?", "No reconocida")


def mandar_a_arduino(letra):
    """Envía la letra al Arduino por serial"""
    if arduino and arduino.is_open:
        try:
            arduino.write((letra + "\n").encode())
        except Exception as e:
            print(f"Error serial: {e}")


def dibujar_ui(frame, letra, descripcion, confianza, fps):
    """Dibuja la interfaz visual sobre el frame"""
    h, w = frame.shape[:2]

    # Panel izquierdo oscuro
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (220, h), (10, 12, 20), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

    # Título
    cv2.putText(frame, "GUANTE", (12, 40),
                cv2.FONT_HERSHEY_DUPLEX, 0.9, COLOR_ACENTO, 2)
    cv2.putText(frame, "DE SENAS", (12, 66),
                cv2.FONT_HERSHEY_DUPLEX, 0.9, COLOR_ACENTO, 2)

    # Línea separadora
    cv2.line(frame, (12, 80), (208, 80), COLOR_ACENTO, 1)

    # Letra grande detectada
    cv2.putText(frame, letra, (55, 175),
                cv2.FONT_HERSHEY_DUPLEX, 5.5, COLOR_LETRA, 8)
    cv2.putText(frame, letra, (55, 175),
                cv2.FONT_HERSHEY_DUPLEX, 5.5, COLOR_ACENTO, 3)

    # Descripción
    cv2.putText(frame, descripcion[:18], (10, 210),
                cv2.FONT_HERSHEY_PLAIN, 1.0, (160, 160, 160), 1)

    # FPS
    cv2.putText(frame, f"FPS: {fps:.0f}", (10, h - 40),
                cv2.FONT_HERSHEY_PLAIN, 1.0, (80, 80, 80), 1)

    # Estado Arduino
    estado_txt = "Arduino: OK" if arduino else "Arduino: OFF"
    estado_col = COLOR_VERDE if arduino else COLOR_ROJO
    cv2.putText(frame, estado_txt, (10, h - 20),
                cv2.FONT_HERSHEY_PLAIN, 1.0, estado_col, 1)

    # Borde acento izquierdo
    cv2.line(frame, (0, 0), (0, h), COLOR_ACENTO, 3)


#LOOP PRINCIPAL 
def main():
    cap = cv2.VideoCapture(CAMARA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    letra_anterior  = ""
    tiempo_anterior = time.time()
    fps             = 0

    print("Iniciando detección... presiona Q para salir")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Error: no se puede leer la cámara")
            break

        # Calcular FPS
        ahora = time.time()
        fps = 1.0 / (ahora - tiempo_anterior + 0.001)
        tiempo_anterior = ahora

        # Voltear horizontalmente (efecto espejo)
        frame = cv2.flip(frame, 1)
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Procesar mano
        resultado = hands.process(rgb)

        letra      = "-"
        descripcion = "Sin mano detectada"

        if resultado.multi_hand_landmarks:
            for hand_landmarks, hand_info in zip(
                resultado.multi_hand_landmarks,
                resultado.multi_handedness
            ):
                # Dibujar esqueleto de la mano
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_styles.get_default_hand_landmarks_style(),
                    mp_styles.get_default_hand_connections_style()
                )

                # Detectar seña
                puntos         = hand_landmarks.landmark
                es_derecha     = hand_info.classification[0].label == "Right"
                letra, descripcion = detectar_seña(puntos, es_derecha)

                # Mandar a Arduino solo si cambió la letra
                if letra != letra_anterior and letra != "?":
                    mandar_a_arduino(letra)
                    letra_anterior = letra
                    print(f"→ Letra detectada: {letra}")

        # Dibujar interfaz
        dibujar_ui(frame, letra, descripcion, 0, fps)

        cv2.imshow("Guante de Lenguaje de Senas", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    if arduino:
        arduino.close()
    print("Programa terminado.")


if __name__ == "__main__":
    main()
