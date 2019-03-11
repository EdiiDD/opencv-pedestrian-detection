import requests
import base64
import logging



# Parametros del servidor de imagenes
urlServerImg = "http://julian.byprox.com/opencv/upload.php"

frameName = 'frame0.png'

frame = base64.b64encode(open(frameName, 'rb').read())

datos = { 'imagen' : frame }


req = requests.post(urlServerImg, data=datos)


print(req.url)


try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

requests.get(urlServerImg)

print(req.content)
