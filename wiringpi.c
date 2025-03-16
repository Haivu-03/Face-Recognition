#include <wiringPi.h>
#include <lcd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUZZER_PIN 0 // GPIO pin 17

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <name>\n", argv[0]);
        return 1;
    }

    char *name = argv[1];

    // Setup WiringPi
    if (wiringPiSetup() == -1) {
        fprintf(stderr, "WiringPi setup failed\n");
        return 1;
    }

    // Setup Buzzer
    pinMode(BUZZER_PIN, OUTPUT);

    // Setup LCD (assuming you have connected it correctly)
    int lcd;
    if ((lcd = lcdInit(2, 16, 4, 11,10, 0,1,2,3,4,5,6,7)) == -1) {
        fprintf(stderr, "LCD setup failed\n");
        return 1;
    }

    // Sound the buzzer
    digitalWrite(BUZZER_PIN, HIGH);
    delay(500); // 0.5 second
    digitalWrite(BUZZER_PIN, LOW);

    // Display welcome message on LCD
    lcdClear(lcd);
    lcdPosition(lcd, 0, 0);
    lcdPrintf(lcd, "Welcome");
    lcdPosition(lcd, 0, 1);
    lcdPrintf(lcd, "%s", name);

    delay(3000); // Display for 3 seconds

    // Clear the LCD
    lcdClear(lcd);

    return 0;
}
