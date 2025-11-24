"""
Example usage of recaptchaSolverWithDriver module.

This demonstrates how to use the ReCAPTCHA solver with your own driver instance.
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from recaptchaSolverWithDriver import RecaptchaSolverWithDriver, solve_recaptcha_with_driver


def example1_using_class():
    """Example 1: Using the RecaptchaSolverWithDriver class."""
    print("Example 1: Using the class-based approach")
    
    # Create your own Firefox driver
    firefox_options = FirefoxOptions()
    firefox_options.set_preference("intl.accept_languages", "en-US, en")  # Required for English reCAPTCHA
    # firefox_options.add_argument('--headless')  # Uncomment for headless mode
    driver = webdriver.Firefox(options=firefox_options)
    
    # Create solver instance
    solver = RecaptchaSolverWithDriver(model_path="./model.onnx", verbose=True)
    
    # Solve reCAPTCHA and get the driver back
    url = "https://google.com/recaptcha/api2/demo"
    driver = solver.solve(driver, url)
    
    print("ReCAPTCHA solved! Driver is ready to use.")
    
    # Continue using the driver for other tasks...
    # For example, you could interact with the page after solving the captcha
    
    # Don't forget to quit the driver when done
    driver.quit()


def example2_using_function():
    """Example 2: Using the convenience function."""
    print("\nExample 2: Using the convenience function")
    
    # Create your own Firefox driver
    firefox_options = FirefoxOptions()
    firefox_options.set_preference("intl.accept_languages", "en-US, en")  # Required for English reCAPTCHA
    # firefox_options.add_argument('--headless')  # Uncomment for headless mode
    driver = webdriver.Firefox(options=firefox_options)
    
    # Solve reCAPTCHA using the convenience function
    url = "https://google.com/recaptcha/api2/demo"
    driver = solve_recaptcha_with_driver(driver, url, verbose=True)
    
    print("ReCAPTCHA solved! Driver is ready to use.")
    
    # Continue using the driver...
    
    # Don't forget to quit the driver when done
    driver.quit()


def example3_with_chrome():
    """Example 3: Using with Chrome driver."""
    print("\nExample 3: Using with Chrome driver")
    
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    
    # Create your own Chrome driver
    chrome_options = ChromeOptions()
    chrome_options.add_argument('--lang=en-US')  # Required for English reCAPTCHA
    # chrome_options.add_argument('--headless')  # Uncomment for headless mode
    driver = webdriver.Chrome(options=chrome_options)
    
    # Solve reCAPTCHA
    url = "https://google.com/recaptcha/api2/demo"
    driver = solve_recaptcha_with_driver(driver, url, verbose=True)
    
    print("ReCAPTCHA solved! Driver is ready to use.")
    
    # Continue using the driver...
    
    driver.quit()


def example4_reusing_solver():
    """Example 4: Reusing the same solver instance for multiple URLs."""
    print("\nExample 4: Reusing solver instance")
    
    # Create solver once
    solver = RecaptchaSolverWithDriver(model_path="./model.onnx", verbose=True)
    
    # Create driver
    firefox_options = FirefoxOptions()
    firefox_options.set_preference("intl.accept_languages", "en-US, en")  # Required for English reCAPTCHA
    driver = webdriver.Firefox(options=firefox_options)
    
    # Solve multiple reCAPTCHAs with the same solver instance
    urls = [
        "https://google.com/recaptcha/api2/demo",
        # Add more URLs as needed
    ]
    
    for url in urls:
        print(f"\nSolving reCAPTCHA for: {url}")
        driver = solver.solve(driver, url)
        print("Solved!")
        
        # Do something with the page...
    
    driver.quit()


if __name__ == "__main__":
    # Run example 2 (using the function) - the simplest approach
    example2_using_function()
    
    # Uncomment to try other examples:
    # example1_using_class()
    # example3_with_chrome()
    # example4_reusing_solver()
