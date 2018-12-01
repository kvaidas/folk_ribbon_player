import cv2
import numpy
import time

camera = cv2.VideoCapture(0)
capture_interval = 0.500
resize_multiplier = .02
brightness_threshold = 180
debug = False
old_notes = {}

def process_notes(new_notes):
    global old_notes
    if old_notes.keys() != new_notes.keys():
        print(new_notes)
        old_notes = new_notes

while True:
    # Capture image
    retval, image = camera.read()
    resized_dimendions = (
        int(image.shape[0] * resize_multiplier),
        int(image.shape[1] * resize_multiplier)
    )
    if debug: cv2.imwrite('image01_original.png', image)

    # Resize image
    image = cv2.resize(image, resized_dimendions)
    if debug: cv2.imwrite('image02_resized.png', image)

    # Get a single pixel strip from the image
    image = numpy.array([image[0]])
    if debug: cv2.imwrite('image03_slice.png', image)

    # Print strip as numbers
    notes_detected = {}
    for number, colors in enumerate(image[0]):
        if image[0][number][0] < brightness_threshold and \
           image[0][number][1] < brightness_threshold and \
           image[0][number][2] < brightness_threshold:
            notes_detected[number] = (
                image[0][number][0],
                image[0][number][1],
                image[0][number][2]
            )
    process_notes(notes_detected)

    # Wait until next note has arrived
    time.sleep(capture_interval)

#cv2.imshow('test',image)
#cv2.waitKey(0)