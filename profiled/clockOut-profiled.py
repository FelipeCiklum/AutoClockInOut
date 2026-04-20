from asyncio import wait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env from the current directory
folder = os.getenv("FOLDER_ROUTE")
log_file = f"{folder}\\profiled\\logs\\clockout_profiled_log.txt"

logging.basicConfig(
    filename=log_file,
    filemode='w',  # overwrite the file each run
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Hora objetivo (17:00 am)
scheduled_time = datetime.now().replace(hour=17, minute=0, second=0, microsecond=0)
# Máximo retraso permitido
max_delay = timedelta(hours=7)

# Comprobar si estamos dentro de la ventana
if datetime.now() > scheduled_time + max_delay:
    logging.info("⏰ Demasiado tarde para ejecutar la tarea")
    exit()  # Salir sin hacer nada

source_profile = os.getenv("CHROME_PROFILE_ROUTE")
profile="Default"
oracle_url="https://ialmme.fa.ocs.oraclecloud.com/fscmUI/faces/FuseWelcome"

options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={source_profile}")
options.add_argument(f"--profile-directory={profile}")
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(oracle_url)

wait = WebDriverWait(driver, 20) 

# Click Company SSO
try:
    logging.info("🔐 Esperando botón 'Company Single Sign-On'...")
    sso_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Company Single Sign-On')]")))
    sso_button.click()
except TimeoutException:
    logging.warning("⚙️ Botón 'Company Single Sign-On' no encontrado. Asumimos que ya estamos logueados.")
except Exception as e:
    logging.error(f"❌ Error inesperado buscando 'Company Single Sign-On': {e}")

# After login is complete, navigate and clock out
logging.info("🔐 Esperando botón 'Web Clock'...")
web_clock_button = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//a[contains(@class,'flat-quickactions-item-link') and normalize-space(text())='Web Clock']"))
)
web_clock_button.click()

logging.info("🕒 Esperando botón 'Clock Out'...")
clock_out_button = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//a[.//span[normalize-space(text())='Clock Out']]")
    )
)

# Asegura visibilidad
driver.execute_script("arguments[0].scrollIntoView(true);", clock_out_button)
time.sleep(2)

# Simula clic nativo del navegador
driver.execute_script("""
var event = new MouseEvent('click', {
    view: window,
    bubbles: true,
    cancelable: true
});
arguments[0].dispatchEvent(event);
""", clock_out_button)

logging.info("✅ Clock Out realizado correctamente.")
time.sleep(3)
driver.quit()
