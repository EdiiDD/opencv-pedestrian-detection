import cv2
import sys

# Set up tracker.
# Instead of MIL, you can also use
# BOOSTING, KCF, TLD, MEDIANFLOW or GOTURN

tracker = cv2.TrackerMIL_create()

# Read video
url = "prueba1.mp4"
video = cv2.VideoCapture(url)

# Exit if video not opened.
if not video.isOpened():
    print ("Could not open video")
    sys.exit()

# Read first frame.
ok, frame = video.read()
if not ok:
    print ('Cannot read video file')
    sys.exit()

# Define an initial bounding box
bbox = (287, 23, 86, 320)

# Uncomment the line below to select a different bounding box
# bbox = cv2.selectROI(frame, False)

# Initialize tracker with first frame and bounding box
ok = tracker.init(frame, bbox)

## Select boxes
bboxes = []
colors = [] 

while True: 
	bbox = cv2.selectROI('MultiTracker', frame) 
	bboxes.append(bbox)
	colors.append((randint(0, 255), randint(0, 255), randint(0, 255)))	
	k = cv2.waitKey(0) & 0xFF
	if (k == 113): # q is pressed
		break
	# Specify the tracker type
	trackerType = "CSRT"
	
	# Create MultiTracker object
	multiTracker = cv2.MultiTracker_create()
	
	# Initialize MultiTracker 
	for bbox in bboxes:
		multiTracker.add(createTrackerByName(trackerType), frame, bbox)

	# Process video and track objects
	while cap.isOpened():
		success, frame = cap.read()
		if not success:
			break
   
		# get updated location of objects in subsequent frames
		success, boxes = multiTracker.update(frame)
	
		# draw tracked objects
		for i, newbox in enumerate(boxes):
			p1 = (int(newbox[0]), int(newbox[1]))
			p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
			cv2.rectangle(frame, p1, p2, colors[i], 2, 1)
		
		# show frame
		cv2.imshow('MultiTracker', frame)

		# quit on ESC button
		if cv2.waitKey(1) & 0xFF == 27:  # Esc pressed
			break