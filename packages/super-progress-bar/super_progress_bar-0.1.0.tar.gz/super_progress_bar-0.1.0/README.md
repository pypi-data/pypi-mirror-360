# Progress

A modern, customizable, and colorful terminal progress bar for Python.

![Progress Bar Demo](https://user-images.githubusercontent.com/your-demo.gif) <!-- Substitua por um GIF se quiser -->

## Features

- 🔄 Real-time updates with smooth speed estimation
- 🎨 Gradient or single-color progress bar
- ⌛ ETA (Estimated Time Remaining)
- 📏 Adapts to terminal width
- 🧩 Customizable display template
- ✅ Easy to use and dependency-free

---

## Installation

```bash
pip install progress-bar-cli  # (Nome provisório, ajuste conforme seu setup.py)
```

---

## Usage

```python
import time
from progress import Progress

progress = Progress(
    min_value=0,
    max_value=100,
    unit="items",
    colors=[(255, 0, 0), (255, 255, 0), (0, 255, 0)],
    single_color=False
)

for i in range(101):
    progress.update(i)
    time.sleep(0.05)

print("\nDone!")
```

---

## Template Formatting

You can fully customize the progress bar layout:

```python
template="{progress_bar} {percentage}% • {velocity} {unit}/s • {eta}"
```

Available placeholders:
- `{progress_bar}`: the visual bar
- `{percentage}`: progress percent (int)
- `{velocity}`: items per second (float)
- `{unit}`: unit you provided (e.g., `files`)
- `{eta}`: estimated time remaining (e.g., `0m12s`)

---

## Parameters

| Parameter     | Description                                                             |
|---------------|-------------------------------------------------------------------------|
| `min_value`   | The start of the progress range (e.g., 0)                                |
| `max_value`   | The end of the progress range (e.g., 100)                                |
| `unit`        | Unit label to display next to speed (`items`, `MB`, `files`, etc.)       |
| `colors`      | List of RGB tuples for gradient coloring                                 |
| `single_color`| If True, uses one interpolated color instead of gradient                 |
| `template`    | Custom string template for output display                                |

---

## Example with Single Color Mode

```python
Progress(
    min_value=0,
    max_value=50,
    unit="steps",
    colors=[(0, 128, 255), (0, 255, 255)],
    single_color=True
)
```

---

## License

This project is licensed under the MIT License.
