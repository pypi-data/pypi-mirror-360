import time
import shutil
import traceback
import sys
import os

class Progress:
    """
    A dynamic terminal progress bar with optional color gradients, velocity tracking,
    and estimated time remaining (ETA).

    Features:
    ----------
    - Customizable display template.
    - Smoothed speed calculation (average of last 10 updates).
    - Automatically adapts to terminal width.
    - Supports multicolor gradient or single interpolated color.
    - Shows percentage, speed, and ETA in real-time.

    Parameters:
    ----------
    min_value : float
        The starting value of the progress range.
    max_value : float
        The ending value of the progress range.
    unit : str, optional
        The unit label to display next to the speed value (e.g., "MB", "items").
    colors : list of tuple(int, int, int), optional
        A list of RGB tuples used to create a gradient for the filled bar.
        Example: [(255, 0, 0), (255, 255, 0), (0, 255, 0)].
    single_color : bool, default=False
        If True, applies a single interpolated color across the whole bar.
        If False, creates a smooth gradient effect across all segments.
    template : str, optional
        A custom template string. You can use the following placeholders:
            - {progress_bar}
            - {percentage}
            - {velocity}
            - {unit}
            - {eta}
        Example:
            "{progress_bar} {percentage}% | Speed: {velocity} {unit}/s | ETA: {eta}"

    Raises:
    ------
    SystemExit
        If any required parameter is missing or template contains {unit} without defining `unit`.

    Methods:
    -------
    update(current_value: float):
        Updates the progress bar in the terminal according to the current progress.
    """

    def __init__(self, min_value=None, max_value=None, unit=None, colors=None,
                 single_color=False, template=None):

        if min_value is None or max_value is None:
            self.__fatal_error("You must define min_value and max_value.")

        if template is None:
            if unit is None:
                self.__fatal_error("You must define 'unit' if no custom template is provided.")
            self.template = "{progress_bar} {percentage}% {velocity} {unit}/s  {eta}"
        else:
            self.template = template
            if '{unit}' in template and unit is None:
                self.__fatal_error("Your template includes '{unit}' but no 'unit' was provided.")

        self.min = min_value
        self.max = max_value
        self.unit = unit
        self.colors = colors
        self.single_color = single_color

        self.__start_time = time.perf_counter()
        self.__last_value = min_value
        self.__last_time = self.__start_time
        self.__history = []

    def update(self, current_value: float):
        """
        Update the progress bar display in the terminal.

        Parameters:
        ----------
        current_value : float
            The current progress value (should be between `min_value` and `max_value`).

        Behavior:
        ---------
        - Computes percentage and smooth speed.
        - Estimates time remaining.
        - Renders a dynamic progress bar with optional colors and template.
        - Overwrites the terminal line with updated info.
        """
        now = time.perf_counter()
        delta_value = current_value - self.__last_value
        delta_time = now - self.__last_time
        speed = delta_value / delta_time if delta_time > 0 else 0.0

        self.__history.append((now, current_value))
        if len(self.__history) > 10:
            self.__history.pop(0)
        times, values = zip(*self.__history)
        smooth_delta = values[-1] - values[0]
        smooth_time = times[-1] - times[0]
        smooth_speed = smooth_delta / smooth_time if smooth_time > 0 else 0.0

        pct = (current_value - self.min) / (self.max - self.min)
        pct = max(0.0, min(1.0, pct))
        percent = int(pct * 100)

        remaining = self.max - current_value
        eta = int(remaining / smooth_speed) if smooth_speed > 0 else 0
        m, s = divmod(eta, 60)
        eta_str = f"{m}m{s:02}s"

        term_width = shutil.get_terminal_size().columns
        bar_width = max(10, min(40, term_width - 40))
        filled = int(pct * bar_width)

        # Gera a barra com cor única ou degradê
        bar = "|"
        for i in range(bar_width):
            if i < filled:
                if self.colors:
                    if self.single_color:
                        color = self.__interpolate_color(current_value)
                    else:
                        virtual_val = self.min + (self.max - self.min) * (i / bar_width)
                        color = self.__interpolate_color(virtual_val)
                    bar += f"{color}█"
                else:
                    bar += "█"
            else:
                bar += f"{self.__reset()} "
        bar += f"{self.__reset()}|"

        # Monta o texto final
        output = self.template.format(
            progress_bar=bar,
            percentage=percent,
            velocity=f"{smooth_speed:5.1f}",
            eta=eta_str,
            unit=self.unit
        )

        print(f"\r{output}", end="", flush=True)

        self.__last_value = current_value
        self.__last_time = now

    def __interpolate_color(self, value):
        if not self.colors:
            return ""
        pos = (value - self.min) / (self.max - self.min)
        pos = max(0.0, min(1.0, pos))
        segments = len(self.colors) - 1
        idx = min(int(pos * segments), segments - 1)
        frac = (pos * segments) - idx
        r1, g1, b1 = self.colors[idx]
        r2, g2, b2 = self.colors[idx + 1]
        r = int(r1 + (r2 - r1) * frac)
        g = int(g1 + (g2 - g1) * frac)
        b = int(b1 + (b2 - b1) * frac)
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def __reset():
        return "\033[0m"

    def __fatal_error(self, message: str):
        stack = traceback.extract_stack()
        this_file = os.path.abspath(__file__) if '__file__' in globals() else ''
        for frame in reversed(stack):
            if os.path.abspath(frame.filename) != this_file:
                caller = frame
                break
        else:
            caller = stack[-3] if len(stack) >= 3 else stack[-1]

        code_line = caller.line or ''
        col = code_line.find('Progress')
        arrow = ' ' * (col if col >= 0 else 0) + '↑'

        print(f"\n\033[31mFile \"{caller.filename}\", line {caller.lineno}:\033[0m")
        print(f"  \033[33m{code_line.strip()}\033[0m")
        print(f"  {arrow}")
        print(f"\033[31m❌ {message}\033[0m")
        sys.exit(1)
