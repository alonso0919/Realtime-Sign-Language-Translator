# Sign Language to Text

Proyecto que traduce lenguaje de señas a texto en tiempo real usando Python y Arduino

Este sistema utiliza la cámara para detectar la mano interpreta la seña como una letra y la muestra en pantalla además la envía a un Arduino que despliega la información en una pantalla LCD y forma palabras automáticamente

Tecnologías utilizadas

Python con OpenCV MediaPipe y PySerial
Arduino con comunicación serial y pantalla LCD I2C

Funcionamiento

La cámara detecta la mano usando MediaPipe
Se analizan los puntos de la mano
Se identifica qué dedos están doblados o extendidos
Se compara con patrones para obtener una letra
La letra se envía a Arduino
Arduino muestra la letra y forma palabras automáticamente
Si no hay nuevas letras en unos segundos se reinicia la palabra

Estructura del proyecto

sign_to_text.py código principal en Python
arduino.ino código para Arduino
README.md documentación

Requisitos

Instalar en Python las librerías opencv python mediapipe pyserial

Se necesita Arduino compatible y pantalla LCD I2C

Uso

Conectar el Arduino a la computadora
Configurar el puerto en el archivo Python por ejemplo COM4
Subir el código al Arduino
Ejecutar el programa con python sign_to_text.py
Presionar Q para salir

Notas

El sistema funciona con reglas no es un modelo de inteligencia artificial entrenado
Funciona mejor con buena iluminación
Detecta solo una mano
Puede requerir ajustes dependiendo de la cámara

Autor

Alonso Sanchez

Licencia

Uso educativo