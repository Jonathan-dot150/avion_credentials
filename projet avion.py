
import keypad
import board
import mfrc522
import neopixel
import time
import pwmio
from adafruit_motor import motor
from adafruit_motor import servo
import analogio
import adafruit_dht
import adafruit_hcsr04
import math
import digitalio



rfidRST = board.A2
rfidSCK = board.D12
rfidMosi = board.D11
rfidMiso = board.D13
rfidSDA = board.D10

rfid = mfrc522.MFRC522( rfidSCK,rfidMosi,rfidMiso,rfidRST,rfidSDA)
rfid.set_antenna_gain(0x07 << 8)

# Configuration des broches PWM pour contrôler le moteur DC
foward = pwmio.PWMOut(board.A0)
backward = pwmio.PWMOut(board.A1)

# Création de l'objet moteur DC
moteur = motor.DCMotor(positive_pwm=foward, negative_pwm=backward)

# Création de l'objet PWM pour contrôler le signal de commande du servo-moteur
pwm = pwmio.PWMOut(board.A3, duty_cycle=2 ** 15, frequency=50)

# Création de l'objet Servo pour contrôler le servo-moteur
servo_motor = servo.Servo(pwm)

# Configuration des broches analogiques pour le joystick
x = board.D9
y = board.D6
button = digitalio.DigitalInOut(board.D5)
button.switch_to_input(pull=digitalio.Pull.UP)

analog_center = 32768
analog_min = 0
analog_max = 65535

x_analog_in = analogio.AnalogIn(x)
y_analog_in = analogio.AnalogIn(y)

dht11 = adafruit_dht.DHT11(board.A4)

pixel_pin = board.A5
num_pixels = 8
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.3, auto_write=False)

RED = (255, 0, 0)

sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.RX, echo_pin=board.TX)



# Identifiants autorisés
AUTHORIZED_IDS = ["6d1a64382b"], ["7dsO97Nd2L"], ["2Dohs719Kq"], ["9Hfs61Lnd6"]

AUTHORIZED_DOUBLEAUTH = ["7382"], ["9210"], ["2824"], ["4021"]


# Initialisation de la Neopixel
#np = neopixel.NeoPixel(machine.Pin(14), 1)

# État initial
current_state = 1

# Initialisation du clavier à matrice
touche = {
    0: '1',
    1: '2',
    2: '3',
    3: '4',
    4: '5',
    5: '6',
    6: '7',
    7: '8',
    8: '9',
    9: '*',
    10: '0',
    11: '#',
}

#km = keypad.KeyMatrix(
    #row_pins=(board.A0, board.A1, board.A2, board.A3),
    #column_pins=(board.D13, board.D12, board.D11),
    #columns_to_anodes=True,
#)



# Tableau des aéroports
AIRPORTS = {
    "101": "YUL Montreal",
    "111": "ATL Atlanta",
    "222": "HND Tokyo",
    "764": "LHR London",
    "492": "CAN Baiyun",
    "174": "CDG Paris",
    "523": "AMS Amsterdam",
    "829": "FRA Frabcfort",
    "912": "MAD Madrid-Barajas",
    "927": "YVR Vancouver"
}

while True:
    if current_state == 1:
        print("En attente d'une carte RFID...")
        # Attendre qu'une carte soit détectée
        (stat, tag_type) = rfid.request(rfid.REQIDL)
        if stat == rfid.OK:
            (stat, raw_uid) = rfid.anticoll()
            if stat == rfid.OK:
                # Convertir l'identifiant de la carte en chaîne hexadécimale
                uid_hex = ''.join('{:02x}'.format(x) for x in raw_uid)
                print("Identifiant de la carte: ", uid_hex)
                # Vérifier si l'identifiant est autorisé
                if uid_hex in AUTHORIZED_IDS:
                    DoubleAuth= print("Entrez votre double Authentification: ")
                    if DoubleAuth in AUTHORIZED_DOUBLEAUTH:
                        print("Accès autorisé !")
                        current_state = 2
                    else: print("Accès refusé.")
                else:
                    print("Accès refusé.")
                    

    elif current_state == 2:
        print("Entrez le code de l'aeroport:")
# Attendre que le code de l'aéroport soit entré via le clavier matriciel
        code = ""
        event = []
        while len(code) < 3:
            #event = km.events.get()
            if event:
                if event.pressed:
                    key = touche[event.key_number]
                    print("Clé appuyée :", key)
                    if key.isdigit() and len(code) < 3:
                        code += key
                        print("Entrez le code de l'aeroport:", code)
                        time.sleep(0.2)

        airport_name = AIRPORTS.get(code)
        if airport_name:
            print("L'aéroport sélectionné est :", airport_name)
            print("Aeroport: " + airport_name + "\nAppuyez sur PWR")
            # Attendre que l'interrupteur PWR soit mis à la position ON
            while True:
                #if machine.Pin(13, machine.Pin.IN).value() == 1:
                    current_state = 3
                    break
        else:
            print("Code d'aéroport invalide.")
            print("Code invalide !\nEntrez le code de l'aeroport:")
            time.sleep(2)
                # Retourner à l'état 2 pour permettre la saisie d'un nouveau code
            current_state = 2
    elif current_state == 3:
        # Initialisation de l'état du verrouillage
        locked = False
        while True:

           temp_c = dht11.temperature
           humidity =dht11.humidity
    
           distance = sonar.distance
           if (distance < 10):
                current_state ==1
               
            if code == 0000:
                print("Aéroport avisé")
            
            # Si le bouton est appuyé, verrouiller/déverrouiller les contrôles
           if not button.value:
                locked = not locked
                time.sleep(0.2)  # Ajout d'un délai pour éviter les rebonds de bouton
            
           if not locked:
                # servo moteur
                x_degrees = int(x_analog_in.value / 65535 * 180)
                servo_motor.angle = x_degrees

                # Lecture de la valeur de l'axe Y du joystick
                y_axis = y_analog_in.value
                
                # Moteur
                y_normalized = (y_axis - analog_center) / (analog_max - analog_center)
                y_normalized = max(-1, min(1, y_normalized))
                
                moteur.throttle = y_normalized
            
           x_analog_value = x_analog_in.value
           y_analog_value = y_analog_in.value

        
           x_position = x_analog_value - analog_center
           y_position = y_analog_value - analog_center

           angle_degrees = math.degrees(math.atan2(y_position, x_position)) % 360

           for i in range(num_pixels):
                if i*45 <= angle_degrees < (i+1)*45:
                    pixels[i] = (255, 150, 0)
                else:
                    pixels[i] = (0, 0, 0)
           pixels.show()

           print("\033[2J\033[H")
           print("Angle Servo = ", x_degrees)
           print("Temp: {:.1f} C ".format(temp_c))
           print(" Humidité: {:.1f}% ".format(humidity))
           print("Vitesse Moteur= {:.1f}%.".format(y_normalized* 100))
           print (angle_degrees)
           print(airport_name)
            

           time.sleep(0.1)




