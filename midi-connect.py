import os, time, usb.core, usb.util, socket, RPi.GPIO as GPIO

# MIDI CHANNEL CONSTANTS
NOTE_OFF       = 0x80
NOTE_ON        = 0x90
POLY_PRESSURE  = 0xA0
CONTROL_CHANGE = 0xB0
PROG_CHANGE    = 0xC0
CHAN_PRESSURE  = 0xD0
PITCH_BEND     = 0xE0
SYSEX_START    = 0xF0
SONG_POSITION  = 0xF2
SONG_SELECT    = 0xF3
SYSEX_END      = 0xF7
CLOCK          = 0xF8
START          = 0xFA
CONTINUE       = 0xFB
STOP           = 0xFC
ACTIVE_SENSE   = 0xFE

# MIDI CONTROL CONSTANTS
DRUM_CHANNEL         = 0x09
ALL_NOTES_OFF        = 0x78  # Send 0xBn 0x78 0x00 on each channel
LOCAL_CONTROL        = 0x7A  # 0xBn 0x7A 0x00 = OFF,  0x7F = ON  (n is ignored)
CONTROL_ON           = 0x7F
CONTROL_OFF          = 0X00
SUSTAIN_PEDAL        = 0x40
TOP_SHUTDOWN_NOTE    = 0x5E  # Bb5
TOP_SHUTDOWN_CONFIRM = 0x5C  # Ab5
HUBRESET_NOTE        = 0x5A  # F#5
TOP_REBOOT_NOTE      = 0x57  # Eb5
TOP_REBOOT_CONFIRM   = 0x55  # C#5
SCANUSB_NOTE         = 0x52  # Bb4
USB_DEBUG_NOTE       = 0x50  # Ab4
ALL_OFF_NOTE         = 0x4E  # F#4
OCTAVE_UP_NOTE       = 0x4B  # Eb4
OCTAVE_DOWN_NOTE     = 0x49  # C#4
DRUMS_TO_UDP_NOTE    = 0x46  # Bb3
DRUMS_TO_QY70_NOTE   = 0x44  # Ab3
DRUMS_TO_DGX_NOTE    = 0x42  # F#3
UDP_TO_QY70_NOTE     = 0x3F  # Eb3
UDP_TO_DGX_NOTE      = 0x3D  # C#3
MK61_TO_UDP_NOTE     = 0x3A  # Bb2
MK61_TO_QY70_NOTE    = 0x38  # Ab2
MK61_TO_DGX_NOTE     = 0x36  # F#2
QY70_TO_UDP_NOTE     = 0x33  # Eb2
QY70_TO_DGX_NOTE     = 0x31  # C#2
DGX_TO_UDP_NOTE      = 0x2E  # Bb1
DGX_TO_QY70_NOTE     = 0x2C  # Ab1
DGX_TO_DGX_NOTE      = 0x2A  # F#1
SYSEX_COUNT_NOTE     = 0x27  # Eb1
BOTTOM_SYSTEM_NOTE   = 0x25  # C#1
SILENT_NOTE          = 0X00
DEBUG_COLUMNS        = 5

# CONSOLE COLOURS
GREY   = '\033[1;37;0m'
WHITE  = '\033[1;37;48m'
CYAN   = '\033[1;36;48m'
PINK   = '\033[1;35;48m'
BLUE   = '\033[1;34;48m'
YELLOW = '\033[1;33;48m'
GREEN  = '\033[1;32;48m'
RED    = '\033[1;31;48m'


# FUNCTION DEFINITIONS

def dettachmocolufa():
   global mococfg, mocointf, mocobintf, mocoepin, mocoepout
   mococfg = mocolufa [0]
   mocointf = mococfg[(1,0)]
   mocobintf = mocointf.bInterfaceNumber
   mocoepin = mocointf[1]
   mocoepout = mocointf[0]
   if mocolufa.is_kernel_driver_active(0):
      mocolufa.detach_kernel_driver(0)
   if mocolufa.is_kernel_driver_active(mocobintf):
      mocolufa.detach_kernel_driver(mocobintf)
      usb.util.claim_interface(mocolufa, mocobintf)


