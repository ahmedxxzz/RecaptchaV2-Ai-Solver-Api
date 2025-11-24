"""
Quick test to verify the reCAPTCHA solver fix.
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from recaptchaSolverWithDriver import solve_recaptcha_with_driver

print("Starting test...")

# Create Firefox driver
firefox_options = FirefoxOptions()
# Set language preference
firefox_options.set_preference("intl.accept_languages", "en-US, en")

driver = webdriver.Firefox(options=firefox_options)

try:
    # Solve reCAPTCHA
    url = "https://google.com/recaptcha/api2/demo"
    print(f"Navigating to: {url}")
    
    driver = solve_recaptcha_with_driver(driver, url, verbose=True)
    
    print("\n✓ SUCCESS! reCAPTCHA solved. Driver is ready to use.")
    print("You can now continue using the driver for other tasks...")
    
    # Optional: Wait a bit so you can see the result
    input("\nPress Enter to close the browser...")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
    print("Browser closed.")
