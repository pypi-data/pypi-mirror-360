import os
import asyncio
import logging
from aiohttp import ClientSession
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Wg_web_client.exceptions import WGAutomationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class WireGuardWebClient:
    def __init__(self, ip: str, download_dir: str, chromedriver_path: str = None):
        self.ip = ip
        self.download_dir = os.path.abspath(download_dir)
        self.chromedriver_path = chromedriver_path
        os.makedirs(self.download_dir, exist_ok=True)

    async def _setup(self):
        try:
            from .driver_factory import create_driver
            loop = asyncio.get_running_loop()
            self.driver = await loop.run_in_executor(None, create_driver, self.download_dir, self.chromedriver_path)
            self.wait = WebDriverWait(self.driver, 3)
        except Exception as e:
            logger.error(f"Error in _setup: {str(e)}")
            raise

    async def create_key(self, key_name: str) -> str:
        await self._setup()
        try:
            logger.info(f"Creating key: {key_name}")
            self.driver.get(f"http://{self.ip}")

            new_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'New')]]")))
            new_button.click()

            input_field = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Name']")))
            input_field.send_keys(key_name)

            create_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Create')]")))
            create_button.click()

            await asyncio.sleep(1.5)

            client_blocks = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'relative overflow-hidden')]"))
            )

            target_block = None
            for block in reversed(client_blocks):
                try:
                    block.find_element(By.XPATH, f".//span[normalize-space(text())='{key_name}']")
                    target_block = block
                    break
                except:
                    continue

            if not target_block:
                logger.error(f"Key block not found for key_name: {key_name}")
                raise WGAutomationError(f"Не найден блок с именем ключа '{key_name}'")

            download_link = target_block.find_element(
                By.XPATH, ".//a[contains(@href, '/api/wireguard/client/') and contains(@href, '/configuration')]"
            )
            download_url = download_link.get_attribute("href")
            full_download_url = f"http://{self.ip}{download_url.lstrip('.')}" if not download_url.startswith("http") else download_url

            self.driver.get(full_download_url)

            result = await self._get_latest_downloaded_conf(key_name)
            logger.info(f"Key created successfully: {key_name}, config at {result}")
            return result
        except Exception as e:
            logger.error(f"Error creating key '{key_name}': {str(e)}")
            raise
        finally:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error quitting driver in create_key: {str(e)}")

    async def delete_key(self, key_name: str) -> None:
        await self._setup()
        try:
            logger.info(f"Deleting key: {key_name}")
            self.driver.get(f"http://{self.ip}")

            client_blocks = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'relative overflow-hidden')]"))
            )

            target_block = None
            for block in reversed(client_blocks):
                try:
                    block.find_element(By.XPATH, f".//span[normalize-space(text())='{key_name}']")
                    target_block = block
                    break
                except:
                    continue

            if not target_block:
                logger.error(f"Key not found for deletion: {key_name}")
                raise WGAutomationError(f"Не найден ключ для удаления: '{key_name}'")

            delete_button = target_block.find_element(By.XPATH, ".//button[@title='Delete Client']")
            delete_button.click()
            await asyncio.sleep(1)

            confirm_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Delete Client') and contains(@class,'bg-red-600')]"))
            )
            confirm_button.click()

            file_path = os.path.join(self.download_dir, f"{key_name}.conf")
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Deleted config file: {file_path}")
                except Exception as e:
                    logger.error(f"Error deleting config file {file_path}: {str(e)}")
            logger.info(f"Key deleted successfully: {key_name}")
        except Exception as e:
            logger.error(f"Error deleting key '{key_name}': {str(e)}")
            raise
        finally:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error quitting driver in delete_key: {str(e)}")

    async def get_key_status(self, key_name: str) -> bool:
        url = f"http://{self.ip}/api/wireguard/client"
        try:
            logger.info(f"Checking status for key: {key_name}")
            async with ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        logger.error(f"API request failed for {url}: Status {resp.status}")
                        raise Exception(f"Ошибка запроса: {resp.status}")
                    data = await resp.json()

            for client in data:
                if client["name"] == key_name:
                    logger.info(f"Key status for '{key_name}': {'enabled' if client['enabled'] else 'disabled'}")
                    return client["enabled"]

            logger.error(f"Client '{key_name}' not found on server")
            raise Exception(f"Клиент '{key_name}' не найден на сервере.")
        except Exception as e:
            logger.error(f"Error getting status for key '{key_name}': {str(e)}")
            raise

    async def _get_latest_downloaded_conf(self, key_name: str) -> str:
        try:
            target_path = os.path.join(self.download_dir, f"{key_name}.conf")
            for _ in range(30):
                files = [f for f in os.listdir(self.download_dir) if f.endswith(".conf")]
                if files:
                    source_path = os.path.join(self.download_dir, files[0])
                    os.rename(source_path, target_path)
                    return target_path
                await asyncio.sleep(1)
            logger.error("No configuration file found after download attempt")
            raise WGAutomationError("Файл конфигурации не найден после скачивания")
        except Exception as e:
            logger.error(f"Error in _get_latest_downloaded_conf: {str(e)}")
            raise

    async def enable_key(self, key_name: str) -> None:
        await self._setup()
        try:
            logger.info(f"Enabling key: {key_name}")
            self.driver.get(f"http://{self.ip}")
            await asyncio.sleep(1)

            blocks = self.driver.find_elements(By.XPATH, "//div[contains(@class,'border-b')]")
            for block in blocks:
                try:
                    block.find_element(By.XPATH, f".//span[normalize-space(text())='{key_name}']")
                    try:
                        toggle = block.find_element(By.XPATH, ".//div[@title='Enable Client']")
                        toggle.click()
                        logger.info(f"✅ Key '{key_name}' enabled")
                    except:
                        logger.warning(f"⚠️ Key '{key_name}' already enabled")
                    return
                except:
                    continue
            logger.error(f"Key '{key_name}' not found")
            print(f"❌ Ключ '{key_name}' не найден")
        except Exception as e:
            logger.error(f"Error enabling key '{key_name}': {str(e)}")
            raise
        finally:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error quitting driver in enable_key: {str(e)}")

    async def disable_key(self, key_name: str) -> None:
        await self._setup()
        try:
            logger.info(f"Disabling key: {key_name}")
            self.driver.get(f"http://{self.ip}")
            await asyncio.sleep(1)

            blocks = self.driver.find_elements(By.XPATH, "//div[contains(@class,'border-b')]")
            for block in blocks:
                try:
                    block.find_element(By.XPATH, f".//span[normalize-space(text())='{key_name}']")
                    try:
                        toggle = block.find_element(By.XPATH, ".//div[@title='Disable Client']")
                        toggle.click()
                        logger.info(f"⛔ Key '{key_name}' disabled")
                    except:
                        logger.warning(f"⚠️ Key '{key_name}' already disabled")
                    return
                except:
                    continue
            logger.error(f"Key '{key_name}' not found")
            print(f"❌ Ключ '{key_name}' не найден")
        except Exception as e:
            logger.error(f"Error disabling key '{key_name}': {str(e)}")
            raise
        finally:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error quitting driver in disable_key: {str(e)}")