def dettachyamaha():
   global dgxcfg, dgxintf, dgxbintf, dgxepin, dgxepout
   dgxcfg = yamaha[0]
   dgxintf = dgxcfg[(0,0)]
   dgxbintf = dgxintf.bInterfaceNumber
   dgxepin = dgxintf[0]
   dgxepout = dgxintf[1]
   if yamaha.is_kernel_driver_active(dgxbintf):
      yamaha.detach_kernel_driver(dgxbintf)
      usb.util.claim_interface(yamaha, dgxbintf)


def dettachmidiplus():
   global mkbcfg, mkbintf, mkbbintf, mkbepin, mkbepout
   mkbcfg = midiplus[0]
   mkbintf = mkbcfg[(0,0)]
   mkbbintf = mkbintf.bInterfaceNumber
   mkbepin = mkbintf[1]
   mkbepout = mkbintf[0]
   if midiplus.is_kernel_driver_active(mkbbintf):
      midiplus.detach_kernel_driver(mkbbintf)
      usb.util.claim_interface(midiplus, mkbbintf)


def dettachadapter():
   global adapcfg, adapintf, adapbintf, adapepin, adapepout
   adapcfg = adapter[0]
   adapintf = adapcfg[(1,0)]
   adapbintf = adapintf.bInterfaceNumber
   adapepin = adapintf[1]
   adapepout = adapintf[0]
   if adapter.is_kernel_driver_active(0):
      adapter.detach_kernel_driver(0)
   if adapter.is_kernel_driver_active(adapbintf):
      adapter.detach_kernel_driver(adapbintf)
      usb.util.claim_interface(adapter, adapbintf)


def scanusbdevices():
   print(GREEN + "SCANNING FOR DEVICES")
   global mocolufa, arduino, yamaha, adapter, midiplus
   global mocolufadetected, arduinodetected, yamahadetected, adapterdetected, midiplusdetected
   global adapter_count

   mocolufa = usb.core.find(idVendor=0x03eb, idProduct=0x2048)   # MocoLUFA Midi (Arduino)
   arduino = usb.core.find(idVendor=0x2341, idProduct=0x0001)    # Arduino Serial
   yamaha = usb.core.find(idVendor=0x0499, idProduct=0x1039)     # DGX-520
   adapter = usb.core.find(idVendor=0x0a92, idProduct=0x1010)    # USB to Midi Adapter (QY70)
   midiplus = usb.core.find(idVendor=0x0ccd, idProduct=0x0035)   # Midiplus 61 Keyboard
   ethernet = usb.core.find(idVendor=0x0fe6, idProduct=0x9700)   # Ethernet Adapter
   ext_hub = usb.core.find(idVendor=0x1a40, idProduct=0x0101)    # External USB Hub
   int_hub = usb.core.find(idVendor=0x1d6b, idProduct=0x0002)    # Internal USB Hub
   usb4_hub = usb.core.find(idVendor=0x058f, idProduct=0x9254)   # External 4 Port USB Hub

   if usb4_hub != None:
      print(YELLOW + "External 4 Port USB HUB detected")

   if int_hub == None:
      print(RED + "Internal USB HUB not detected")

   if ext_hub == None:
      print(RED + "USB HUB not detected")

   if ethernet == None:
      print(YELLOW + "Ethernet Adapter not detected")
 
   if mocolufa == None:
      mocolufadetected = False
   else:
      if not mocolufadetected:
         print(GREY + "Drumkit detected")
         dettachmocolufa()              # dettaches from Kernel Driver
         mocolufadetected = True

   if arduino == None:
      arduinodetected = False
   else:
      if not arduinodetected:
         print(RED + "Arduino Serial detected - Unplug and retry !")
         arduinodetected = True

   if yamaha == None:
      yamahadetected = False
   else:
      if not yamahadetected:
         print(GREY + "Yamaha DGX-520 detected")
         dettachyamaha()               # dettaches from Kernel Driver
         yamahadetected = True

   if midiplus == None:
      midiplusdetected = False
   else:
      if not midiplusdetected:
         print(GREY + "Midiplus 61 Keyboard detected")
         try:
            dettachmidiplus()              # dettaches from Kernel Driver
         except  usb.core.USBError as mkboerror:
            print(YELLOW + "WHOOPS")
            midiplusdetected = False
         midiplusdetected = True

   if adapter == None:
      adapterdetected = False
   else:
      if not adapterdetected:
         print(GREY + "USB Midi Adapter detected")
         dettachadapter()               # dettaches from Kernel Driver
         adapterdetected = True
   adapter_count = time.monotonic()
   set_play_mode()
   

