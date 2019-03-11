# Importacion de librerias
from datetime import datetime, time
from imutils.object_detection import non_max_suppression
import numpy as np
import urllib.request
import random as rng
import cv2
import imutils
import time
import os
import requests
import base64

# PARAMETROS DEL PROGRAMA

# Capturamos el video de una camara Web IP
url = "../video/7.mp4"
urlWebCam = "http://91.221.52.198:82/mjpg/video.mjpg"
urlWebCam1 = "http://93.87.72.254:8090/mjpg/video.mjpg"
urlWebCam2 = 'rtsp://172.30.30.6/ch0_1.h264'
cap = cv2.VideoCapture(url)

# Parametros del servidor de imagenes
urlServerImg = "http://julian.byprox.com/opencv/upload.php"


# Color del rectangulo
color = (0,0,0)
colorAzul  = (255,0,0)
colorVerde = (0,255,0)
colorRojo = (0,0,255)

# Grosor de figuras
grosor = 0
grosorNormal = 2
grosorAlerta = 3

# Posiciones de la linea de seguridad
xS1 = 250
yS1 = 0
xS2 = 250
yS2 = 380

# Tiempo que esta la persona en la zona de seguridad
zonaProhibida = False
currentMillis = 0
endMillis = 0
textoProhibido =  "Tiempo en zona de seguridad " , currentMillis

# Parametros de texto indicativo
font                   = cv2.FONT_HERSHEY_COMPLEX_SMALL
topLeftCornerOfText = (10,20)
topLeftCornerOfText1 = (10,30)
bottomLeftCornerOfText = (20,340)
fontScale              = 0.5
fontColor              = colorVerde
lineType               = 1

# Texto a imprimir
textoSinPeligro = "Sin Peligro"
textoPeligro = "PELIGRO"
texto = textoSinPeligro

# Capturar el tiempo actual
tiempoActual = 0
tiempoAux = 0
tiempoDiff = 0

# Carpeta donde se va a guardar las imagenes
FOLDER_NAME_IMAGES = "./../images_HOG"


# Frames a mostrar
FRAMES = 3
numFrames = 0

# Frames a enviar, cada x tiempo
FRAMES_ENVIAR = 5

# Parametros HOG
hog = cv2.HOGDescriptor()
hog.setSVMDetector( cv2.HOGDescriptor_getDefaultPeopleDetector())

# Contador imagenes
contImages = 0

# Coordenadas auxiliares  [xA, yA, xB, yB]
coordenadasAnteriores = [0, 0, 0, 0]

# FUNCIONES AUXILIARES DEL PRGRAMA
def background_subtraction(previous_frame, frame_resized_grayscale, min_area):
    frameDelta = cv2.absdiff(previous_frame, frame_resized_grayscale)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, np.ones((11,11)), 5)
    _,cnts,_ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    temp = 0
    for c in cnts:
        if cv2.contourArea(c) > 500:
            temp = 1
    return temp

# Ver si en el punto anterior estaban muy lejo
def detect_people(frame):
	(rects, weights) = hog.detectMultiScale(frame, winStride = (4, 4), padding = (0, 0), scale = 1.05)
	rects = np.array([[x, y, x + w, y + h] for (x, y, w,h) in rects])
	pick = non_max_suppression(rects, probs = None, overlapThresh = 0.65)
	return pick

def drawDetection(frame, xA, yA, xB, yB, cont):
	# Dibujamos en la imagen.
	os.environ['TZ'] = 'EST'
	strTime = " "
	strTime = time.strftime("%x %X")
	cv2.putText(frame,"Time: {time}".format(time=tiempoDiff), topLeftCornerOfText1, cv2.FONT_HERSHEY_SIMPLEX, fontScale, color, grosorNormal) #Peligro
	# Guardamos la imagen en un folder.
	frameName = "frame%d.png" %cont
	cv2.imwrite(frameName, frame)
	postFrame(frameName)
	return frame
	
def postFrame(frame):
	frame = base64.b64encode(open(frame, 'rb').read())
	datos = { 'imagen' : frame }
	req = requests.post(urlServerImg, data=datos)
	print("Image post to server")


