import socket
from InquirerPy import inquirer

# ----------------------
# Discover NodeMCU devices on your local network
# ----------------------

def discover_devices(subnet="192.168.1.", port=1234):
    print("[Scanner] Looking for NodeMCU devices on the network...")

    found_ips = []
    for i in range(2, 255):
        ip = subnet + str(i)
        try:
            s = socket.socket()
            s.settimeout(0.2)
            s.connect((ip, port))
            s.sendall(b"ping()")
            resp = s.recv(1024).decode()
            if "pong" in resp:
                found_ips.append(ip)
            s.close()
        except:
            pass

    if not found_ips:
        print("⚠️  No NodeMCU devices found on network.")
        exit(1)
    return found_ips

# Scan subnet (update subnet if needed)
devices = discover_devices()

# Let user select
selected_ip = inquirer.select(
    message="Select NodeMCU device:",
    choices=devices,
).execute()

print(f"✅ Selected NodeMCU at {selected_ip}")

# ----------------------
# Send commands to selected NodeMCU
# ----------------------

def send_command(command):
    port = 1234
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((selected_ip, port))
        s.sendall(command.encode())
        data = s.recv(1024)
        print("[NodeMCU Response]:", data.decode())

# Movement commands
def move_forward(distance):
    send_command(f"move_forward({distance})")

def move_backward(distance):
    send_command(f"move_backward({distance})")

def turn_left(angle):
    send_command(f"turn_left({angle})")

def turn_right(angle):
    send_command(f"turn_right({angle})")

def stop():
    send_command("stop()")

def beep():
    send_command("beep()")

def set_speed(value):
    send_command(f"set_speed({value})")

def read_distance():
    send_command("read_distance()")

def wait(seconds):
    send_command(f"wait({seconds})")

# IMU functions
def read_gyroscope():
    send_command("read_gyroscope()")

def read_accelerometer():
    send_command("read_accelerometer()")

def calibrate_imu():
    send_command("calibrate_imu()")

def balance_upright(kp=1.0, ki=0.0, kd=0.0, target_angle=0.0):
    send_command(f"balance_upright({kp},{ki},{kd},{target_angle})")

# Example usage test
if __name__ == "__main__":
    move_forward(10)
    turn_left(90)
    beep()