def bindethernet():
   global udpmidi, udp_in, netdetected
   print(GREEN + "CONFIGURING ETHERNET")
   print(GREY + "IP Address 192.168.0.50, Out Port 5555, In Port 6666")
   netdetected = False
   try:
      udpmidi.bind(udp_in)
   except OSError as neterror:
      print(neterror)
      print(RED + "UNABLE TO BIND UDP PORT")
   else:
      print(WHITE + "UDP Bind Success")
      netdetected = True


def reset_usb_hub():
   print(RED + "DISABLING USB HUB")
   os.system("echo 0 | sudo tee /sys/bus/usb/devices/1-1/authorized")
   hubstart = time.monotonic()
   while time.monotonic() - hubstart < 3:
      pass
   print(GREEN + "RE-ENABLING USB HUB")
   os.system("echo 1 | sudo tee /sys/bus/usb/devices/1-1/authorized")
   adapter_count = time.monotonic()
   set_play_mode()


def send_all_notes_off():
   global mocolufadetected, yamahadetected, adapterdetected
   print(PINK + "ALL NOTES OFF")
   all_off_array = bytearray(64)
   i = 0
   c = 0
   while i < 64:
       all_off_array[i] = 0x0B
       i = i + 1
       all_off_array[i] = CONTROL_CHANGE + c
       i = i + 1
       c = c + 1
       all_off_array[i] = ALL_NOTES_OFF
       i = i + 1
       all_off_array[i] = CONTROL_OFF
       i = i + 1
   usb_to_udp(all_off_array)
   if yamahadetected:
      dgxepout.write(all_off_array)
   if mocolufadetected:
      mocoepout.write(all_off_array)
   if adapterdetected:
      usb_to_adapter(all_off_array)
   set_play_mode()


def send_dgx_local_control(allow_local):
   global yamahadetected
   local_control_array = bytearray(64)
   local_control_array[0] = 0x0B
   local_control_array[1] = CONTROL_CHANGE
   local_control_array[2] = LOCAL_CONTROL
   if allow_local:
      print(PINK + "DGX-520 LOCAL CONTROL OFF")
      local_control_array[3] = CONTROL_OFF
   else:
      print(PINK + "DGX-520 LOCAL CONTROL ON")
      local_control_array[3] = CONTROL_ON
   if yamahadetected:
      dgxepout.write(local_control_array)


def set_play_mode():
   global ledontime, ledofftime, system_count
   if system_count != 0:
      ledontime = 2
      ledofftime = 1
      system_count = 0
      print(GREEN + "PLAY MODE")


def toggle_allow_debug():
   global allow_debug
   allow_debug = not allow_debug
   if allow_debug:
      print(WHITE + "USB DEBUG ON")
   else:
      print(WHITE + "USB DEBUG OFF")
   set_play_mode()


def octave_up(note_offset):
   if note_offset <= 12:
      note_offset = note_offset + 12
      print(PINK + "OCTAVE UP")
   else:
      print(PINK + "OCTAVE ALREADY MAXIMUM")
   set_play_mode()
   return note_offset


