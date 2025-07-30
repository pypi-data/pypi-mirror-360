import cv2
from rubu import temas

# Connect to the device (via hostname or IP address)
device = temas.Connect(hostname="temas")
# Alternatively: device = temas.Connect(ip_address="192.168.4.4")

# Initialize control class
control = temas.Control()

# Measure distance (laser, in cm)
distance = control.distance()
print(f"Measured distance: {distance} cm")

# Move to a specific position (Pan, Tilt)
control.move_pos(60, 30)

# Initialize camera (Visual Port: 8081, ToF Port: 8084)
camera = temas.Camera(port=8081)
camera.start_thread()

while True:
    try:
        frame = camera.get_frame()
        if frame is not None:
            cv2.imshow('Visual Camera', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting camera stream...")
            break
    except Exception as e:
        print(f"Error retrieving camera frame: {e}")

# Reset camera and control
control.move_home()
camera.stop_thread()
cv2.destroyAllWindows()
print("Program terminated.")