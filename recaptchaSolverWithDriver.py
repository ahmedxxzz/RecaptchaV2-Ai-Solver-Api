# Standard imports
import re
import shutil
from time import sleep

# Third-party imports
import cv2
import numpy as np
import requests
from PIL import Image
from ultralytics import YOLO
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class RecaptchaSolverWithDriver:
    """
    A reusable ReCAPTCHA solver that works with an existing WebDriver instance.
    
    Usage:
        solver = RecaptchaSolverWithDriver(model_path="./model.onnx", verbose=True)
        driver = solver.solve(driver, url)
    """
    
    def __init__(self, model_path: str = "./model.onnx", verbose: bool = False):
        """
        Initialize the ReCAPTCHA solver.
        
        :param model_path: Path to the YOLO model file.
        :param verbose: Enable verbose logging.
        """
        self.model_path = model_path
        self.verbose = verbose
        self.model = None
    
    def _load_model(self):
        """Load the YOLO model if not already loaded."""
        if self.model is None:
            self.model = YOLO(self.model_path, task="detect")
    
    @staticmethod
    def _find_between(s, first, last):
        """
        Find a substring between two substrings.
        
        :param s: String to search.
        :param first: First substring.
        :param last: Last substring.
        :return: Extracted substring or empty string.
        """
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""
    
    @staticmethod
    def _random_delay(mu=0.3, sigma=0.1):
        """
        Random delay to simulate human behavior.
        
        :param mu: Mean of normal distribution.
        :param sigma: Standard deviation of normal distribution.
        """
        delay = np.random.normal(mu, sigma)
        delay = max(0.1, delay)
        sleep(delay)
    
    def _go_to_recaptcha_iframe1(self, driver):
        """Go to the first recaptcha iframe (CheckBox)."""
        driver.switch_to.default_content()
        recaptcha_iframe1 = WebDriverWait(driver=driver, timeout=20).until(
            EC.presence_of_element_located((By.XPATH, '//iframe[@title="reCAPTCHA"]')))
        driver.switch_to.frame(recaptcha_iframe1)
    
    def _go_to_recaptcha_iframe2(self, driver):
        """Go to the second recaptcha iframe (Images)."""
        driver.switch_to.default_content()
        recaptcha_iframe2 = WebDriverWait(driver=driver, timeout=20).until(
            EC.presence_of_element_located((By.XPATH, '//iframe[contains(@title, "challenge")]')))
        driver.switch_to.frame(recaptcha_iframe2)
    
    def _get_target_num(self, driver):
        """Get the target number from the recaptcha title."""
        target_mappings = {
            "bicycle": 1,
            "bus": 5,
            "boat": 8,
            "car": 2,
            "hydrant": 10,
            "motorcycle": 3,
            "traffic": 9
        }
        
        target = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, '//div[@id="rc-imageselect"]//strong')))
        
        for term, value in target_mappings.items():
            if re.search(term, target.text):
                return value
        
        return 1000
    
    def _dynamic_and_selection_solver(self, target_num):
        """
        Get the answers from the recaptcha images.
        
        :param target_num: Target number.
        :return: List of answer positions.
        """
        # Load image and predict
        image = Image.open("0.png")
        image = np.asarray(image)
        result = self.model.predict(image, task="detect", verbose=self.verbose)
        
        # Get the index of the target number
        target_index = []
        count = 0
        for num in result[0].boxes.cls:
            if num == target_num:
                target_index.append(count)
            count += 1
        
        # Get the answers from the index
        answers = []
        boxes = result[0].boxes.data
        for i in target_index:
            target_box = boxes[i]
            p1, p2 = (int(target_box[0]), int(target_box[1])), (int(target_box[2]), int(target_box[3]))
            x1, y1 = p1
            x2, y2 = p2
            
            xc = (x1 + x2) / 2
            yc = (y1 + y2) / 2
            
            row = yc // 100
            col = xc // 100
            answer = int(row * 3 + col + 1)
            answers.append(answer)
        
        return list(set(answers))
    
    @staticmethod
    def _get_all_captcha_img_urls(driver):
        """Get all the image urls from the recaptcha."""
        images = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
            (By.XPATH, '//div[@id="rc-imageselect-target"]//img')))
        
        img_urls = []
        for img in images:
            img_urls.append(img.get_attribute("src"))
        
        return img_urls
    
    @staticmethod
    def _download_img(name, url):
        """
        Download the image.
        
        :param name: Name of the image.
        :param url: URL of the image.
        """
        response = requests.get(url, stream=True)
        with open(f'{name}.png', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
    
    def _get_all_new_dynamic_captcha_img_urls(self, answers, before_img_urls, driver):
        """
        Get all the new image urls from the recaptcha.
        
        :param answers: Answers from the recaptcha.
        :param before_img_urls: Image urls before.
        :return: Tuple of (is_new, img_urls).
        """
        images = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
            (By.XPATH, '//div[@id="rc-imageselect-target"]//img')))
        img_urls = []
        
        # Get all the image urls
        for img in images:
            try:
                img_urls.append(img.get_attribute("src"))
            except:
                is_new = False
                return is_new, img_urls
        
        # Check if the image urls are the same as before
        index_common = []
        for answer in answers:
            if img_urls[answer - 1] == before_img_urls[answer - 1]:
                index_common.append(answer)
        
        # Return if the image urls are the same as before
        if len(index_common) >= 1:
            is_new = False
            return is_new, img_urls
        else:
            is_new = True
            return is_new, img_urls
    
    @staticmethod
    def _paste_new_img_on_main_img(main, new, loc):
        """
        Paste the new image on the main image.
        
        :param main: Main image.
        :param new: New image.
        :param loc: Location of the new image.
        """
        paste = np.copy(main)
        
        row = (loc - 1) // 3
        col = (loc - 1) % 3
        
        start_row, end_row = row * 100, (row + 1) * 100
        start_col, end_col = col * 100, (col + 1) * 100
        
        paste[start_row:end_row, start_col:end_col] = new
        
        paste = cv2.cvtColor(paste, cv2.COLOR_RGB2BGR)
        cv2.imwrite('0.png', paste)
    
    @staticmethod
    def _get_occupied_cells(vertices):
        """
        Get the occupied cells from the vertices.
        
        :param vertices: Vertices of the image.
        :return: List of occupied cells.
        """
        occupied_cells = set()
        rows, cols = zip(*[((v - 1) // 4, (v - 1) % 4) for v in vertices])
        
        for i in range(min(rows), max(rows) + 1):
            for j in range(min(cols), max(cols) + 1):
                occupied_cells.add(4 * i + j + 1)
        
        return sorted(list(occupied_cells))
    
    def _square_solver(self, target_num):
        """
        Get the answers from the recaptcha images for square challenges.
        
        :param target_num: Target number.
        :return: List of answer positions.
        """
        # Load image and predict
        image = Image.open("0.png")
        image = np.asarray(image)
        result = self.model.predict(image, task="detect", verbose=self.verbose)
        boxes = result[0].boxes.data
        
        target_index = []
        count = 0
        for num in result[0].boxes.cls:
            if num == target_num:
                target_index.append(count)
            count += 1
        
        answers = []
        for i in target_index:
            target_box = boxes[i]
            p1, p2 = (int(target_box[0]), int(target_box[1])), (int(target_box[2]), int(target_box[3]))
            x1, y1 = p1
            x4, y4 = p2
            x2 = x4
            y2 = y1
            x3 = x1
            y3 = y4
            xys = [x1, y1, x2, y2, x3, y3, x4, y4]
            
            four_cells = []
            for j in range(4):
                x = xys[j * 2]
                y = xys[(j * 2) + 1]
                
                if x < 112.5 and y < 112.5:
                    four_cells.append(1)
                if 112.5 < x < 225 and y < 112.5:
                    four_cells.append(2)
                if 225 < x < 337.5 and y < 112.5:
                    four_cells.append(3)
                if 337.5 < x <= 450 and y < 112.5:
                    four_cells.append(4)
                
                if x < 112.5 and 112.5 < y < 225:
                    four_cells.append(5)
                if 112.5 < x < 225 and 112.5 < y < 225:
                    four_cells.append(6)
                if 225 < x < 337.5 and 112.5 < y < 225:
                    four_cells.append(7)
                if 337.5 < x <= 450 and 112.5 < y < 225:
                    four_cells.append(8)
                
                if x < 112.5 and 225 < y < 337.5:
                    four_cells.append(9)
                if 112.5 < x < 225 and 225 < y < 337.5:
                    four_cells.append(10)
                if 225 < x < 337.5 and 225 < y < 337.5:
                    four_cells.append(11)
                if 337.5 < x <= 450 and 225 < y < 337.5:
                    four_cells.append(12)
                
                if x < 112.5 and 337.5 < y <= 450:
                    four_cells.append(13)
                if 112.5 < x < 225 and 337.5 < y <= 450:
                    four_cells.append(14)
                if 225 < x < 337.5 and 337.5 < y <= 450:
                    four_cells.append(15)
                if 337.5 < x <= 450 and 337.5 < y <= 450:
                    four_cells.append(16)
            
            answer = self._get_occupied_cells(four_cells)
            for ans in answer:
                answers.append(ans)
        
        answers = sorted(list(answers))
        return list(set(answers))
    
    def _solve_recaptcha(self, driver):
        """
        Solve the recaptcha challenge.
        
        :param driver: Selenium WebDriver instance.
        """
        self._go_to_recaptcha_iframe1(driver)
        
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//div[@class="recaptcha-checkbox-border"]'))).click()
        
        # Check if the reCAPTCHA was solved immediately (no challenge shown)
        try:
            self._go_to_recaptcha_iframe1(driver)
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//span[contains(@aria-checked, "true")]')))
            if self.verbose:
                print("reCAPTCHA solved automatically (no challenge required)")
            driver.switch_to.default_content()
            return
        except:
            # Challenge is required, continue to solve it
            pass
        
        self._go_to_recaptcha_iframe2(driver)
        
        self._load_model()
        
        while True:
            try:
                while True:
                    reload = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, 'recaptcha-reload-button')))
                    title_wrapper = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'rc-imageselect')))
                    
                    target_num = self._get_target_num(driver)
                    
                    if target_num == 1000:
                        self._random_delay()
                        if self.verbose:
                            print("skipping")
                        reload.click()
                    elif "squares" in title_wrapper.text:
                        if self.verbose:
                            print("Square captcha found....")
                        img_urls = self._get_all_captcha_img_urls(driver)
                        self._download_img(0, img_urls[0])
                        answers = self._square_solver(target_num)
                        if len(answers) >= 1 and len(answers) < 16:
                            captcha = "squares"
                            break
                        else:
                            reload.click()
                    elif "none" in title_wrapper.text:
                        if self.verbose:
                            print("found a 3x3 dynamic captcha")
                        img_urls = self._get_all_captcha_img_urls(driver)
                        self._download_img(0, img_urls[0])
                        answers = self._dynamic_and_selection_solver(target_num)
                        if len(answers) > 2:
                            captcha = "dynamic"
                            break
                        else:
                            reload.click()
                    else:
                        if self.verbose:
                            print("found a 3x3 one time selection captcha")
                        img_urls = self._get_all_captcha_img_urls(driver)
                        self._download_img(0, img_urls[0])
                        answers = self._dynamic_and_selection_solver(target_num)
                        if len(answers) > 2:
                            captcha = "selection"
                            break
                        else:
                            reload.click()
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                        (By.XPATH, '(//div[@id="rc-imageselect-target"]//td)[1]')))
                
                if captcha == "dynamic":
                    for answer in answers:
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                            (By.XPATH, f'(//div[@id="rc-imageselect-target"]//td)[{answer}]'))).click()
                        self._random_delay(mu=0.5, sigma=0.2)
                    while True:
                        before_img_urls = img_urls
                        while True:
                            is_new, img_urls = self._get_all_new_dynamic_captcha_img_urls(
                                answers, before_img_urls, driver)
                            if is_new:
                                break
                        
                        new_img_index_urls = []
                        for answer in answers:
                            new_img_index_urls.append(answer - 1)
                        
                        for index in new_img_index_urls:
                            self._download_img(index + 1, img_urls[index])
                        while True:
                            try:
                                for answer in answers:
                                    main_img = Image.open("0.png")
                                    new_img = Image.open(f"{answer}.png")
                                    location = answer
                                    self._paste_new_img_on_main_img(main_img, new_img, location)
                                break
                            except:
                                while True:
                                    is_new, img_urls = self._get_all_new_dynamic_captcha_img_urls(
                                        answers, before_img_urls, driver)
                                    if is_new:
                                        break
                                new_img_index_urls = []
                                for answer in answers:
                                    new_img_index_urls.append(answer - 1)
                                
                                for index in new_img_index_urls:
                                    self._download_img(index + 1, img_urls[index])
                        
                        answers = self._dynamic_and_selection_solver(target_num)
                        
                        if len(answers) >= 1:
                            for answer in answers:
                                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                                    (By.XPATH, f'(//div[@id="rc-imageselect-target"]//td)[{answer}]'))).click()
                                self._random_delay(mu=0.5, sigma=0.1)
                        else:
                            break
                elif captcha == "selection" or captcha == "squares":
                    for answer in answers:
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                            (By.XPATH, f'(//div[@id="rc-imageselect-target"]//td)[{answer}]'))).click()
                        self._random_delay()
                
                verify = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                    (By.ID, "recaptcha-verify-button")))
                self._random_delay(mu=2, sigma=0.2)
                verify.click()
                
                try:
                    self._go_to_recaptcha_iframe1(driver)
                    WebDriverWait(driver, 4).until(
                        EC.presence_of_element_located((By.XPATH, '//span[contains(@aria-checked, "true")]')))
                    if self.verbose:
                        print("solved")
                    driver.switch_to.default_content()
                    break
                except:
                    self._go_to_recaptcha_iframe2(driver)
            except Exception as e:
                if self.verbose:
                    print(f"Error: {e}")
    
    def solve(self, driver, url: str):
        """
        Solve reCAPTCHA on the specified URL using the provided driver.
        
        :param driver: Selenium WebDriver instance (e.g., Firefox, Chrome).
        :param url: URL of the page with reCAPTCHA.
        :return: The same driver instance with reCAPTCHA solved.
        """
        driver.get(url)
        self._solve_recaptcha(driver)
        return driver


def solve_recaptcha_with_driver(driver, url: str, model_path: str = "./model.onnx", verbose: bool = False):
    """
    Convenience function to solve reCAPTCHA with an existing driver.
    
    :param driver: Selenium WebDriver instance (e.g., Firefox, Chrome).
    :param url: URL of the page with reCAPTCHA.
    :param model_path: Path to the YOLO model file.
    :param verbose: Enable verbose logging.
    :return: The driver instance with reCAPTCHA solved.
    
    Example:
        from selenium import webdriver
        from recaptchaSolverWithDriver import solve_recaptcha_with_driver
        
        driver = webdriver.Firefox()
        driver = solve_recaptcha_with_driver(driver, "https://google.com/recaptcha/api2/demo", verbose=True)
        # Continue using the driver...
        driver.quit()
    """
    solver = RecaptchaSolverWithDriver(model_path=model_path, verbose=verbose)
    return solver.solve(driver, url)
