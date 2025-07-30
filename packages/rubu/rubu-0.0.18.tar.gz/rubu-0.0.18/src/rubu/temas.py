import socket
import urllib.request
import cv2
from threading import Thread, Lock
import threading
from datetime import datetime
import numpy as np


class Connect:
    """This class alows the Temas connection.
    """

    def __init__(self, hostname="temas", ip_address=""):
        """Initial values of class Connect."""
        global ip
        ip = ""
        if ip_address == "":
            ip = self.get_ip_from_hostname(hostname)
        else:
            ip = ip_address
        self.ip = ip
        print(ip)

    def get_ip_from_hostname(self, hostname, max_attempts=4):
        """Attempts to determine the IP address of the hostname."""
        for attempt in range(max_attempts):
            try:
                ip = socket.gethostbyname(hostname)
                return ip
            except socket.gaierror:
                print(f"Attempt {attempt + 1}/{max_attempts}: Could not resolve hostname '{hostname}'. Retrying...")
        print(f"Error: Could not resolve hostname '{hostname}' after {max_attempts} attempts.")
        return None


class Socket:
    """This class send commands to Temas
    """

    def __init__(self, port, ip_address=""):
        """Initial values of class Socket."""
        global ip
        if ip_address == "":
            self.ip = ip
        else:
            self.ip = ip_address
        self.port = port
        self.buffer = ""
        self.data = ""

    def send_cmd(self, command, text=False, path=""):
        """Send commands

        :param command: A command is given
        :type command: List, optional
        :return: Data of socket :class:`temas.send_cmd`
        :raises: Exception
        """
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.ip, self.port))
            self.client.sendall((command).encode())
            if text:
                response = ''
                while True:
                    buffer = self.client.recv(4096)
                    if not buffer:
                        break

                    response += buffer.decode("utf-8")

                now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                filename = path + now + '-laser.ply'
                with open(filename, 'w') as f:
                    text2 = response.replace("\\n", "\n")
                    text2 = text2.replace("b'", "")
                    text2 = text2.replace("'", "")
                    f.write(text2)
                    # f.write(self.data)
                self.client.close()
            else:
                self.buffer = self.client.recv(4096)
                self.data = self.buffer.decode()
                self.client.close()
        except:
            raise Exception("Sending failed - IP: " + self.ip + " PORT: " + str(self.port))
        return self.data


class Camera:
    """This class allows the control of camera using urllib."""

    def __init__(self, port=8081, ip_address=""):
        """Initializes the Camera class"""
        if ip_address == "":
            global ip
            self.ip = ip
        else:
            self.ip = ip_address

        self.port = port
        self.stream = bytes()
        self.html_page = f"http://{self.ip}:{self.port}/stream.mjpg"
        self.file = urllib.request.urlopen(self.html_page)
        self.frame = None
        self.kill = True
        self.lock = Lock()
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True

    def update(self):
        """Continuously fetches frames from the MJPEG stream."""
        while not self.kill:
            try:
                chunk = self.file.read(4096)
                if not chunk:
                    continue
                self.stream += chunk
                a = self.stream.find(b'\xff\xd8')  # Start of JPEG
                b = self.stream.find(b'\xff\xd9')  # End of JPEG
                if a != -1 and b != -1:
                    jpg = self.stream[a:b + 2]
                    self.stream = self.stream[b + 2:]
                    img_array = np.frombuffer(jpg, dtype=np.uint8)
                    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    if frame is not None:
                        with self.lock:
                            self.frame = frame
            except Exception as e:
                print(f"Camera stream error: {e}")
                continue

    def start_thread(self):
        """Starts the thread to fetch frames."""
        self.kill = False
        self.thread.start()

    def stop_thread(self):
        """Stops the thread."""
        self.kill = True
        self.file.close()

    def get_frame(self):
        """Returns the most recent frame

        :return: Frame
        :rtype: numpy.ndarray or None
        """
        with self.lock:
            return self.frame

    def set_exposure_time(self, microseconds):
        """Set exposure time of visual camera 50-33000µs
        :return: Exposure time
        :rtype: String
        """
        url = "http://" + self.ip + ":" + str(self.port) + "/set_exposure/" + str(microseconds)
        response = urllib.request.urlopen(url)
        return response.read().decode()

    def set_brightness(self, brightness_percent):
        """Set brightness of visual camera 0-100
        :return: Brightness
        :rtype: String
        """
        url = "http://" + self.ip + ":" + str(self.port) + "/set_brightness/" + str(brightness_percent)
        response = urllib.request.urlopen(url)
        return response.read().decode()

    def set_saturation(self, saturation_percent):
        """Set saturation of visual camera 0-100
        :return: Saturation
        :rtype: String
        """
        url = "http://" + self.ip + ":" + str(self.port) + "/set_saturation/" + str(saturation_percent)
        response = urllib.request.urlopen(url)
        return response.read().decode()

    def set_contrast(self, contrast_percent):
        """Set contrast of visual camera 0-100
        :return: Contrast
        :rtype: String
        """
        url = "http://" + self.ip + ":" + str(self.port) + "/set_contrast/" + str(contrast_percent)
        response = urllib.request.urlopen(url)
        return response.read().decode()

    def set_lens_position(self, lens_position_percent):
        """Set lens position of visual camera 0-100
        :return: Lens position
        :rtype: String
        """
        url = "http://" + self.ip + ":" + str(self.port) + "/set_lens_position/" + str(lens_position_percent)
        response = urllib.request.urlopen(url)
        return response.read().decode()

    def set_gain(self, gain_value):
        """Set gain of visual camera 1.123-16.0
        :return: Gain
        :rtype: String
        """
        url = "http://" + self.ip + ":" + str(self.port) + "/set_gain/" + str(float(gain_value))
        response = urllib.request.urlopen(url)
        return response.read().decode()


