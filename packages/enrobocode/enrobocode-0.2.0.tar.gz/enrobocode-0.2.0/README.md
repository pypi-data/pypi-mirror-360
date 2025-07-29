# enrobocode

English Robot Code — a simple, friendly Python library to control your NodeMCU-based robots with easy English-like commands.

## Example

```python
from enrobocode import nodemcu, speaker

speaker.speak("Hello, world!")
nodemcu.move_forward(10)
nodemcu.turn_left(90)
nodemcu.beep()
nodemcu.set_speed(70)
nodemcu.wait(2)
nodemcu.stop()
distance = nodemcu.read_distance()
print(f"Distance: {distance} cm")

nodemcu.balance_upright(kp=1.2, ki=0.0, kd=0.1, target_angle=0.0)
```