def octave_down(note_offset):
   if note_offset >= -24:
      note_offset = note_offset - 12
      print(PINK + "OCTAVE DOWN")
   else:
      print(PINK + "OCTAVE ALREADY MINIMUM")
   set_play_mode()
   return note_offset


def print_sysex_count():
   global udp_sysex_count, usb_sysex_count
   print(WHITE + "UDP Sysex =", udp_sysex_count, " ... USB Sysex =", usb_sysex_count)
   udp_sysex_count = 0
   usb_sysex_count = 0
   set_play_mode()


def print_grey_or_cyan(allowed_var, device_text):
   if allowed_var:
      print(CYAN + device_text, end='')
   else:
      print(GREY + device_text, end='')


def print_enabled_devices():
   print_grey_or_cyan(allow_dgx_to_dgx, "DGX   ")
   print_grey_or_cyan(allow_dgx_to_adap, "QY70  ")
   print_grey_or_cyan(allow_dgx_to_udp, "UDP     ")
   print_grey_or_cyan(allow_adap_to_dgx, "DGX   ")
   print_grey_or_cyan(allow_adap_to_udp, "UDP     ")
   print_grey_or_cyan(allow_mkb_to_dgx, "DGX   ")
   print_grey_or_cyan(allow_mkb_to_adap, "QY70  ")
   print_grey_or_cyan(allow_mkb_to_udp, "UDP     ")
   print_grey_or_cyan(allow_udp_to_dgx, "DGX   ")
   print_grey_or_cyan(allow_udp_to_adap, "QY70    ")
   print_grey_or_cyan(allow_moco_to_dgx, "DGX  ")
   print_grey_or_cyan(allow_moco_to_adap, "QY70  ")
   print_grey_or_cyan(allow_moco_to_udp, "UDP")
   print()


def print_system_page():
   print(CYAN + "DEVICE ROUTING CONTROL")
                 # 0x2A  0x2C  0x2E    0x31  0x33    0x36  0x38  0x3A    0x3D  0x3F    0x42  0x44  0x46
   print(CYAN +   "F#1   Ab1   Bb1     C#2   Eb2     F#2   Ab2   Bb2     C#3   Eb3     F#3   Ab3   Bb3")
   print(CYAN +   "Send DGX to ....    QY70 to ..    Send MK61 to ...    UDP to ...    Send DRUMS to ..")
  #print(CYAN +   "DGX   QY70  UDP     DGX   UDP     DGX   QY70  UDP     DGX   QY70    DGX  QY70  UDP")
   print_enabled_devices()
   print(YELLOW + "SYSTEM ACTIONS")
                 # 0x27   ...    0x49  0x4B    0x4E  0x50  0x52    0x55  0x57    0x5A  0x5C  0x5E
   print(YELLOW + "Eb1    ...    C#4   Eb4     F#4   Ab4   Bb4     C#5   Eb5     F#5   Ab5   Bb5")
   print(YELLOW + "SYSEX         OCT   OCT     ALL   USB   SCAN    CON-  RE-     RESET CON-  SHUT")
   print(YELLOW + "COUNT         DOWN  UP      OFF   DEBUG USB     FIRM  BOOT    HUB   FIRM  DOWN")


