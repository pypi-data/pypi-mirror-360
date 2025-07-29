import time
from typing import Optional, Tuple
from py_pidx.gain_scheduler import GainScheduler


class PID:
    """
    PID controller implementing proportional-integral-derivative control with
    optional features including gain scheduling, deadbands, derivative filtering,
    anti-windup, slew rate limiting, feedforward control, and thread safety.

    Parameters
    ----------
    Kp : float, default=1.0
        Proportional gain coefficient.
    Ki : float, default=0.0
        Integral gain coefficient.
    Kd : float, default=0.0
        Derivative gain coefficient.
    gain_scheduler : Optional[GainScheduler], default=None
        Optional object to dynamically update PID gains based on process variable.
    setpoint : float, default=0.0
        Desired target value for the controlled variable.
    sample_time : float, default=0.01
        Minimum time interval (seconds) between PID calculations.
    output_limits : Tuple[Optional[float], Optional[float]], default=(None, None)
        Min and max allowable controller output.
    output_deadband_limits : Tuple[Optional[float], Optional[float]], default=(None, None)
        Range around zero output where output is forced to zero to reduce noise effects.
    error_deadband_limits : Tuple[Optional[float], Optional[float]], default=(None, None)
        Range around zero error where error is treated as zero to reduce sensitivity to noise.
    feedforward : float, default=0.0
        Constant feedforward term added to controller output.
    derivative_filter : float, default=0.0
        Low-pass smoothing factor (alpha) for derivative term (0.0–1.0).
    auto_mode : bool, default=True
        Enable or disable PID output calculation.
    anti_windup : bool, default=True
        Enable anti-windup to prevent integral runaway.
    max_output_rate : Optional[float], default=None
        Max allowed rate of output change per second (slew rate limiting).
    derivative_on_measurement : bool, default=False
        Compute derivative term from process variable instead of error.
    integral_on_measurement : bool, default=False
        Compute integral term based on measurement changes instead of error.

    Notes
    -----
    - Gain scheduling allows dynamic tuning of PID gains based on operating conditions.
    - Anti-windup helps prevent integral accumulation when actuators saturate.
    - Derivative filtering reduces noise amplification in the derivative term.
    """

    def __init__(
        self,
        Kp: float = 1.0,
        Ki: float = 0.0,
        Kd: float = 0.0,
        gain_scheduler: Optional[GainScheduler] = None,
        setpoint: float = 0.0,
        sample_time: float = 0.01,
        output_limits: Tuple[Optional[float], Optional[float]] = (None, None),
        output_deadband_limits: Tuple[Optional[float], Optional[float]] = (None, None),
        error_deadband_limits: Tuple[Optional[float], Optional[float]] = (None, None),
        feedforward: float = 0.0,
        derivative_filter: float = 0.0,
        auto_mode: bool = True,
        anti_windup: bool = True,
        max_output_rate: Optional[float] = None,
        derivative_on_measurement: bool = False,
        integral_on_measurement: bool = False,
    ):
        """
        Initialize PID controller with specified parameters.

        Sets all gains, limits, modes, and initial internal states.

        Parameters
        ----------
        (See class-level docstring for details)
        """
        self.derivative_on_measurement = derivative_on_measurement
        self.integral_on_measurement = integral_on_measurement
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.gain_scheduler = gain_scheduler

        self.setpoint = setpoint
        self.sample_time = sample_time
        self.output_limits = output_limits
        self.output_deadband_limits = output_deadband_limits
        self.error_deadband_limits = error_deadband_limits
        self.feedforward = feedforward
        self.derivative_filter = derivative_filter
        self.auto_mode = auto_mode
        self.anti_windup = anti_windup

        self._last_time = None
        self._last_error = 0.0
        self._integral = 0.0
        self._last_derivative = 0.0
        self._last_pv = None
        self._output = 0.0
        self._last_output = 0.0
        self.max_output_rate = max_output_rate

    def reset(self):
        """
        Reset the internal PID controller state.

        Clears integral accumulation, last error, last derivative,
        last process variable, and output history to initial states.

        """
        self._last_time = None
        self._last_error = 0.0
        self._integral = 0.0
        self._last_derivative = 0.0
        self._last_pv = None
        self._output = 0.0
        self._last_output = 0.0

    def set_auto_mode(self, enabled: bool, reset: bool = True):
        """
        Enable or disable automatic PID computation mode.

        When disabled, the PID output remains constant at the last computed value.

        Parameters
        ----------
        enabled : bool
            True to enable automatic PID computation, False to disable.
        reset : bool, optional
            If True, reset internal state when mode is changed.
        """
        self.auto_mode = enabled
        if reset:
            self.reset()

    def set_output_limits(self, min_output: Optional[float], max_output: Optional[float]):
        """
        Define the saturation limits for the controller output.

        Controller output will be clamped within these bounds.

        Parameters
        ----------
        min_output : float or None
            Minimum output limit; None means no limit.
        max_output : float or None
            Maximum output limit; None means no limit.
        """
        self.output_limits = (min_output, max_output)

    def _compute_proportional(self, error: float) -> float:
        """
        Calculate proportional term contribution.

        Parameters
        ----------
        error : float
            Current error between setpoint and process variable.

        Returns
        -------
        float
            Proportional term output.
        """
        return self.Kp * error

    def _compute_integral(self, error: float, process_variable: float, delta_time: float) -> float:
        """
        Calculate integral term contribution and update integral accumulator.

        Parameters
        ----------
        error : float
            Current error between setpoint and process variable.
        process_variable : float
            Current measured process variable.
        delta_time : float
            Time elapsed since last update (seconds).

        Returns
        -------
        float
            Integral term output.
        """
        if self.integral_on_measurement:
            # Integrate the negative of the measurement change (like derivative on measurement)
            if self._last_pv is None:
                self._last_pv = process_variable
                return 0.0
            delta_pv = process_variable - self._last_pv
            self._integral -= delta_pv * delta_time
            self._last_pv = process_variable
        else:
            self._integral += error * delta_time

        return self.Ki * self._integral

    def _compute_derivative(self, error: float, process_variable: float, delta_time: float) -> float:
        """
        Calculate derivative term contribution, optionally filtering and
        computing derivative on measurement or error.

        Parameters
        ----------
        error : float
            Current error between setpoint and process variable.
        process_variable : float
            Current measured process variable.
        delta_time : float
            Time elapsed since last update (seconds).

        Returns
        -------
        float
            Derivative term output.
        """
        if delta_time <= 0:
            return 0.0

        if self.derivative_on_measurement:
            if self._last_pv is None:
                self._last_pv = process_variable
                return 0.0
            derivative = -(process_variable - self._last_pv) / delta_time
            self._last_pv = process_variable
        else:
            derivative = (error - self._last_error) / delta_time

        if self.derivative_filter > 0.0:
            alpha = self.derivative_filter
            derivative = alpha * derivative + (1 - alpha) * self._last_derivative
            self._last_derivative = derivative

        return self.Kd * derivative

    def _calculate_error(self, process_variable: float) -> float:
        """
        Calculate current control error.

        Parameters
        ----------
        process_variable : float
            Current measured value of the process variable.

        Returns
        -------
        float
            Error (setpoint - process_variable).
        """
        return self.setpoint - process_variable

    def _apply_output_limits(self, output: float, error: float, delta_time: float) -> float:
        """
        Clamp the output to configured limits and apply anti-windup correction if enabled.

        If output saturates, integral term is adjusted to prevent integral windup.

        Parameters
        ----------
        output : float
            Raw PID output before clamping.
        error : float
            Current control error.
        delta_time : float
            Time elapsed since last update (seconds).

        Returns
        -------
        float
            Clamped output value.
        """
        min_output, max_output = self.output_limits

        if max_output is not None and output > max_output:
            output = max_output
            if self.anti_windup:
                self._integral -= error * delta_time

        elif min_output is not None and output < min_output:
            output = min_output
            if self.anti_windup:
                self._integral -= error * delta_time

        return output

    def _apply_slew_rate_limiter(self, output: float, delta_time: float) -> float:
        """
        Limit the rate of change of output to max_output_rate to prevent abrupt changes.

        Parameters
        ----------
        output : float
            Proposed controller output.
        delta_time : float
            Time elapsed since last update (seconds).

        Returns
        -------
        float
            Output value adjusted by slew rate limiter if applicable.
        """
        if self.max_output_rate is None:
            return output

        delta = output - self._last_output
        max_delta = self.max_output_rate * delta_time

        if abs(delta) > max_delta:
            output = self._last_output + max_delta * (1 if delta > 0 else -1)

        return output

    def _apply_output_deadband(self, output: float) -> float:
        """
        Apply deadband to the output signal, zeroing it if within the deadband limits.

        Parameters
        ----------
        output : float
            Current controller output.

        Returns
        -------
        float
            Zero if output within deadband range; otherwise unchanged output.
        """
        min_output_deadband, max_output_deadband = self.output_deadband_limits
        if min_output_deadband is None or max_output_deadband is None:
            return output

        if min_output_deadband <= output <= max_output_deadband:
            return 0.0

        return output

    def _apply_error_deadband(self, error: float) -> float:
        """
        Apply deadband to the error signal, zeroing it if within the deadband limits.

        Parameters
        ----------
        error : float
            Current control error.

        Returns
        -------
        float
            Zero if error within deadband range; otherwise unchanged error.
        """
        min_error_deadband, max_error_deadband = self.error_deadband_limits
        if min_error_deadband is None or max_error_deadband is None:
            return error

        if min_error_deadband <= error <= max_error_deadband:
            return 0.0

        return error

    def _run(self, process_variable: float, delta_time: Optional[float], feedforward: Optional[float]) -> float:
        """
        Perform a PID calculation cycle, computing the control output based on current process variable.

        Applies gain scheduling, deadbands, integral anti-windup, derivative filtering,
        output limits, slew rate limiting, and feedforward.

        Parameters
        ----------
        process_variable : float
            Current measured process variable.
        delta_time : float or None
            Time elapsed since last PID calculation. If None, it will be computed internally.
        feedforward : float or None
            Optional feedforward term to override the stored feedforward value.

        Returns
        -------
        float
            Updated controller output value.
        """
        if self.gain_scheduler is not None:
            self.Kp, self.Ki, self.Kd = self.gain_scheduler.get_gains(process_variable)

        ff = feedforward if feedforward is not None else self.feedforward

        if not self.auto_mode:
            return self._output

        now = time.time()

        error = self._calculate_error(process_variable)

        if self.error_deadband_limits != (None, None):
            error = self._apply_error_deadband(error)

        if delta_time is None:
            if self._last_time is None:
                self._last_time = now
                return self._output
            delta_time = now - self._last_time

        if delta_time < self.sample_time:
            return self._output

        self._last_time = now

        # Proportional term
        P = self._compute_proportional(error)

        # Integral term with anti-windup
        I = self._compute_integral(error, process_variable, delta_time)

        # Derivative term with optional filtering
        D = self._compute_derivative(error, process_variable, delta_time)

        output = P
        output = P + I + D + ff

        # Clamp output and apply anti-windup
        output = self._apply_output_limits(output, error, delta_time)

        # Apply output deadband if configured
        if self.output_deadband_limits != (None, None):
            output = self._apply_output_deadband(output)

        # Limit output slew rate
        output = self._apply_slew_rate_limiter(output, delta_time)

        self._last_error = error
        self._last_output = output
        self._output = output

        return output


    def run(self, process_variable: float, delta_time: Optional[float] = None, feedforward: Optional[float] = None) -> float:
        """
        Compute the PID output for the given process variable.

        Parameters
        ----------
        process_variable : float
            Current measured value of the process variable.
        delta_time : float or None, optional
            Time elapsed since last update; if None, it will be internally computed.
        feedforward : float or None, optional
            Optional feedforward term to override the internal feedforward value.

        Returns
        -------
        float
            Updated controller output value.
        """
        return self._run(process_variable, delta_time, feedforward)

    def __repr__(self):
        """
        Return a string representation showing current gains, setpoint, and last output.

        Useful for debugging and logging the PID state.
        """
        return (
            f"PID(Kp={self.Kp}, Ki={self.Ki}, Kd={self.Kd}, "
            f"Setpoint={self.setpoint}, Output={self._output:.3f})"
        )