def moveX(xA, yA, pick, frame):
	
	
	# Ver el punto actual supera la linea
	x = 0
	if xA > xS1:
		x = 1

	# Ver que el punto anterior no se mueve del sitio, aqui tengo devuelvo un 0 si esta de paso 
	# Variacion en el eje de la X
		#print("Dentro de la zona ejeX1")
		variacionX = 5
		#print("Dentro de la zona ejeX2")
		if abs(xA - coordenadasAnteriores[0]) > variacionX:
			#cv2.putText(frame,"XXX", (xA, yA), cv2.FONT_HERSHEY_SIMPLEX, fontScale, color, grosorNormal) #Peligro
			x = 2

	return x

def moveY(xA, yA, pick, frame):

	y = 0
	if xA > yS1:
		y = 1
		# Ver si esta de paso, ver si vuelve hacia atras.
		#print("Dentro de la zona ejeY1")
		variacionY = 5
		if abs(yA - coordenadasAnteriores[1]) > variacionY:
			#print("Dentro de la zona ejeY2")	
			#cv2.putText(frame,"YYY", (xA, yA), cv2.FONT_HERSHEY_SIMPLEX, fontScale, color, grosorNormal) #Peligro 
			y = 2
	return y

# Funcion para calucar la diferencia en segundos
def date_diff_in_Seconds(dt2, dt1):
	timedelta = dt2 - dt1
	return timedelta.days * 24 * 3600 + timedelta.seconds


primeraVez = 0
primeraImagen = 0
while(1):
	numFrames = numFrames + 1
	if numFrames % FRAMES ==  0:

		# Capturamos el frame siguiente
		ret, current_frame = cap.read()
		# Si el video termina
		if (not ret):
			break

		cv2.line(current_frame, (xS1, yS1), (xS2, yS2), colorRojo, grosorNormal)
		#frame_resized = imutils.resize(current_frame, width=min(400, current_frame.shape[1]))
		frame_resized_grayscale = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
		previous_frame = frame_resized_grayscale

		# Capturamos el frame siguiente
		ret, current_frame = cap.read()
		# Si el video termina
		if (not ret):
			break
		#frame_resized = imutils.resize(current_frame, width=min(400, current_frame.shape[1]))
		min_area = (3000/800) * current_frame.shape[1]
		frame_resized_grayscale = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
		temp = background_subtraction(previous_frame, frame_resized_grayscale, min_area)

		# Si hay movimiento empieza a capturar frames para detectar a una persona.
		if temp == 1:
			# Detectamos en la imagen al sujeto
			pick = detect_people(current_frame)
			frame_proccesed = current_frame
			for (xA, yA, xB, yB) in pick:	
				print("PERSONA detectada")
				# Capturamos el tiempo actual, la primera vez que aparece el sujeto
				if primeraVez == 0:
					tiempoActual = datetime.now()
					primeraVez = 1

				tiempoAux = datetime.now()
				tiempoDiff = date_diff_in_Seconds(tiempoAux, tiempoActual)	
				imageF = 0
				if(tiempoDiff > 2):
					print("Tiempo INADECUADO en la zona de peligro: ",tiempoDiff)
					if moveX(xA, yA, pick, frame_proccesed) > 1 or moveY(xA, yA, pick, frame_proccesed) > 1:

						# Captura de la persona mientras se encuentra dentro de la zona.						
						if(tiempoDiff % 5 == 0):
							frame_proccesed = drawDetection(current_frame, xA, yA, xB, yB, contImages)
							contImages += 1
							imageF = 1
						# Captura de la persona al realizar movimientos muy cortos(no esta de paso)
						if moveX(xA, yA, pick, frame_proccesed) == 2 or moveY(xA, yA, pick, frame_proccesed) == 2:
								print("Movimiento corto")
								if imageF is not 1:
									frame_proccesed = drawDetection(current_frame, xA, yA, xB, yB, contImages)
									contImages += 1

				else:
						print("Tiempo NORMAL en la zona de peligro: ", tiempoDiff)
	
				# Actualizamos la nuevas coordenadas
				coordenadasAnteriores[0] = xA
				coordenadasAnteriores[1] = yA
				coordenadasAnteriores[2] = xB
				coordenadasAnteriores[3] = yB			
		cv2.imshow('Current_frame', current_frame)
			# Movimiento extranio

	else:
		# Capturamos los frames sucesivos
		for x in  range(0,5):
			ret, current_frame = cap.read()

	# Sentencias para salir, pulsa 's' y sale
	k = cv2.waitKey(30) & 0xff
	if k == ord("s"):
		break

# Liberamos la camara y cerramos todas las ventanas
cap.release()
cv2.destroyAllWindows()
