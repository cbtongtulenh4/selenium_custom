









class SeleP:
    

    



    
    def wait_for_page_load(driver):
        try:
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
        except:
            pass

    def wait_for_element(driver, type_handler, timeout=10, skip_error=True):
        if skip_error:
            try:
                WebDriverWait(driver, timeout).until(type_handler)
                return True
            except:
                pass
            return False
        WebDriverWait(driver, timeout).until(type_handler)
        return True

    def click(driver: WebDriver, xpath):
        try:
            driver.find_element(By.XPATH, xpath).click()
            return
        except: pass
        try:
            element = driver.find_element(By.XPATH, xpath)
            driver.execute_script("arguments[0].click();", element)
            time.sleep(2)
            if not driver.find_elements(By.XPATH, xpath):
                return
        except: pass
        try:
            element = driver.find_element(By.XPATH, xpath)
            actions = ActionChains(driver)
            # actions.move_to_element_with_offset(element, random_x, random_y).click().perform()
            actions.move_to_element(element).click().perform()
            return
        except: pass



    def is_element_in_viewport(driver, element):
        return driver.execute_script("""
            var element = arguments[0];
            var rect = element.getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        """, element)


    def scroll_into_view(driver: WebDriver, xpath):
        ele = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].scrollIntoView(false);", ele)#{ behavior: 'smooth', block: 'center' }
        wait_for_element(
            driver,
            EC.visibility_of_element_located((By.XPATH, xpath)),
            5
        )
        time.sleep(1)
        actions = ActionChains(driver)
        cnt = 10
        while not is_element_in_viewport(driver, ele) and cnt > 0:
            element_position = driver.execute_script("return arguments[0].getBoundingClientRect();", ele)
            if element_position['top'] < 0:
                actions.send_keys(Keys.ARROW_UP).perform()
            else:
                actions.send_keys(Keys.ARROW_DOWN).perform()
            time.sleep(0.1) 
            cnt -= 1

    def send_keys(driver: WebDriver, xpath_ele: str, text: str, speed=True):
        WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.XPATH, xpath_ele)))
        try:
            click(driver, xpath_ele)
            if not speed:
                time.sleep(rand.uniform(0.5, 1))
        except:
            pass
        driver.find_element(By.XPATH, xpath_ele).send_keys(Keys.CONTROL + "a")
        if not speed:
            time.sleep(rand.uniform(2, 3))
        driver.find_element(By.XPATH, xpath_ele).send_keys(Keys.DELETE)
        if not speed:
            time.sleep(rand.uniform(2, 3))
        driver.find_element(By.XPATH, xpath_ele).send_keys(text)


















