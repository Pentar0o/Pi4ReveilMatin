import board
import digitalio
from digitalio import DigitalInOut, Direction, Pull
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
import time
import vlc

import adafruit_dotstar


###############################################################################
##########                   GESTION DES E LED                     ############
###############################################################################
DOTSTAR_DATA = board.D5
DOTSTAR_CLOCK = board.D6
dots = adafruit_dotstar.DotStar(DOTSTAR_CLOCK, DOTSTAR_DATA, 3, brightness=0.2)
###############################################################################
##########               FIN GESTION DES 3 LED                      ###########
###############################################################################


###############################################################################
##########                   GESTION DES BOUTONS                   ############
###############################################################################
BUTTON_PIN = board.D17
JOYDOWN_PIN = board.D27
JOYLEFT_PIN = board.D22
JOYUP_PIN = board.D23
JOYRIGHT_PIN = board.D24
JOYSELECT_PIN = board.D16
 
buttons = [BUTTON_PIN, JOYUP_PIN, JOYDOWN_PIN,
           JOYLEFT_PIN, JOYRIGHT_PIN, JOYSELECT_PIN]
for i,pin in enumerate(buttons):
  buttons[i] = DigitalInOut(pin)
  buttons[i].direction = Direction.INPUT
  buttons[i].pull = Pull.UP
button, joyup, joydown, joyleft, joyright, joyselect = buttons
###############################################################################
##########               FIN GESTION DES BOUTONS                    ###########
###############################################################################


###############################################################################
##########                   GESTION DE L'ECRAN                    ############
###############################################################################

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None
# # Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000
# # Setup SPI bus using hardware SPI:
spi = board.SPI()
# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=240,
    height=240,
    x_offset=0,
    y_offset=284,
)
 
# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = 40  # we swap height/width to rotate it to landscape!
width = 240
image = Image.new("RGB", (width, height))
rotation = 0
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

###############################################################################
##########               FIN GESTION DE L'ECRAN                    ############
###############################################################################

#Symbole d'alarme activée en blanc par défaut
CouleurAlarmeOff = (255,255,255)
CouleurAlarmeOn = (255,0,0)
CouleurAlarme = (255,255,255)

pos_led = 0

######## Gestion de l'Alarme ########
heure = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
minute = [0,15,30,45]
alarmeh = heure[8]
alarmem = minute[0]
#On stock la position dans le tableau pour l'incrémentation via le joystick
posh = 8
posm = 0
play = 0

###############################################################################
##########               GESTION DE LA MUSIQUE                     ############
###############################################################################
player = vlc.MediaPlayer("Daft.flac")


while(True):

    if (alarmeh < 10):
        txtalarmeh = "0" + str(alarmeh)
    else:
        txtalarmeh = str(alarmeh)
    if (alarmem == 0):
        txtalarmem = "00"
    else :
        txtalarmem = str(alarmem)

    draw.text((30, 0), "Alarme : " + txtalarmeh + ":" + txtalarmem, font=font, fill=(255,255,255))
    draw.ellipse((0, 5, 20, 25), fill=CouleurAlarme)

    Heure = time.strftime("%H:%M", time.localtime())
    HeureAlarme = txtalarmeh+":"+txtalarmem


###############################################################################
##########               GESTION DE L'ALARME                       ############
###############################################################################

    if (Heure == HeureAlarme):
        if (CouleurAlarme == CouleurAlarmeOn):
            player.play()
            play = 1
            CouleurAlarme = CouleurAlarmeOff

###############################################################################
##########               FIN GESTION DE L'ALARME                   ############
###############################################################################


    if not button.value:
        if (CouleurAlarme == CouleurAlarmeOn):
            CouleurAlarme = CouleurAlarmeOff
        else:
            CouleurAlarme = CouleurAlarmeOn


    if not joyup.value:
        #Comme le pi est inversé on inverse les commandes
        if (posh == 0) :
            posh = 23
            alarmeh = heure[posh]
            #print(str(alarmeh))
        else :
            posh -= 1
            alarmeh = heure[posh]
            #print(str(alarmeh))
        draw.rectangle((140, 5, 180, 25), fill=(0,0,0))

    if not joydown.value:
        if (posh == 23) :
            posh = 0
            alarmeh = heure[posh]
            #print(str(alarmeh))
        else :
            posh += 1
            alarmeh = heure[posh]
            #print(str(alarmeh))
        draw.rectangle((140, 5, 180, 25), fill=(0,0,0))

    if not joyright.value:
        if (posm == 0) :
            posm = 3
            alarmem = minute[posm]
            #print(str(alarmem))
        else :
            posm -= 1
            alarmem = minute[posm]
            #print(str(alarmem))
        draw.rectangle((190, 5, 230, 25), fill=(0,0,0))

    if not joyleft.value:
        if (posm == 3) :
            posm = 0
            alarmem = minute[posm]
            #print(str(alarmem))
        else :
            posm += 1
            alarmem = minute[posm]
            #print(str(alarmem))
        draw.rectangle((190, 5, 230, 25), fill=(0,0,0))


    if not joyselect.value:
        if (play == 0):
            player.play()
            play = 1
        else:
            player.stop()
            play = 0

    disp.image(image, rotation)

#Chenillard Led
    if (pos_led == 0):
        dots[0] = (0,0,0)
        dots[1] = (0,0,0)
        dots[2] = (255,255,0)
        pos_led += 1
    elif (pos_led == 1):
        dots[0] = (0,0,0)
        dots[1] = (255,255,0)
        dots[2] = (0,0,0)
        pos_led += 1
    else :
        dots[0] = (255,255,0)
        dots[1] = (0,0,0)
        dots[2] = (0,0,0)
        pos_led = 0

    dots.show()
#Fin Chenillard Led

    time.sleep(1)
