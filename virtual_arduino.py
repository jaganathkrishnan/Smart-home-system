class VirtualArduino:
    def __init__(self):
        self.led_state = False  # Simulate an LED

    def turn_on_led(self):
        self.led_state = True
        print("LED turned ON")

    def turn_off_led(self):
        self.led_state = False
        print("LED turned OFF")

    def get_led_state(self):
        return self.led_state

    def cleanup(self):
        self.turn_off_led()
        print("LED turned OFF during cleanup")
