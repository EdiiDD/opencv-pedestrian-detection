# Importación de librerías
import numpy as np
import urllib.request
import random as rng
from datetime import datetime, time
import cv2
import imutils
import time


# TODO Line iterator para saber si mi bbox esta dentro de los pixeles de la linea

# Capturamos el vídeo de una camara Web IP
url = "../video/7.mp4"
urlWebCam = "http://91.221.52.198:82/mjpg/video.mjpg"
cap = cv2.VideoCapture(urlWebCam) 

# Color del rectangulo
color = (0,0,0)
colorAzul  = (255,0,0)
colorVerde = (0,255,0)
colorRojo = (0,0,255)

# Grosor de figuras
grosor = 0
grosorNormal = 2
grosoAlerta = 3

# Posiciones de la linea de seguridad
x1 = 330
y1 = 0
x2 = 330
y2 = 380

# Tiempo que esta la persona en la zona de seguridad
zonaProhibida = False
currentMillis = 0
endMillis = 0
textoProhibido =  "Tiempo en zona de seguridad " , currentMillis

# Parametros de texto indicativo
font                   = cv2.FONT_HERSHEY_COMPLEX_SMALL
topLeftCornerOfText = (10,20)
topLeftCornerOfText1 = (10,50)
bottomLeftCornerOfText = (20,340)
fontScale              = 0.5
fontColor              = colorVerde
lineType               = 1

# Texto a imprimir
textoSinPeligro = "Sin Peligro"
textoPeligro = "PELIGRO"
texto = textoSinPeligro

# Función para calucar la diferencia en segundos
def date_diff_in_Seconds(dt2, dt1):
	timedelta = dt2 - dt1
	return timedelta.days * 24 * 3600 + timedelta.seconds

# Capturar el tiempo actual
tiempoActual = 0


# Capturamos el primer frame
ret, current_frame = cap.read()
previuos_frame = current_frame

fgbg = cv2.createBackgroundSubtractorKNN()
fgbg.setDetectShadows(True)

while(1):

	# Capturamos el tiempo actual
	tiempoActual = datetime.now()

	# Capturamos los frames sucesivos
	ret, current_frame = cap.read()

	# Si el video termina
	if (not ret):
		break

	# Mostramos linea de seguridad
	cv2.line(current_frame, (x1, y1), (x2, y2), colorRojo, grosorNormal)

	# Clean Frame
	gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.erode(gray, np.ones((5,5)), 16)
	aux = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, np.ones((11,11)))



	gray = cv2.inRange(gray, 20, 255)
	gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 1)

	fgmask = fgbg.apply(gray)
	blur = cv2.medianBlur(fgmask, 5)

	
	thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY)[1]  # shadow of MOG@ is grey = 127
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

	closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)  # fill any small holes
	opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)  # remove noise
	
	#cv2.imshow('Frame Diff', opening)
	aux = cv2.Canny(opening.copy(), 5, 8)
	contours,_ = cv2.findContours(aux, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


	# Miramos cada uno de los contornos y, si no es ruido, dibujamos su Bounding Box sobre la imagen original
	timeDiff = 0
	for c in contours:
		if cv2.contourArea(c) >= 500:
			# Guardamos las dimensiones de la Bounding Box
			posicion_x,posicion_y,ancho,alto = cv2.boundingRect(c) 
			
			if ancho >= 50 and alto >= 50:
				#Tiempo que esta en la zona
				if posicion_x + ancho >= x1 and posicion_x + ancho >= x2:
					color = colorRojo
					fontColor = colorRojo
					grosor = grosoAlerta
					texto = textoPeligro
					# El tiempo se actualiza cada vez que entramos a la zona de seguridad
					if not zonaProhibida:
						currentMillis = datetime.now()
					zonaProhibida = True

				else:
					color = colorVerde
					fontColor = colorVerde
					grosor = grosorNormal
					texto = textoSinPeligro
					zonaProhibida = False
					endMillis =  datetime.now()
			
			cv2.rectangle(current_frame, (posicion_x,posicion_y), (posicion_x+ancho,posicion_y+alto), color, grosor) #Dibujamos la bounding box


	if zonaProhibida:
		#Mostramos texto indicativo 
		endMillis =  datetime.now()
		timeDiff = date_diff_in_Seconds(endMillis, currentMillis)
		cv2.putText(current_frame,"{texto}".format(texto=texto), topLeftCornerOfText, cv2.FONT_HERSHEY_SIMPLEX, fontScale, fontColor, lineType) #Peligro
		cv2.putText(current_frame,"Tiempo dentro de la zona de seguridad: {time}".format(time=timeDiff), topLeftCornerOfText1, cv2.FONT_HERSHEY_SIMPLEX, fontScale, fontColor, lineType) #Peligro

	else:
		# Mostramos texto indicativos
		cv2.putText(current_frame, texto, topLeftCornerOfText, cv2.FONT_HERSHEY_SIMPLEX, fontScale, fontColor, lineType) 
	
	cv2.putText(current_frame, str(tiempoActual), bottomLeftCornerOfText, cv2.FONT_HERSHEY_SIMPLEX, fontScale, colorAzul, lineType) 
	
	#frame_diff = imutils.resize(frame_diff, width=min(400, current_frame.shape[1]))
	current_frame = imutils.resize(current_frame, width=min(400, current_frame.shape[1]))
	# Mostramos las capturas
	#cv2.imshow('Frame Diff', frame_diff)
	cv2.imshow('Current_frame',current_frame)

	
	# Sentencias para salir, pulsa 's' y sale
	k = cv2.waitKey(30) & 0xff
	if k == ord("s"):
		break

# Liberamos la cámara y cerramos todas las ventanas
cap.release()
cv2.destroyAllWindows()
