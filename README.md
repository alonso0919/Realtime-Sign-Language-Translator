# Sign Language to Text

Project that translates sign language to text in real time using Python and Arduino.

This system uses the camera to detect the hand, interprets the sign as a letter, and displays it on screen. It also sends the information to an Arduino, which displays it on an LCD screen and automatically forms words.

## Technologies Used

- Python with OpenCV, MediaPipe, and PySerial
- Arduino with serial communication and I2C LCD screen

## How It Works

1. The camera detects the hand using MediaPipe
2. The hand landmarks are analyzed
3. It identifies which fingers are bent or extended
4. This is compared against patterns to determine a letter
5. The letter is sent to Arduino
6. Arduino displays the letter and automatically forms words
7. If no new letters are detected for a few seconds, the word resets

## Project Structure

- `sign_to_text.py` — main Python code
- `arduino.ino` — Arduino code
- `README.md` — documentation

## Requirements

Install the following Python libraries:
- opencv-python
- mediapipe
- pyserial

A compatible Arduino board and I2C LCD screen are required.

## Usage

1. Connect the Arduino to the computer
2. Set the port in the Python file (e.g., `COM4`)
3. Upload the code to the Arduino
4. Run the program with `python sign_to_text.py`
5. Press `Q` to quit

## Notes

- The system works based on rules, not a trained AI model
- Works best with good lighting
- Detects only one hand
- May require adjustments depending on the camera

## Author

Alonso Sanchez

## License

Educational use