def mkb_parse(usb_data):
   global system_count, ledontime, ledofftime, udp_sysex_count, usb_sysex_count, mkb_offset
   global allow_dgx_to_dgx,  allow_dgx_to_adap,  allow_dgx_to_udp
   global allow_mkb_to_dgx,  allow_mkb_to_adap,  allow_mkb_to_udp
   global allow_moco_to_dgx, allow_moco_to_adap, allow_moco_to_udp
   global allow_adap_to_dgx, allow_adap_to_udp
   global allow_udp_to_dgx,  allow_udp_to_adap
   mkb_parsed_ok = True
   i = 1
   while i < len(usb_data) and usb_data[i] == 0x00:
      i = i + 4
   if usb_data[i] & 0xF0 == CONTROL_CHANGE and usb_data[i + 1] == SUSTAIN_PEDAL:  # Sustain pedal pressed
      mkb_parsed_ok = False
      if usb_data[i + 2] == CONTROL_ON:
         system_count = 1
         print(BLUE + "CONTROL MODE  ...  Press lowest C# for more !")
      elif usb_data[i + 2] == CONTROL_OFF:                              # Sustain pedal released
         set_play_mode()
   elif usb_data[i] & 0xF0 == NOTE_ON and usb_data[i + 2] != SILENT_NOTE:  # Keypressed
      if usb_data[i + 1] == BOTTOM_SYSTEM_NOTE and system_count == 1:   # System sequence started
         system_count = 2
         ledontime = 0.05
         ledofftime = 0.05
         print_system_page()
      elif usb_data[i + 1] == TOP_SHUTDOWN_NOTE and system_count == 2:  # Shutdown sequence
         system_count = 3
         print(RED + "SHUTDOWN ENABLED  ...  Press Top Ab to Confirm !")
      elif usb_data[i + 1] == TOP_SHUTDOWN_CONFIRM and system_count == 3:
         print(RED + "SHUTDOWN")
         os.system("sudo shutdown -h now")
      elif usb_data[i + 1] == TOP_REBOOT_NOTE and system_count == 2:    # Reboot sequence
         system_count = 4
         print(RED + "REBOOT ENABLED  ...  Press Top C# to Confirm !")
      elif usb_data[i + 1] == TOP_REBOOT_CONFIRM  and system_count == 4:
         print(RED + "REBOOT")
         os.system("sudo reboot -h now")
      elif usb_data[i + 1] == SCANUSB_NOTE and system_count == 2:       # Scan USB & UDP
         bindethernet()
         scanusbdevices()
      elif usb_data[i + 1] == USB_DEBUG_NOTE and system_count == 2:     # Toggle USB debug
         toggle_allow_debug()
      elif usb_data[i + 1] == HUBRESET_NOTE and system_count == 2:      # Reset USB HUB
         reset_usb_hub()
      elif usb_data[i + 1] == ALL_OFF_NOTE and system_count == 2:       # Send All Notes Off
         send_all_notes_off()
      elif usb_data[i + 1] == DGX_TO_DGX_NOTE and system_count == 2:    # DGX routing
         allow_dgx_to_dgx = not allow_dgx_to_dgx
         print_enabled_devices()
         send_dgx_local_control(allow_dgx_to_dgx)
      elif usb_data[i + 1] == DGX_TO_QY70_NOTE and system_count == 2:
         allow_dgx_to_adap = not allow_dgx_to_adap
         print_enabled_devices()
      elif usb_data[i + 1] == DGX_TO_UDP_NOTE and system_count == 2:
         allow_dgx_to_udp = not allow_dgx_to_udp
         print_enabled_devices()
      elif usb_data[i + 1] == MK61_TO_DGX_NOTE and system_count == 2:    # MKB61 routing
         allow_mkb_to_dgx = not allow_mkb_to_dgx
         print_enabled_devices()
      elif usb_data[i + 1] == MK61_TO_QY70_NOTE and system_count == 2:
         allow_mkb_to_adap = not allow_mkb_to_adap
         print_enabled_devices()
      elif usb_data[i + 1] == MK61_TO_UDP_NOTE and system_count == 2:
         allow_mkb_to_udp = not allow_mkb_to_udp
         print_enabled_devices()
      elif usb_data[i + 1] == DRUMS_TO_DGX_NOTE and system_count == 2:  # DRUMS routing
         allow_moco_to_dgx = not allow_moco_to_dgx
         print_enabled_devices()
      elif usb_data[i + 1] == DRUMS_TO_QY70_NOTE and system_count == 2:
         allow_moco_to_adap = not allow_moco_to_adap
         print_enabled_devices()
      elif usb_data[i + 1] == DRUMS_TO_UDP_NOTE and system_count == 2:
         allow_moco_to_udp = not allow_moco_to_udp
         print_enabled_devices()
      elif usb_data[i + 1] == QY70_TO_DGX_NOTE and system_count == 2:   # QY70 routing
         allow_adap_to_dgx = not allow_adap_to_dgx
         print_enabled_devices()
      elif usb_data[i + 1] == QY70_TO_UDP_NOTE and system_count == 2:
         allow_adap_to_udp = not allow_adap_to_udp
         print_enabled_devices()
      elif usb_data[i + 1] == UDP_TO_DGX_NOTE and system_count == 2:    # UDP routing
         allow_udp_to_dgx = not allow_udp_to_dgx
         print_enabled_devices()
      elif usb_data[i + 1] == UDP_TO_QY70_NOTE and system_count == 2:
         allow_udp_to_adap = not allow_udp_to_adap
         print_enabled_devices()
      elif usb_data[i + 1] == OCTAVE_UP_NOTE and system_count == 2:     # Octave control
         mkb_offset = octave_up(mkb_offset)
      elif usb_data[i + 1] == OCTAVE_DOWN_NOTE and system_count == 2:
         mkb_offset = octave_down(mkb_offset)
      elif usb_data[i + 1] == SYSEX_COUNT_NOTE and system_count == 2:   # Print Sysex Count
         print_sysex_count()
      else:
         mkb_parsed_ok = False
         set_play_mode()
   else:
      mkb_parsed_ok = False
      set_play_mode()
   return mkb_parsed_ok


