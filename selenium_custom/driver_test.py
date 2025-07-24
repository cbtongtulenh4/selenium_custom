import time
import random
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional, Callable

class SeleP:
    def __init__(self, driver: WebDriver, default_timeout: int = 10, verbose: bool = False):
        self.driver = driver
        self.default_timeout = default_timeout
        self.verbose = verbose

    def log(self, msg):
        if self.verbose:
            print(f"[SeleP] {msg}")

    def wait_for_page_load(self, timeout: Optional[int] = None):
        timeout = timeout or self.default_timeout
        self.log("Waiting for page load...")
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            self.log("Page loaded.")
        except Exception as e:
            self.log(f"Page load wait failed: {e}")

    def wait_for_element(self, locator, condition=EC.presence_of_element_located, timeout=None, skip_error=True):
        timeout = timeout or self.default_timeout
        try:
            WebDriverWait(self.driver, timeout).until(condition(locator))
            return True
        except Exception as e:
            self.log(f"Wait for element {locator} failed: {e}")
            if not skip_error:
                raise
        return False

    def click(self, xpath, timeout=None, skip_error=True):
        timeout = timeout or self.default_timeout
        try:
            ele = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            ele.click()
            self.log(f"Clicked on {xpath}")
            return True
        except Exception as e:
            self.log(f"Normal click failed: {e}")
        # JavaScript click fallback
        try:
            ele = self.driver.find_element(By.XPATH, xpath)
            self.driver.execute_script("arguments[0].click();", ele)
            time.sleep(0.5)
            self.log(f"Clicked via JS on {xpath}")
            return True
        except Exception as e:
            self.log(f"JS click failed: {e}")
        # ActionChains click fallback
        try:
            ele = self.driver.find_element(By.XPATH, xpath)
            ActionChains(self.driver).move_to_element(ele).click().perform()
            self.log(f"Clicked via ActionChains on {xpath}")
            return True
        except Exception as e:
            self.log(f"ActionChains click failed: {e}")
        if not skip_error:
            raise
        return False

    def is_element_in_viewport(self, element):
        return self.driver.execute_script("""
            var element = arguments[0];
            var rect = element.getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        """, element)
    
    def clear_input(self, xpath):
        
        pass

    def scroll_into_view(self, xpath, center=True, timeout=None):
        timeout = timeout or self.default_timeout
        try:
            ele = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});" if center else "arguments[0].scrollIntoView(false);", ele)
            time.sleep(0.5)
            self.log(f"Scrolled into view: {xpath}")
            return True
        except Exception as e:
            self.log(f"Scroll into view failed: {e}")
            return False

    def send_keys(self, xpath, text, speed=True, timeout=None, clear=True):
        timeout = timeout or self.default_timeout
        try:
            ele = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, xpath)))
            self.click(xpath)
            if clear:
                ele.send_keys(Keys.CONTROL + "a", Keys.DELETE)
            if not speed:
                for c in text:
                    ele.send_keys(c)
                    time.sleep(random.uniform(0.05, 0.2))
            else:
                ele.send_keys(text)
            self.log(f"Sent keys to {xpath}: {text}")
            return True
        except Exception as e:
            self.log(f"Send keys failed: {e}")
            return False

    def get_text(self, xpath, timeout=None):
        timeout = timeout or self.default_timeout
        try:
            ele = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, xpath)))
            text = ele.text
            self.log(f"Got text from {xpath}: {text}")
            return text
        except Exception as e:
            self.log(f"Get text failed: {e}")
            return None

    def get_attr(self, xpath, attr, timeout=None):
        timeout = timeout or self.default_timeout
        try:
            ele = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            value = ele.get_attribute(attr)
            self.log(f"Got attribute {attr} from {xpath}: {value}")
            return value
        except Exception as e:
            self.log(f"Get attr failed: {e}")
            return None

from selenium import webdriver
if __name__ == "__main__":
    driver = webdriver.Chrome()
    selep = SeleP(driver, verbose=True)
    selep.wait_for_page_load()
    selep.wait_for_element((By.XPATH, "//button[@id='submit']"), EC.element_to_be_clickable)
    selep.click("//button[@id='submit']")
    selep.send_keys("//input[@name='q']", "hello", speed=False)