class Control:
    """This class alows the control of motors and laser.
    """

    def __init__(self, port=8082, ip_address=""):
        self.lock = threading.Lock()
        self.port_control = port
        global ip
        self.ip = ip if ip_address == "" else ip_address

        try:
            self.temas = Socket(self.port_control, ip_address=self.ip)
        except Exception as e:
            print(f"Fehler beim Erstellen des Sockets: {e}")

    def get_pcl(self, path):
        """Retrieve the latest point cloud from the laser scan (e.g., located at C:/temp/).

        :return: .ply file
        """
        self.temas.send_cmd('get_pcl\n', text=True, path=path)

    def distance(self):
        """Laser distance measurment

        :return: Value of the distance [cm]
        :rtype: String
        """
        value = self.temas.send_cmd('distance\n')
        return value

    def mean_distance(self):
        """Mean laser distance measurement

        :return: Value of the mean_distance [cm]
        :rtype: String
        """
        value = self.temas.send_cmd('distance_mean_fix_number\n')
        return value

    def move_pos(self, phi, theta):
        """Move to the specified pan and tilt angles in degrees (e.g., 12.5, 11) with a step size of 0.5°.

        :return: Status message indicating if the move was successful. Returns True if successful.
        :rtype: String
        """
        if (phi * 2) % 1 != 0 or (theta * 2) % 1 != 0:
            return "Error: Only values in 0.5° steps are allowed."
        value = self.temas.send_cmd('move_pos|' + str(phi) + '|' + str(theta) + '|' + '\n')
        return value

    def get_pos(self):
        """Get motor positions

        :return: pan, tilt positions [°]
        :rtype: String
        """
        value = self.temas.send_cmd('get_position\n')
        return value

    def move_home(self):
        """Move to home position"""
        value = self.temas.send_cmd('move_home\n')
        return value

    def move(self, direction):
        """Sends a movement command to the motor."""
        with self.lock:
            value = self.temas.send_cmd(f"move_{direction}\n")
        return value

    def move_threaded(self, direction):
        """Starts the movement in a separate thread."""
        threading.Thread(target=self.move, args=(direction,), daemon=True).start()

    def move_right(self):
        """Move motor right in 1° steps"""
        self.move_threaded("right")

    def move_left(self):
        """Move motor left in 1° steps"""
        self.move_threaded("left")

    def move_up(self):
        """Move motor up in 1° steps"""
        self.move_threaded("up")

    def move_down(self):
        """Move motor down in 1° steps"""
        self.move_threaded("down")

    def move_right_fine(self):
        """Move motor right in 0.5° steps"""
        self.move_threaded("right_fine")

    def move_left_fine(self):
        """Move motor left in 0.5° steps"""
        self.move_threaded("left_fine")

    def move_up_fine(self):
        """Move motor up in 0.5° steps"""
        self.move_threaded("up_fine")

    def move_down_fine(self):
        """Move motor down in 0.5° steps"""
        self.move_threaded("down_fine")

    def start_point_cloud_scan(self, theta1, theta2, phi1, phi2, color=1):
        """
        Starts a point cloud scan between the specified pan and tilt angle ranges.

        :param theta1: Minimum elevation angle in degrees (-30 to 90, step size 0.5°)
        :param theta2: Maximum elevation angle in degrees (-30 to 90, step size 0.5°)
        :param phi1: Minimum azimuth angle in degrees (-60 to 60, step size 0.5°)
        :param phi2: Maximum azimuth angle in degrees (-60 to 60, step size 0.5°)
        :param color: Color mode (default = 1)
        :return: Status message indicating if the scan was started successfully. Returns True if successful.
        :rtype: String
        """

        # Hilfsfunktion zur Schrittgrößenprüfung
        def is_valid_angle(value, min_val, max_val):
            return min_val <= value <= max_val and (value * 2) % 1 == 0

        if not all([
            is_valid_angle(theta1, -30, 90),
            is_valid_angle(theta2, -30, 90),
            is_valid_angle(phi1, -60, 60),
            is_valid_angle(phi2, -60, 60)
        ]):
            return "Error: Angles must be in valid ranges and in 0.5° steps."
        value = self.temas.send_cmd(
            'start_point_cloud_scan|' + str(theta1) + '|' + str(theta2) + '|' + str(phi1) + '|' + str(phi2) + '|' + str(
                color) + '|' + '\n')
        return value

    def stop_point_cloud_scan(self):
        """Stop point cloud scan

        :return: Status message indicating if the scan was stopped successfully. Returns True if successful.
        :rtype: String
        """
        value = self.temas.send_cmd('stop_point_cloud_scan\n')
        return value

    def get_point_cloud_scan_percent(self):
        """Point cloud scan status in perecent

        :return: Point cloud scan status [%]
        :rtype: String
        """
        value = self.temas.send_cmd('get_point_cloud_scan_percent\n')
        return value


