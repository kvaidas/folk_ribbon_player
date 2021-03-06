import cv2
import numpy
import time
from matplotlib import pyplot as plt
import mido

# Image settings
camera = cv2.VideoCapture(1)
capture_interval = 0
#resize_multiplier = .05
resize_multiplier = 0.2
brightness_threshold = 180
skip_img_left = 25 # Ignore left side of image in percents
skip_img_right = 25 # Ignore right side of image in percents
max_display_rows = 10 # Maximum number of ribbon rows to display in pixels

# Note settings
note_min = 40
note_max = 100
delta_note = 12
note_multiplier = 4
note_repetition_threshold = 1

# MIDI settings
controller_delta = 64
attrib_coef = (127 - controller_delta) / brightness_threshold
lfo_id = 26
cutoff_id = 43
lfo_coef = 2
lfo_speed_id = 24

# Other settings
debug = False
old_notes = {}
note_counter={}

    
midi_devices = mido.get_output_names()
if len(midi_devices) == 1:
    midi_device = midi_devices[0]
else:
    print('Available MIDI output devices:')
    for item in midi_devices:
        print(midi_devices.index(item), item)
    device_number = int(
        input('Select MIDI output device: ')
    )
    midi_device = midi_devices[device_number]
print('Using MIDI device "' + midi_device + '"')
port = mido.open_output(midi_device)


def show_rgb_equalized(image):
    channels = cv2.split(image)
    eq_channels = []
    for ch, color in zip(channels, ['B', 'G', 'R']):
        eq_channels.append(cv2.equalizeHist(ch))

    eq_image = cv2.merge(eq_channels)
    # eq_image = cv2.cvtColor(eq_image, cv2.COLOR_BGR2RGB)
    #return image
    return eq_image

def process_notes(new_notes):
    global old_notes
    #if old_notes.keys() != new_notes.keys():
    print(new_notes.keys())
      
    for note, colors in new_notes.items():

        

        if note_counter.get(note) is None:
            note_counter[note] = 0
            
        note_counter[note]=note_counter[note]+1;
        if note_counter[note]<=note_repetition_threshold:
            continue;
        
        note_counter[note]=0
        if (note not in old_notes):
            note_normalized = int(
                note_min + (note / image.shape[1]) * (note_max - note_min)
            )
            # note = note * note_multiplier + delta_note

            note = note_normalized
            print(note)
            message = mido.Message('note_on', channel=1, note=note, velocity=127)
            port.send(message)

            controller_value = int(colors[0] * attrib_coef) + controller_delta
            current_control = cutoff_id
            message = mido.Message('control_change', channel=1, control=current_control, value=controller_value)
            port.send(message)

            controller_value = int(colors[1] * attrib_coef) + controller_delta
            controller_value = int(controller_value/lfo_coef)
            message = mido.Message('control_change', channel=1, control=lfo_id, value=controller_value)
            port.send(message)

            controller_value = int(colors[2] * attrib_coef) + controller_delta
            controller_value = int(controller_value)
            message = mido.Message('control_change', channel=1, control=lfo_id, value=controller_value)
            port.send(message)

    time.sleep(0.150)

    for note, colors in new_notes.items():
        if 0 <= note <= 127:
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
    if debug:
        cv2.imwrite('image01_original.png', image)

    # Resize image
    image = cv2.resize(image, resized_dimendions)
    if debug:
        cv2.imwrite('image02_resized.png', image)

    # Get a few pixel strips from the image for display on a screen
    image_part = []
    for i in range(1,max_display_rows):
        image_part.append(image[i])
#    image = numpy.array([image[0]])

    
    # Normalize lighting
    image = numpy.array(image_part)
    image = show_rgb_equalized(image)

    if debug:
        cv2.imwrite('image03_slice.png', image)

    # Display image
#    cv2.imshow('image',image)
#    cv2.waitKey(1)
    

    hor_width = len(image[0])
    min_x = int(hor_width * skip_img_left / 100)
    max_x = int(hor_width - hor_width * skip_img_right / 100)
    
    # Show red rulers - notes are detected only between them
    image[0:max_display_rows, min_x] = (0,0,255)
    image[0:max_display_rows, max_x] = (0,0,255)
    
    # Highlight the line below the reading line
    image[1, 0:hor_width] = (0,255,0)

    # Full screen
    cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.imshow("window", image)
    cv2.waitKey(1)

    # Get a single row
    image = numpy.array([image[0]])

    # Print strip as numbers
    notes_detected = {}
    for number, colors in enumerate(image[0]): 
        if number >= min_x and \
           number <= max_x and \
           image[0][number][0] < brightness_threshold and \
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

# cv2.imshow('test',image)
# cv2.waitKey(0)

