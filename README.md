# RecaptchaV2 AI Solver API

A powerful, AI-driven solution for solving Google's ReCAPTCHA V2 challenges using Selenium and YOLO object detection. This tool offers two main modes: a standalone token extractor and a driver-integrated solver.

## 🚀 Features

- **Dual Modes**:
  - **Standalone**: Extract reCAPTCHA tokens and cookies for external use.
  - **Integrated**: Solve challenges directly within your existing Selenium WebDriver session.
- **AI-Powered**: Uses YOLO (You Only Look Once) object detection to accurately identify captcha targets.
- **Auto-Handling**: Automatically handles various captcha types (3x3, 4x4, dynamic, selection).
- **Smart Detection**: Detects if reCAPTCHA auto-solves (no challenge) to save time.
- **Support for Chrome & Firefox**: Works with both major browsers.

## 📋 Prerequisites

1.  **Python 3.8+**
2.  **Browser Drivers**:
    - **Firefox**: [GeckoDriver](https://github.com/mozilla/geckodriver/releases) (Recommended)
    - **Chrome**: [ChromeDriver](https://chromedriver.chromium.org/downloads)
3.  **YOLO Model**: A trained YOLO model file named `model.onnx` must be in the project directory.

## 🛠️ Installation

1.  Clone this repository.
2.  Install the required Python packages:

```bash
pip install -r requirements.txt
```

> [!NOTE]
> This project uses `selenium-wire` for token extraction and `ultralytics` for AI detection.

## ⚡ Usage

### ⚠️ Critical Requirement: Language Setting

**You MUST set the browser language to English (`en-US`).**
The solver relies on reading the English text of the challenge. If the browser uses another language, the solver will fail to identify targets.

### 1. Standalone Solver (Token Extraction)

Use `recaptchaSolver.py` when you need to get the `recaptcha_token` and `cookies` to use in a separate request (e.g., via `requests`).

```python
from recaptchaSolver import solver

# Extract token and session data
result = solver(
    url="https://google.com/recaptcha/api2/demo",
    proxy=None,       # Optional: "user:pass@host:port"
    verbose=True,     # Enable logging
    headless=True     # Run without opening a browser window
)

print(f"Token: {result['recaptcha_token']}")
print(f"Time Taken: {result['time_taken']}s")
```

### 2. Driver-Integrated Solver (In-Place)

Use `recaptchaSolverWithDriver.py` when you are already automating a browser session and encounter a captcha.

```python
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from recaptchaSolverWithDriver import solve_recaptcha_with_driver

# 1. Configure Browser for English
options = FirefoxOptions()
options.set_preference("intl.accept_languages", "en-US, en")

# 2. Initialize Driver
driver = webdriver.Firefox(options=options)

# 3. Solve reCAPTCHA in the current session
# This will navigate to the URL and solve the captcha in-place
driver = solve_recaptcha_with_driver(
    driver,
    "https://google.com/recaptcha/api2/demo",
    verbose=True
)

# 4. Continue using the driver
# The captcha is now solved in this driver instance
print("Captcha solved!")
driver.quit()
```

### Chrome Configuration

For Google Chrome, ensure the language is set correctly:

```python
from selenium.webdriver.chrome.options import Options as ChromeOptions

options = ChromeOptions()
options.add_argument('--lang=en-US')
driver = webdriver.Chrome(options=options)
```

## 📂 Project Structure

- `recaptchaSolver.py`: Standalone solver logic for token extraction.
- `recaptchaSolverWithDriver.py`: Class and function for solving captchas using an existing driver.
- `main.py`: Simple entry point demonstrating standalone usage.
- `example_usage.py`: Comprehensive examples for different integration scenarios.
- `test_fix.py`: Script to verify the integrated solver functionality.
- `model.onnx`: (Required) Your trained YOLO detection model.
- `requirements.txt`: Dependencies including `ultralytics`, `selenium-wire`, and `opencv-python`.

## ❓ Troubleshooting

**Issue: `TimeoutException` or Solver hangs**

- **Fix**: Ensure `intl.accept_languages` (Firefox) or `--lang=en-US` (Chrome) is set. The solver MUST see English text.

**Issue: "skipping" printed repeatedly**

- **Cause**: The target object name is not recognized or not in the supported mapping.
- **Supported Targets**: Bicycle, Bus, Boat, Car, Hydrant, Motorcycle, Traffic Light.

## 📄 License

[Your License Here]
