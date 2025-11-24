# RecaptchaV2 AI Solver API

A powerful, AI-driven solution for solving Google's ReCAPTCHA V2 challenges using Selenium and YOLO object detection. This tool allows you to pass your own Selenium WebDriver instance, solves the captcha, and returns the driver to you for continued use.

## 🚀 Features

- **Bring Your Own Driver**: Works with your existing Selenium WebDriver (Firefox, Chrome, etc.).
- **AI-Powered**: Uses YOLO (You Only Look Once) object detection to accurately identify captcha targets.
- **Auto-Handling**: Automatically handles different captcha types (3x3, 4x4, dynamic, selection).
- **Smart Detection**: Detects if reCAPTCHA auto-solves (no challenge) to save time.
- **Easy Integration**: Simple function or class-based API to fit your workflow.

## 📋 Prerequisites

1.  **Python 3.8+**
2.  **Browser Drivers**:
    *   **Firefox**: [GeckoDriver](https://github.com/mozilla/geckodriver/releases) (recommended)
    *   **Chrome**: [ChromeDriver](https://chromedriver.chromium.org/downloads)
    *   Ensure the driver is in your system PATH.
3.  **YOLO Model**: You need a trained YOLO model file named `model.onnx` in your project directory.

## 🛠️ Installation

1.  Clone this repository.
2.  Install the required Python packages:

```bash
pip install -r requirements.txt
```

## ⚡ Usage

### ⚠️ Critical Requirement: Language Setting

**You MUST set the browser language to English (`en-US`).**
The solver relies on reading the English text of the challenge (e.g., "Select all images with **cars**"). If the browser uses another language, the solver will fail.

### Basic Example (Function)

The easiest way to use the solver:

```python
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from recaptchaSolverWithDriver import solve_recaptcha_with_driver

# 1. Configure Firefox for English
options = FirefoxOptions()
options.set_preference("intl.accept_languages", "en-US, en")

# 2. Create Driver
driver = webdriver.Firefox(options=options)

# 3. Solve reCAPTCHA
# Pass the driver and the URL containing the reCAPTCHA
driver = solve_recaptcha_with_driver(
    driver, 
    "https://google.com/recaptcha/api2/demo", 
    verbose=True
)

# 4. Continue using the driver...
print("Captcha solved!")
driver.quit()
```

### Advanced Example (Class)

For more control or reusing the solver instance:

```python
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from recaptchaSolverWithDriver import RecaptchaSolverWithDriver

# Setup Driver
options = FirefoxOptions()
options.set_preference("intl.accept_languages", "en-US, en")
driver = webdriver.Firefox(options=options)

# Initialize Solver (load model once)
solver = RecaptchaSolverWithDriver(model_path="./model.onnx", verbose=True)

# Solve
driver = solver.solve(driver, "https://google.com/recaptcha/api2/demo")

driver.quit()
```

### Chrome Usage

For Google Chrome, set the language argument:

```python
from selenium.webdriver.chrome.options import Options as ChromeOptions

options = ChromeOptions()
options.add_argument('--lang=en-US')  # Set language to English
driver = webdriver.Chrome(options=options)

# ... use solver as normal
```

## 📂 Project Structure

*   `recaptchaSolverWithDriver.py`: Main module containing the solver logic.
*   `example_usage.py`: Comprehensive examples for different scenarios.
*   `test_fix.py`: A simple test script to verify functionality.
*   `requirements.txt`: List of dependencies.
*   `model.onnx`: (Required) Your trained YOLO model file.

## ❓ Troubleshooting

**Issue: `TimeoutException` or Solver hangs**
*   **Cause**: The browser might be displaying the reCAPTCHA in a non-English language.
*   **Fix**: Ensure you are setting `intl.accept_languages` (Firefox) or `--lang=en-US` (Chrome) as shown in the examples.

**Issue: "skipping" printed repeatedly**
*   **Cause**: The solver cannot identify the target object name from the text.
*   **Fix**: Check the browser language. If it is English, the object might not be in the supported list (car, bus, bicycle, traffic light, etc.).

## 📄 License

[Your License Here]
