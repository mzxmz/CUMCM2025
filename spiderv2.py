from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException,TimeoutException
import time
import pandas as pd
import os


my_options = Options()
#my_options.add_argument("--headless")
driver = webdriver.Chrome(service = Service(), options = my_options)
wait = WebDriverWait(driver, 5)
flag = 1

url = "https://icisee.sjtu.edu.cn/jiaoshiml.html"
driver.get(url)
rows = []
li_list = []
li_list_text = []

while(True):
    tutors = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,"#article_list")))
    pre_li_list_text = [l for l in li_list_text]#8.20问题：翻页后立马27报错stale
    li_list = tutors[0].find_elements(By.CSS_SELECTOR,"li")
    li_list_text = [l.text for l in li_list]
    if(li_list_text == pre_li_list_text):
        break
    
    for li in li_list:
        flag = 1
        button = li.find_element(By.CSS_SELECTOR, "a[href*='sjtu']")
        name = li.find_element(By.CSS_SELECTOR, ".name").text
        original_window = driver.current_window_handle
        button.click()
        wait.until(EC.number_of_windows_to_be(2))
        new_window = [w for w in driver.window_handles if w!=original_window][0]
        driver.switch_to.window(new_window)
        
        #list = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".js-list")))
        #item = list[0].find_element(By.XPATH, '//div[div[@class="tit"][text()="研究方向"]]')
        try:
            item = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[div[@class="tit"][text()="研究方向"]]')))
            direction = item[0].find_element(By.CSS_SELECTOR, ".txt").text.strip()
            rows.append({"name": name, "direction": direction})
        except :
            pass
        
        driver.close()
        driver.switch_to.window(original_window)
        
    next_button = driver.find_element(By.XPATH, '//a[text()="下页"]')
    next_button.click()
    wait.until(EC.staleness_of(li_list[0]))
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,"#article_list")))
    time.sleep(3)


driver.quit()

df = pd.DataFrame(rows)
df.to_excel("集电学院导师研究方向.xlsx", index = False)
print("DONE")