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
url = "../video/2.mp4"
urlWebCam = "http://91.221.52.198:82/mjpg/video.mjpg"
cap = cv2.VideoCapture(url) 

# Color del rectangulo
color = (0,0,0)
colorVerde = (0,255,0)
colorRojo = (0,0,255)

# Grosor de figuras
grosor = 0
grosorNormal = 2
grosoAlerta = 3

# Posiciones de la linea de seguridad
x1 = 330
y1 = 0
x2 = 190
y2 = 380

# Tiempo que esta la persona en la zona de seguridad
zonaProhibida = False
currentMillis = 0
endMillis = 0
textoProhibido =  "Tiempo en zona de seguridad " , currentMillis

# Parametros de texto indicativo
font                   = cv2.FONT_HERSHEY_COMPLEX_SMALL
topLeftCornerOfText = (10,20)
bottomLeftCornerOfText = (10,190)
fontScale              = 0.7
fontColor              = colorVerde
lineType               = 1

# Texto a imprimir
textoSinPeligro = "Sin Peligro!"
textoPeligro = "Peligro!!"
texto = textoSinPeligro

# Función para calucar la diferencia en segundos
def date_diff_in_Seconds(dt2, dt1):
  timedelta = dt2 - dt1
  return timedelta.days * 24 * 3600 + timedelta.seconds

# Capturamos el primer frame
ret, current_frame = cap.read()
previuos_frame = current_frame

currentMillis = datetime.now()
while(1):

	# Capturamos los frames sucesivos
	ret, current_frame = cap.read()

	# Si el video termina
	if (not ret):
		break

	# Mostramos texto indicativos
	cv2.putText(current_frame, texto, topLeftCornerOfText, cv2.FONT_HERSHEY_SIMPLEX, fontScale, fontColor, lineType) 

	# Mostramos linea de seguridad
	cv2.line(current_frame, (x1, y1), (x2, y2), colorRojo, grosorNormal)

	# Calculamos la diferencia entre las dos imagenes.
	current_frame_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
	previuos_frame_gray = cv2.cvtColor(previuos_frame, cv2.COLOR_BGR2GRAY)
	
	#current_frame_gray = imutils.resize(current_frame_gray, width=min(400, current_frame.shape[1]))
	#previuos_frame_gray = imutils.resize(previuos_frame_gray, width=min(400, current_frame.shape[1]))
	
	frame_diff = cv2.absdiff(current_frame_gray, previuos_frame_gray)
	frame_diff = cv2.erode(frame_diff, np.ones((8,8)), 5)


	
	# Buscamos los contornos
	frame_diff = cv2.GaussianBlur(frame_diff, (3, 3), 0)
	edges = cv2.inRange(frame_diff, 20, 255)
	#frame_diff = cv2.adaptiveThreshold(frame_diff, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 1)
	frame_diff = cv2.Canny(edges, 5, 10)
	contours,_ = cv2.findContours(edges,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

	# Miramos cada uno de los contornos y, si no es ruido, dibujamos su Bounding Box sobre la imagen original
	timeDiff = 0
	for c in contours:
		if cv2.contourArea(c) >= 500:
			# Guardamos las dimensiones de la Bounding Box
			posicion_x,posicion_y,ancho,alto = cv2.boundingRect(c) 
			
			if ancho >= 30 and alto >= 30:
				#Tiempo que esta en la zona
				if posicion_x >= x1 and posicion_x >= x2:
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
		cv2.putText(current_frame, str(timeDiff), bottomLeftCornerOfText, cv2.FONT_HERSHEY_SIMPLEX, fontScale, fontColor, lineType) #Peligro
	
	
	frame_diff = imutils.resize(frame_diff, width=min(400, current_frame.shape[1]))
	current_frame = imutils.resize(current_frame, width=min(400, current_frame.shape[1]))
	# Mostramos las capturas
	cv2.imshow('Frame Diff', frame_diff)
	cv2.imshow('Current_frame',current_frame)

	
	# Sentencias para salir, pulsa 's' y sale
	k = cv2.waitKey(30) & 0xff
	if k == ord("s"):
		break

# Liberamos la cámara y cerramos todas las ventanas
cap.release()
cv2.destroyAllWindows()
