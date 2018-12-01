import cv2
import numpy
import time
import mido

camera = cv2.VideoCapture(0)
capture_interval = 0.00
resize_multiplier = .02
brightness_threshold = 180
delta_note = 64
note_multiplier = 4
controller_delta = 64;
attrib_coef = (127 - controller_delta) / brightness_threshold
debug = False
old_notes = {}

lfo_id=26
cutoff_id=43
lfo_coef=2
lfo_speed_id=24

port = mido.open_output(mido.get_output_names()[2])


def process_notes(new_notes):
    global old_notes
    if old_notes.keys() != new_notes.keys():
        print(new_notes)
      
        for note, colors in new_notes.items():

            if note not in old_notes:
                note=note*note_multiplier+delta_note
                message = mido.Message('note_on', channel=1, note=note, velocity=127)
                port.send(message)
            
               # message = mido.Message('sysex', data=[1, 2, 3])
            controller_value = int(colors[0] * attrib_coef) + controller_delta

            current_control=cutoff_id
            
            message = mido.Message('control_change', channel=1, control=current_control, value=controller_value)
            port.send(message)

            controller_value = int(colors[1] * attrib_coef) + controller_delta
            current_control=lfo_id
            controller_value=int(controller_value/lfo_coef)
            message = mido.Message('control_change', channel=1, control=lfo_id, value=controller_value)
            port.send(message)

            controller_value = int(colors[2] * attrib_coef) + controller_delta
            current_control=lfo_speed_id
            controller_value=int(controller_value)
            message = mido.Message('control_change', channel=1, control=lfo_id, value=controller_value)
            port.send(message)

            
            
        time.sleep(0.150)
        for note, colors in new_notes.items():
            note=note*note_multiplier+delta_note
            message = mido.Message('note_off', channel=1, note=note, velocity=127)
            port.send(message)
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
