# Importación de librerías
import numpy as np
import cv2
import urllib.request

#Capturamos el vídeo de una camara Web IP
#cap = cv2.VideoCapture("http://90.173.36.100:84/mjpg/video.mjpg")

# Capturamos el vídeo de una camara Web IP
url = "2.mp4"
tracker_type = "MIL"
cap = cv2.VideoCapture()

#Primer fotograma
ret, frame = cap.read()

# Llamada al método
fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=False)

# Deshabilitamos OpenCL, si no hacemos esto no funciona
cv2.ocl.setUseOpenCL(False)

# Creamos el tracker
tracker = cv2.TrackerMIL_create()

#Detectar en el primer frame
# Aplicamos el algoritmo
fgmask = fgbg.apply(frame)

# Copiamos el umbral para detectar los contornos
contornos = fgmask.copy()

# Para detectar los contronos de una "MONEDA" 
canny = cv2.Canny(fgmask, 100, 150)
#contornos, hierarchy = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Buscamos contorno en la imagen
contornos, hierarchy = cv2.findContours(contornos.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)


# Inicializamos el bbox
bbox = (287, 23, 86, 320)
bbox = cv2.selectROI(frame, False)
ok = tracker.init(frame, bbox)


while(1):

	# Leemos el siguiente frame
	ret, frame = cap.read()

	#Si el video termina
	if (not ret):
		break

	#Tiempo del video
	timer = cv2.getTickCount()

	#Actualizamos el tracker
	ok, bbox = tracker.update(frame)
	fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
	if ok:
		p1 = (int(bbox[0]), int(bbox[1]))
		p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
		cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
	else :
		# Tracking failure
		cv2.putText(frame, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)
		cv2.putText(frame, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2);

	# Display FPS on frame
	cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2);

	# Display result
	cv2.imshow("Tracking", frame)


	"""
	# Aplicamos el algoritmo
	fgmask = fgbg.apply(frame)

	# Copiamos el umbral para detectar los contornos
	contornos = fgmask.copy()

    # Para detectar los contronos de una "MONEDA" 
	canny = cv2.Canny(fgmask, 100, 150)
	#contornos, hierarchy = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	# Buscamos contorno en la imagen
	contornos, hierarchy = cv2.findContours(contornos.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

	# Recorremos todos los contornos encontrados
	for c in contornos:
		# Eliminamos los contornos más pequeños
		if cv2.contourArea(c) < 5000:
			continue

		# Obtenemos el bounds del contorno, el rectángulo mayor que engloba al contorno
		(x, y, w, h) = cv2.boundingRect(c)
		# Dibujamos el rectángulo del bounds
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		#cv2.drawContours(cap,c,-1,(0,0,255), 2)
		#cv2.drawContours(frame, [c], 0, (0, 255, 0), 2, cv2.LINE_AA)


	
	# Mostramos las capturas
	cv2.imshow('Camara',frame)
	#cv2.imshow('Umbral',fgmask)
	#cv2.imshow("canny", canny)
	"""
	# Sentencias para salir, pulsa 's' y sale
	k = cv2.waitKey(30) & 0xff
	if k == ord("s"):
		break

# Liberamos la cámara y cerramos todas las ventanas
cap.release()
cv2.destroyAllWindows()
