from py_pidx import PID

def test_initialization_defaults():
    pid = PID()
    assert pid.Kp == 1.0
    assert pid.Ki == 0.0
    assert pid.Kd == 0.0
    assert pid.setpoint == 0.0
    assert pid.auto_mode is True

def test_basic_pid_output():
    pid = PID(Kp=1.0, Ki=0.5, Kd=0.1, sample_time=0)
    pv = 0.0
    pid.setpoint = 1.0
    # Run once, no integral or derivative yet (delta_time=1 for simplicity)
    output1 = pid.run(pv, delta_time=1.0)
    assert output1 > 0  # Positive control output

def test_output_limits():
    pid = PID(Kp=10, Ki=0, Kd=0, output_limits=(0, 5))
    pid.setpoint = 1.0
    output = pid.run(0.0, delta_time=1.0)
    assert 0 <= output <= 5  # Output is clipped

def test_output_deadband():
    pid = PID(Kp=1, Ki=0, Kd=0, output_deadband_limits=(-0.5, 0.5))
    pid.setpoint = 0.0
    # Output inside deadband
    output = pid.run(0.4, delta_time=1.0)
    assert output == 0.0

def test_error_deadband():
    pid = PID(Kp=1, Ki=0, Kd=0, error_deadband_limits=(-0.2, 0.2))
    pid.setpoint = 0.0
    # Error inside deadband, so output should be 0
    output = pid.run(0.1, delta_time=1.0)
    assert output == 0.0

def test_anti_windup_behavior():
    pid = PID(Kp=0, Ki=1.0, Kd=0, output_limits=(0, 10), anti_windup=True, sample_time=0)
    pid.setpoint = 10
    # Run with a large error to saturate output
    output1 = pid.run(0, delta_time=1.0)
    assert output1 == 10
    integral_before = pid._integral
    # Run again with no error change; integral should not increase because of anti-windup
    output2 = pid.run(0, delta_time=1.0)
    integral_after = pid._integral
    assert integral_after <= integral_before

def test_slew_rate_limiter():
    pid = PID(Kp=100, Ki=0, Kd=0, max_output_rate=5, sample_time=0)
    pid.setpoint = 1.0
    output1 = pid.run(0.0, delta_time=1.0)
    output2 = pid.run(0.0, delta_time=1.0)
    assert abs(output2 - output1) <= 5

def test_auto_mode_off():
    pid = PID(Kp=1.0, Ki=0.5, Kd=0.1, auto_mode=False)
    pid.setpoint = 1.0
    output_before = pid._output
    output = pid.run(0.0, delta_time=1.0)
    assert output == output_before  # Output does not change when auto_mode is off

def test_reset_function():
    pid = PID(Kp=1.0, Ki=1.0, Kd=1.0)
    pid.setpoint = 1.0
    pid.run(0.0, delta_time=1.0)
    pid.reset()
    assert pid._integral == 0.0
    assert pid._last_error == 0.0
    assert pid._last_output == 0.0
    assert pid._output == 0.0
    assert pid._last_pv is None