def usb_to_adapter(usb_data):        # Send to USB Adapter - requires cable values of 1
   i = 0
   while i < len(usb_data):
      usb_data[i] = usb_data[i] + 0x10
      i = i + 4
   try:
      adapepout.write(usb_data)
   except usb.core.USBError as adaperror:
      if adaperror.args[0] == 16:
         print(YELLOW, adaperror, "USB Adapter is Busy")


def usb_to_dgx(usb_data):  # DGX requires 64 bytes
   if len(usb_data) < 0x40:
      for i in range(len(usb_data), 0x40):
         usb_data.append(0x00)
   dgxepout.write(usb_data)


def usb_to_udp(usb_data):
   global usb_sysex_count, netdetected
   try:
      udpmidi.sendto(usb_data, udp_out)
   except OSError as neterror:
      print(RED + "Error Sending UDP", neterror)
      netdetected = False
   for i in range(0, len(usb_data)):
      if usb_data[i] == SYSEX_START:
         usb_sysex_count = usb_sysex_count + 1


def strip_realtime(usb_data):
   not_system_realtime = False
   i = 1
   while i < len(usb_data):
      if usb_data[i] != 0x00:
         if usb_data[i] == CLOCK or usb_data[i] == ACTIVE_SENSE:
            usb_data[i - 1] = 0x00
            usb_data[i] = 0x00
            usb_data[i + 1] = 0x00
            usb_data[i + 2] = 0x00
         else:
            not_system_realtime = True
      i = i + 4
   return not_system_realtime


hex_list = ["0x00", "0x01", "0x02", "0x03", "0x04", "0x05", "0x06", "0x07",
            "0x08", "0x09", "0x0a", "0x0b", "0x0c", "0x0d", "0x0e", "0x0f"]


def print_hex(hex_val):
   if hex_val < 0x10:
      print(WHITE, hex_list[hex_val], end='')
   else:
      print(WHITE, hex(hex_val), end='')


def print_usb_data(usb_data):
   column = 1
   first_line = True
   i = 1
   while i < len(usb_data):
      if usb_data[i] != 0x00:
         if not first_line and column == 1:
            print("    ", end='')
         print_hex(usb_data[i - 1])
         print_hex(usb_data[i])
         print_hex(usb_data[i + 1])
         print_hex(usb_data[i + 2])
         if column >= DEBUG_COLUMNS:
            print()
            column = 1
            first_line = False
         else:
            print("    ", end='')
            column = column + 1
      i = i + 4
   if column > 1:
      print()

