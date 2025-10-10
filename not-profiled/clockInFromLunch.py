from asyncio import wait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import logging
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env from the current directory
folder = os.getenv("FOLDER_ROUTE")
log_file = f"{folder}\\not-profiled\\clockinfromlunch_log.txt"

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

ciklum_user = os.getenv("CIKLUM_USER")
ciklum_password = os.getenv("CIKLUM_PASSWORD")
oracle_url="https://ialmme.fa.ocs.oraclecloud.com/fscmUI/faces/FuseWelcome"

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(oracle_url)

wait = WebDriverWait(driver, 40) 

# Click Company SSO
logging.info("🔐 Esperando botón 'Company Single Sign-On'...")
sso_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Company Single Sign-On')]")))
sso_button.click()

# Google login
logging.info("✉️ Esperando campo de usuario de Google...")
email_input = wait.until(EC.visibility_of_element_located((By.ID, "identifierId")))
email_input.send_keys(ciklum_user)
driver.find_element(By.ID, "identifierNext").click()

logging.info("🔑 Esperando campo de contraseña...")
password_input = wait.until(EC.visibility_of_element_located((By.NAME, "Passwd")))
password_input.send_keys(ciklum_password)
driver.find_element(By.ID, "passwordNext").click()

# Pause until you confirm MFA on your phone
logging.info("📱 Esperando que completes MFA (detecto dashboard de Oracle)...")

# After login is complete, navigate and clock in from lunch
web_clock_button = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'flat-quickactions-item-link') and normalize-space(text())='Web Clock']"))
)
logging.info("✅ MFA completado, continuando...")
web_clock_button.click()

logging.info("🕒 Esperando botón 'Clock in from lunch'...")
clock_in_button = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//a[.//span[normalize-space(text())='In from Lunch']]")
    )
)

# Asegura visibilidad
driver.execute_script("arguments[0].scrollIntoView(true);", clock_in_button)
time.sleep(2)

# Simula clic nativo del navegador
driver.execute_script("""
var event = new MouseEvent('click', {
    view: window,
    bubbles: true,
    cancelable: true
});
arguments[0].dispatchEvent(event);
""", clock_in_button)

logging.info("✅ Clock in from lunch realizado correctamente.")
time.sleep(3)
driver.quit()