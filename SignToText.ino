#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// CONFIGURACIÓN OLED (Steren ARD-384, SSD1306, 128x32, I2C)
#define SCREEN_WIDTH   128
#define SCREEN_HEIGHT  32
#define OLED_RESET     -1
#define SCREEN_ADDRESS 0x3C
//#define SCREEN_ADDRESS 0x3D

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

//VARIABLES
String letraActual   = "";
String letraAnterior = "";
unsigned long tiempoUltima = 0;
String palabraActual = "";

//SETUP
void setup() {
  Serial.begin(9600);

  delay(500);                 // esperar a que el OLED estabilice su alimentación antes de inicializar

  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println("Error: no se encontro el OLED");
    while (true) delay(1000);
  }

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  // Pantalla de bienvenida
  display.setTextSize(2);
  display.setCursor(10, 8);
  display.print("UNIPOLI");
  display.display();
  delay(2000);

  pantallaListo();
}

//LOOP
void loop() {

  // Leer letra enviada por Python
  if (Serial.available() > 0) {
    letraActual = Serial.readStringUntil('\n');
    letraActual.trim();

    if (letraActual.length() > 0 && letraActual != letraAnterior) {
      letraAnterior = letraActual;
      tiempoUltima  = millis();

      // Agregar a la palabra si es una letra válida
      if (letraActual != "?" && letraActual != "-") {
        palabraActual += letraActual;
        if (palabraActual.length() > 10) {
          palabraActual = palabraActual.substring(palabraActual.length() - 10);
        }
      }

      mostrarLetra(letraActual);
    }
  }

  // Si pasan 3 segundos sin nueva letra, limpiar "palabra en progreso"
  if (millis() - tiempoUltima > 3000 && palabraActual.length() > 0) {
    // Mostrar la palabra completa formada
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0, 0);
    display.print("Palabra:");
    display.setTextSize(2);
    display.setCursor(0, 14);
    display.print(palabraActual);
    display.display();
    delay(2000);

    // Reiniciar
    palabraActual  = "";
    letraAnterior  = "";
    pantallaListo();
  }
}

//FUNCIÓN: PANTALLA DE ESPERA
void pantallaListo() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print("Listo!");
  display.setCursor(0, 12);
  display.print("Muestra una sena");
  display.display();
}

//FUNCIÓN: MOSTRAR EN OLED
void mostrarLetra(String letra) {
  display.clearDisplay();

  // Fila superior: etiqueta + letra grande
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print("Letra:");
  display.setTextSize(2);
  display.setCursor(70, 0);
  display.print(letra);

  // Fila inferior: palabra en progreso
  display.setTextSize(1);
  display.setCursor(0, 22);
  display.print("[");
  display.print(palabraActual);
  display.print("]");

  display.display();
}