"""
def detect_channel(usb_data):
   detected_channel = 0x10
   i = 1
   while i < len(usb_data) and detected_channel == 0x10:
      if usb_data[i] >= NOTE_OFF and usb_data[i] < SYSEX_START:
         detected_channel = (usb_data[i] & 0x0F)
      i = i + 4
   return detected_channel
"""
 
def transpose_notes(usb_data, usb_offset):
   i = 1
   while i < len(usb_data):
      if usb_data[i] & 0xF0 == NOTE_ON or usb_data[i] & 0xF0 == NOTE_OFF:
         usb_data[i + 1] = usb_data[i + 1] + usb_offset
      i = i + 4
   return



# MAIN PROGRAM

boot_wait = time.monotonic()
while time.monotonic() - boot_wait < 10:
   pass
print()
print(CYAN + "MIDI CONTROL SYSTEM")
print("- - BY CHRIS - -")
print()
print(WHITE + "Taking conrol of ACT LED ...", end=' ')

os.system("echo gpio | sudo tee /sys/class/leds/led0/trigger")
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(47, GPIO.OUT)

# ETHERNET SETUP
udp_out = ("192.168.0.50", 5555)
udp_in = ('', 6666)
udpmidi = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpmidi.setblocking(False)


# ACT LED control variables
ledontime = 2
ledofftime = 1
ledtoggle = False
ledstart = 0

# Device detection control variables
system_count = 0
scaninterval = 5
scanstart = 0
mocolufadetected = False
arduinodetected = False
yamahadetected = False
adapterdetected = False
midiplusdetected = False
netdetected = False
active_sense_count = 0
udp_sysex_count = 0
usb_sysex_count = 0

# Device routing variables
allow_dgx_to_dgx = False
allow_dgx_to_adap = True
allow_dgx_to_udp = True
allow_mkb_to_dgx = True
allow_mkb_to_adap = True
allow_mkb_to_udp = True
allow_moco_to_dgx = True
allow_moco_to_adap = True
allow_moco_to_udp = True
allow_adap_to_dgx = True
allow_adap_to_udp = True
allow_udp_to_dgx = True
allow_udp_to_adap = True
allow_debug = False
mkb_offset = -12
#current_mkb_in_channel = 0
#current_mkb_out_channel = 0
#current_dgx_in_channel = 0
#current_dgx_out_channel = 0

bindethernet()

