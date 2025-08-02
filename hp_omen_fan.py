#!/usr/bin/env python3
import os
import sys
import argparse

# Base path for the hp-wmi hwmon interface (update the hwmon index if needed - "hwmon6", "hwmon7", etc.)
BASE_PATH = "/sys/devices/platform/hp-wmi/hwmon/hwmon5"
FAN1_INPUT = os.path.join(BASE_PATH, "fan1_input")
FAN2_INPUT = os.path.join(BASE_PATH, "fan2_input")
PWM1_ENABLE = os.path.join(BASE_PATH, "pwm1_enable")

def read_file(path):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except Exception as e:
        sys.stderr.write(f"Error reading {path}: {e}\n")
        return None

def write_file(path, value):
    try:
        with open(path, "w") as f:
            f.write(value)
        print(f"Wrote '{value}' to {path}")
        return True
    except PermissionError:
        sys.stderr.write(f"Permission denied when writing to {path}. Try running as root.\n")
    except Exception as e:
        sys.stderr.write(f"Error writing to {path}: {e}\n")
    return False

def show_status():
    print("=== HP Omen Fan Status ===")
    fan1 = read_file(FAN1_INPUT)
    fan2 = read_file(FAN2_INPUT)
    pwm_enable = read_file(PWM1_ENABLE)
    if fan1 is not None:
        print(f"Fan 1 Speed: {fan1} RPM")
    if fan2 is not None:
        print(f"Fan 2 Speed: {fan2} RPM")
    if pwm_enable is not None:
        if pwm_enable == "2":
            mode = "Automatic"
        elif pwm_enable == "0":
            mode = "Manual (Max RPM)"
        else:
            mode = "Unknown"
        print(f"PWM Control (pwm1_enable): {pwm_enable} ({mode})")

def set_pwm_enable(state):
    """Set pwm1_enable to a given state.
    
    On your system:
      - '2' sets Automatic fan control.
      - '0' sets manual control (Max RPM).
    """
    allowed = ["0", "2"]
    if state not in allowed:
        sys.stderr.write(f"Invalid state. Allowed values are: {', '.join(allowed)}.\n")
        sys.exit(1)
    if write_file(PWM1_ENABLE, state):
        print("pwm1_enable set successfully.")
    else:
        sys.exit(1)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="CLI tool for HP Omen fan control using hp_wmi hwmon interface"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Show status command
    subparsers.add_parser("status", help="Show current fan speeds and pwm control status")

    # Set command to change pwm1_enable value
    parser_set = subparsers.add_parser("set", help="Set pwm1_enable flag")
    parser_set.add_argument("state", choices=["0", "2"], 
                            help="State to set: '2' for Automatic, '0' for Manual (Max RPM)")

    return parser.parse_args()

def main():
    args = parse_arguments()

    if args.command == "status":
        show_status()
    elif args.command == "set":
        set_pwm_enable(args.state)
    else:
        sys.stderr.write("Unknown command.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
