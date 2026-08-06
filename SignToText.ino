#include <Wire.h>
#include <LiquidCrystal_I2C.h>
//#include <hd44780.h>
//#include <hd44780ioClass/hd44780_I2Cexp.h>

// CONFIGURACIÓN LCD 
LiquidCrystal_I2C lcd(0x27, 16, 2);
//LiquidCrystal_I2C lcd(0x3F, 16, 2);

//VARIABLES
String letraActual   = "";
String letraAnterior = "";
unsigned long tiempoUltima = 0;
int contadorLetras = 0;           // para ir formando palabras
String palabraActual = "";

//CARACTERES PERSONALIZADOS (mano
byte iconoMano[8] = {
  0b00000,
  0b01010,
  0b11111,
  0b11111,
  0b01110,
  0b00100,
  0b00100,
  0b00000
};

//SETUP
void setup() {
  Serial.begin(9600);

  delay(500);                 // esperar a que el LCD estabilice su alimentación antes de inicializar

  // Inicializar LCD
  lcd.init();
  lcd.backlight();
  lcd.clear();                // limpiar contenido residual de la RAM del LCD
  lcd.createChar(0, iconoMano);

  // Pantalla de bienvenida
  lcd.setCursor(4, 0);
  lcd.print("UNIPOLI");
  delay(2000);

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.write(0);               // ícono de mano
  lcd.print(" Listo!");
  lcd.setCursor(0, 1);
  lcd.print("Muestra una sena");
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
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Palabra:");
    lcd.setCursor(0, 1);
    lcd.print(palabraActual);
    delay(2000);

    // Reiniciar
    palabraActual  = "";
    letraAnterior  = "";
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.write(0);
    lcd.print(" Listo!");
    lcd.setCursor(0, 1);
    lcd.print("Muestra una sena");
  }
}

//FUNCIÓN: MOSTRAR EN LCD
void mostrarLetra(String letra) {
  lcd.clear();

  // Fila superior: letra grande centrada (simulada con espacios)
  lcd.setCursor(0, 0);
  lcd.print("   LETRA:  ");
  lcd.write(0);              // ícono mano

  // Fila inferior: la letra detectada
  lcd.setCursor(0, 1);
  lcd.print("> ");
  lcd.print(letra);
  lcd.print("   [");
  lcd.print(palabraActual);
  lcd.print("]");
}