while True:    # continuous loop

   if not midiplusdetected:           # Scan for devices if Midiplus is disconnected
      if time.monotonic() - scanstart > scaninterval:
         scanusbdevices()
         scanstart = time.monotonic()
   else:


      if netdetected:   # UDP Ethernet
         try:
            udp_in_data = udpmidi.recvfrom(1024)
         except OSError as neterror:
            if neterror.args[0] != 11:
               print(RED + "UDP has been disconnected", neterror)
               netdetected = False
         else:
            if len(udp_in_data) != 0:
               udp_to_usb = bytearray(udp_in_data[0])
               if allow_debug:
                  print(BLUE + "UDP ", end='')
                  print_usb_data(udp_to_usb)
               if yamahadetected and allow_udp_to_dgx:
                  dgxepout.write(udp_to_usb)
               if adapterdetected and allow_udp_to_adap:
                  usb_to_adapter(udp_to_usb)
               for i in range(0, len(udp_to_usb)):
                  if udp_to_usb[i] == SYSEX_START:
                     udp_sysex_count = udp_sysex_count + 1

      if mocolufadetected:   # Drumkit Midi supplies variable length packets
         try:
            mocodata = mocoepin.read(mocoepin.wMaxPacketSize, 1)
         except usb.core.USBError as mocoerror:
            if mocoerror.args[0] == 32 or mocoerror.args[0] == 19:
               print(YELLOW + "Drumkit has been disconnected")
               mocolufadetected = False
         else:
            if allow_debug:
               print(GREEN + "DRUM", end='')
               print_usb_data(mocodata)
            if netdetected and allow_moco_to_udp:
               usb_to_udp(mocodata)
            if yamahadetected and allow_moco_to_dgx:
               usb_to_dgx(mocodata)
            if adapterdetected and allow_moco_to_adap:
               usb_to_adapter(mocodata)

      if adapterdetected:   # USB Midi Adapter (QY70) supplies variable length packets
         try:
            adapdata = adapepin.read(adapepin.wMaxPacketSize, 1)
         except usb.core.USBError as adaperror:
            if adaperror.args[0] == 32 or adaperror.args[0] == 19:
               print(YELLOW + "USB Adapter has been disconnected")
               adapterdetected = False
         else:
            if strip_realtime(adapdata):
               if allow_debug:
                  print(CYAN + "QY70", end='')
                  print_usb_data(adapdata)
               if netdetected and allow_adap_to_udp:
                  usb_to_udp(adapdata)
               if yamahadetected and allow_adap_to_dgx:
                  usb_to_dgx(adapdata)

      if yamahadetected:   # DGX-520, continually polling prevents lockup.
         try:
            dgxdata = dgxepin.read(dgxepin.wMaxPacketSize, 1)
         except usb.core.USBError as dgxerror:
            if dgxerror.args[0] == 32 or dgxerror.args[0] == 19:
               print(YELLOW + "DGX-520 has been disconnected")
               yamahadetected = False
         else:
            if strip_realtime(dgxdata):
               if allow_debug:
                  print(PINK + "DGX ", end='')
                  print_usb_data(dgxdata)
               if yamahadetected and allow_dgx_to_dgx:
                  dgxepout.write(dgxdata)
               if netdetected and allow_dgx_to_udp:
                  usb_to_udp(dgxdata) 
               if adapterdetected and allow_dgx_to_adap:
                  usb_to_adapter(dgxdata)

      if midiplusdetected:   # Midiplus Keyboard supplies 64 bytes which satisfies DGX-520 requirements
         try:
            mkbdata = mkbepin.read(mkbepin.wMaxPacketSize, 1)
         except usb.core.USBError as mkboerror:
            if mkboerror.args[0] == 32 or mkboerror.args[0] == 19:
               print(YELLOW + "Midiplus Keyboard has been disconnected")
               midiplusdetected = False
         else:
            active_sense_count = 0
            if strip_realtime(mkbdata):
               if allow_debug:
                  print(YELLOW + "MK61", end='')
                  print_usb_data(mkbdata)
               if not mkb_parse(mkbdata):
                  transpose_notes(mkbdata, mkb_offset)
                  if yamahadetected and allow_mkb_to_dgx and system_count < 2:
                     dgxepout.write(mkbdata)
                  if netdetected and allow_mkb_to_udp and system_count < 2:
                     usb_to_udp(mkbdata)
                  if adapterdetected and allow_mkb_to_adap and system_count < 2:
                     usb_to_adapter(mkbdata)


   # ACT LED control
   if ledtoggle:
      if time.monotonic() - ledstart > ledontime:
         ledstart = time.monotonic()
         ledtoggle = False
         GPIO.output(47,GPIO.HIGH)
         if ledontime >= 2 and midiplusdetected:
            active_sense_count = active_sense_count + 1
            if active_sense_count > 1:
               print(RED, "Resetting USB Hub in", 6 - active_sense_count)
               if active_sense_count >= 7:
                  reset_usb_hub()
                  active_sense_count = 0
   else:
      if time.monotonic() - ledstart > ledofftime:
         ledstart = time.monotonic()
         ledtoggle = True
         GPIO.output(47,GPIO.LOW)

   time.sleep(0.001)


# END OF PROGRAM
