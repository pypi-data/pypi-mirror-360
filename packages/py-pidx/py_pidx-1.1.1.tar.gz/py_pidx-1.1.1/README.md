# py_pidx

[![PyPI version](https://img.shields.io/pypi/v/py_pidx.svg)](https://pypi.org/project/py_pidx/)
[![License](https://img.shields.io/github/license/mehrabmahdian/py_pidx)](https://github.com/mehrabmahdian/py_pidx/blob/main/LICENSE)
[![Code Quality](https://img.shields.io/badge/code%20quality-A-brightgreen.svg)](https://github.com/mehrabmahdian/py_pidx)
[![Documentation](https://img.shields.io/badge/docs-available-blue.svg)](#documentation)

**`py_pidx`** is an advanced Python library for PID control that provides robust, real-world-ready features, including:

- 🧠 **Gain scheduling**
- 🧾 **Deadband handling (error & output)**
- 🚦 **Anti-windup**
- 🔁 **Slew rate limiting**
- 🌀 **Derivative filtering**
- 🧮 **Feedforward term**
- 🧪 **Precision control with dynamic time steps**
- 🔄 **Integral and derivative-on-measurement option**


---

## 🔧 Installation

```bash
pip install py_pidx
```

| Feature                   | Description                                                        |
|---------------------------|--------------------------------------------------------------------|
| `Kp`, `Ki`, `Kd`          | Tunable proportional, integral, and derivative gains               |
| `GainScheduler`           | Dynamically adjust PID gains at runtime                            |
| Deadbands                 | Zero out small control efforts or errors to reduce actuator jitter |
| Anti-windup               | Prevents runaway integral values during saturation                 |
| Derivative on Measurement | Optionally compute D-term from PV instead of error                 |
| Integral on Measurement   | Optionally compute I-term on process variable instead of error     |
| Low-pass Filtering        | Smooths noisy derivative term using alpha filtering                |
| Feedforward               | Optional term to improve open-loop response                        |
| Slew Rate Limiting        | Prevents rapid output changes that may shock actuators             |


## 🔧 Basic Usage
``` python
from py_pidx import PID

pid = PID(Kp=1.2, Ki=0.5, Kd=0.05, setpoint=100)

while True:
    pv = read_sensor()  # Your process variable
    control_signal = pid.run(pv)
    send_to_actuator(control_signal)
    time.sleep(0.01)
```

## 🎯 Advanced Features

### Gain Scheduling 

``` python
from py_pidx.gain_scheduler import GainScheduler

class MyScheduler(GainScheduler):
    def get_gains(self, pv):
        if pv < 10:
            return (2.0, 0.1, 0.01)
        elif pv < 20:
            return (1.5, 0.05, 0.005)
        else:
            return (1.0, 0.01, 0.001)

pid = PID(gain_scheduler=MyScheduler())
```

### Deadbands

``` python
pid = PID(
    output_deadband_limits=(-0.1, 0.1),
    error_deadband_limits=(-0.05, 0.05)
)
``` 
### Anti-Windup and Slew Rate

``` python
pid = PID(
    Ki=0.3,
    anti_windup=True,
    max_output_rate=10.0  # Max 10 units/sec change
)
```
### Derivative Filtering and Feedforward

``` python
pid = PID(
    Kd=0.2,
    derivative_filter=0.3,  # Low-pass smoothing factor (0.0–1.0)
    feedforward=1.5
)
``` 

###  Testing / Resetting / Toggling

``` python
pid.set_auto_mode(False)    # Pause control
pid.set_auto_mode(True)     # Resume control
pid.reset()                 # Clear internal state
```

## PID Controller Methods

| Method                        | Description                                |
|------------------------------|--------------------------------------------|
| `run(pv, delta_time=None)`    | Compute the control output                 |
| `reset()`                     | Clear internal PID state                   |
| `set_auto_mode(enabled)`      | Enable/disable PID control loop            |
| `set_output_limits(min, max)` | Clamp controller output                    |
| `__repr__()`                  | Debug string with current gains and output |

## 📄 Documentation
👉 Full API Reference and usage examples:
📖 https://mehrabmahdian.github.io/py_pidx/

## 🧠 Why Use py_pidx?

- Designed with real control systems in mind
- Great for robotics, automation, process control, and simulations
- Extensible and highly configurable
- Clean, readable, and well-documented

## 📃 License
This project is licensed under the terms of the MIT license.

## 🤝 Contributing
Pull requests and feature ideas are welcome!
Please open an issue for bugs or enhancement suggestions.


## ⭐️ Show Your Support
If you find this library useful, consider starring the repo or sharing it with others in the controls/automation community!

## 📬 Contact
Maintained by Mehrab Mahdian.

If you have questions, feature requests, or would like to collaborate, feel free to reach out:

📧 **Email:**  
[memahdian@outlook.com](mailto:memahdian@outlook.com)  
[mehrab.mahdian@taltech.ee](mailto:mehrab.mahdian@taltech.ee)

🧑‍💻 **GitHub:** [@mehrabmahdian](https://github.com/mehrabmahdian)  
💼 **LinkedIn:** [Mehrab Mahdian](https://www.linkedin.com/in/mehrab-mahdian/)

I’m always happy to connect with fellow developers, engineers, and researchers.

