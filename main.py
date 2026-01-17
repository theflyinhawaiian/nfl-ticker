import board
import time
import neopixel
from adafruit_pixel_framebuf import PixelFramebuffer

import wifi
import adafruit_requests
import adafruit_connection_manager

pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)

gameUrl = "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com/getNFLBoxScore?gameID=20260117_BUF%40DEN&playByPlay=true"
custom_headers = {
    'x-rapidapi-host': "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com",
    'x-rapidapi-key': "03e3c28abcmsh0476b313fb0606ap160f2ajsn141566ac6115"
}

pixels = neopixel.NeoPixel(board.GP15, 512, brightness=0.05, auto_write=False)

col_max = 32

pixel_framebuf = PixelFramebuffer(pixels, 16, 32, reverse_x=True, rotation=1)

pixel_framebuf.fill(0x000000)
pixel_framebuf.display()

col = col_max

num_events = 0;

ssid = "wifi-name"
password = "wifi-password"

try:
    # Connect to the Wi-Fi network
    wifi.radio.connect(ssid, password)
except OSError as e:
    print(f"[ERROR]OSError: {e}")

previousEvents = []

while True:
    pixel_framebuf.fill(0x000000)
    pixel_framebuf.display()
    
    print("Making request!")
    response = requests.request("GET", gameUrl, headers=custom_headers)
    print(f"response returned code {response.status_code}")
    
    events = []
    carry = b''
    inQuotes = False
    readingPlay = False
    scoringPlaysFound = False
    try:
        for chunk in response.iter_content(chunk_size=128):
            buf = carry + chunk

            idx = buf.find(b'"')
            while idx != -1:

                if inQuotes:
                    token = buf[:idx]

                    if readingPlay:
                        events.append(token.decode('utf-8'))
                        readingPlay = False

                    if scoringPlaysFound and token == b'score':
                        readingPlay = True
                    elif token == b'scoringPlays':
                        scoringPlaysFound = True

                inQuotes = not inQuotes
                
                buf = buf[idx+1:]
                
                idx = buf.find(b'"')

            carry = buf;
    finally:
        response.close()
    
    if len(previousEvents) < len(events):
        event = events[len(events) - 1]
        strlen = len(event)
        col = col_max
        while col > -(strlen * 5):
            pixel_framebuf.fill(0x000000)
            pixel_framebuf.text(event, col, 4, 0x00ff00)
            pixel_framebuf.display()
            col -= 1
        
        previousEvents = events
    time.sleep(30)