class Common:
    """This class included the common settings of Temas"""

    def __init__(self, port=8083, ip_address=""):
        """Initial values of class Common"""
        global ip
        if ip_address == "":
            self.ip = ip
        else:
            self.ip = ip_address
        self.port = port
        try:
            self.temas = Socket(self.port, ip_address=self.ip)
        except:
            pass

    def shutdown(self):
        """Shutdown Temas

        :return: Status message indicating if the shutdown was successful. Returns True if successful.
        :rtype: String
        """
        value = self.temas.send_cmd('temas_shutdown\n')
        return value

    def restart(self):
        """Restart Temas

        :return: Status message indicating if the restart was successful. Returns True if successful.
        :rtype: String
        """
        value = self.temas.send_cmd('temas_restart\n')
        return value

    def get_temperature(self):
        """Read Temperature of Temas

        :return: Temperature Temas [°C]
        :rtype: String
        """
        value = self.temas.send_cmd('get_temperature\n')
        return value

    def get_ip(self):
        """Get ip address of Temas

        :return: Ip address
        :rtype: String
        """
        global ip
        value = ip
        return value

    def get_sn(self):
        """Get serial number of Temas

        :return: Serial number is returned
        :rtype: String
        """
        value = self.temas.send_cmd('get_sn\n')
        return value

    def get_fw_version(self):
        """Get firmware version of Temas

        :return: Firmware version is returned
        :rtype: String
        """
        value = self.temas.send_cmd('get_fw_version\n')
        return value

    def get_hostname(self):
        """Get hostname of Temas

        :return: Hostname is returned
        :rtype: String
        """
        value = self.temas.send_cmd('get_hostname\n')
        return value

    def set_hostname(self, hostname):
        """Set hostname of Temas"""
        value = self.temas.send_cmd('set_hostname|' + str(hostname) + '|' + '\n')
        return value

    def get_port_camera(self):
        """Get port of Temas visual camera

        :return: Port from visual camera
        :rtype: String
        """
        value = self.temas.send_cmd('get_port_camera\n')
        return value

    def get_port_tof_camera(self):
        """Get port of Temas tof camera

        :return: Port from tof camera
        :rtype: String
        """
        value = self.temas.send_cmd('get_port_tof_camera\n')
        return value

    def get_port_common(self):
        """Get port of Temas common settings

        :return: Port from Temas common settings
        :rtype: String
        """
        value = self.temas.send_cmd('get_port_common\n')
        return value

    def get_port_control(self):
        """Get port of control device

        :return: Port from control device
        :rtype: String
        """
        value = self.temas.send_cmd('get_port_control\n')
        return value

    def get_mac(self):
        """Get the mac address of Temas

        :return: Returns the mac address
        :rtype: String
        """
        value = self.temas.send_cmd('get_mac\n')
        return value

    def get_laser_x_los(self):
        """Get the x value los of Laser in pixels relative to the visual frame.

        :return: Returns the x value los (px)
        :rtype: String
        """
        value = self.temas.send_cmd('get_laser_x_los\n')
        return value

    def get_laser_y_los(self):
        """Get the y value los of Laser in pixels relative to the visual frame.

        :return: Returns the y value los
        :rtype: String
        """
        value = self.temas.send_cmd('get_laser_y_los\n')
        return value

    def set_static_ip(self, ip, gateway, dns):
        """static ip /24 dhcp
        :param ip: IP address
        :param gateway: Default gateway for the network
        :param dns: DNS server address
        """
        self.temas.send_cmd('set_static_ip|' + str(ip) + '|' + str(gateway) + '|' + str(dns) + '|' + '\n')

    def set_direct_static_ip(self, ip):
        """static ip /24 without dhcp
        :param ip: IP address
        """
        self.temas.send_cmd('set_direct_static_ip|' + str(ip) + '|' + '\n')

    def near_mode_on(self):
        """tof near mode on"""
        self.temas.send_cmd('near_mode_on\n')

    def near_mode_off(self):
        """tof near mode off"""
        self.temas.send_cmd('near_mode_off\n')