import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WGAutomationError(Exception):
    pass


class WireGuardWebClient:
    def __init__(self, ip: str, download_dir: str = "./downloads"):
        self.ip = ip
        self.download_dir = os.path.abspath(download_dir)

        os.makedirs(self.download_dir, exist_ok=True)

    def _setup(self):
        from .driver_factory import create_driver
        self.driver = create_driver(self.download_dir)
        self.wait = WebDriverWait(self.driver, 10)

    def create_key(self, key_name: str) -> str:
        self._setup()
        try:
            self.driver.get(f"http://{self.ip}")

            new_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'New')]]"))
            )
            new_button.click()

            input_field = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Name']"))
            )
            input_field.send_keys(key_name)

            create_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Create')]"))
            )
            create_button.click()

            time.sleep(1.5)

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
                raise WGAutomationError(f"Не найден блок с именем ключа '{key_name}'")

            download_link = target_block.find_element(
                By.XPATH, ".//a[contains(@href, '/api/wireguard/client/') and contains(@href, '/configuration')]"
            )
            download_url = download_link.get_attribute("href")
            full_download_url = f"http://{self.ip}{download_url.lstrip('.')}" if not download_url.startswith("http") else download_url

            self.driver.get(full_download_url)

            return self._get_latest_downloaded_conf()

        finally:
            self.driver.quit()

    def delete_key(self, key_name: str) -> None:
        self._setup()
        try:
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
                raise WGAutomationError(f"Не найден ключ для удаления: '{key_name}'")

            delete_button = target_block.find_element(
                By.XPATH, ".//button[@title='Delete Client']"
            )
            delete_button.click()
            time.sleep(1)

            confirm_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Delete Client') and contains(@class,'bg-red-600')]"))
            )
            confirm_button.click()

            for file in os.listdir(self.download_dir):
                if key_name in file and file.endswith(".conf"):
                    os.remove(os.path.join(self.download_dir, file))

        finally:
            self.driver.quit()

    def get_key_status(self, key_name: str) -> bool:
        self._setup()
        try:
            self.driver.get(f"http://{self.ip}")
            time.sleep(1)

            blocks = self.driver.find_elements(By.XPATH, "//div[contains(@class,'border-b')]")
            for block in blocks:
                try:
                    block.find_element(By.XPATH, f".//span[contains(text(), '{key_name}')]")
                    status_elem = block.find_element(By.XPATH, ".//div[@title='Disable Client' or @title='Enable Client']")

                    return status_elem.get_attribute("title") == "Disable Client"
                except Exception:
                    continue

            raise WGAutomationError(f"Ключ с именем '{key_name}' не найден")
        finally:
            self.driver.quit()

    def _get_latest_downloaded_conf(self) -> str:
        for _ in range(10):
            files = [f for f in os.listdir(self.download_dir) if f.endswith(".conf")]
            if files:
                files.sort(key=lambda x: os.path.getctime(os.path.join(self.download_dir, x)), reverse=True)
                return os.path.join(self.download_dir, files[0])
            time.sleep(1)
        raise WGAutomationError("Файл конфигурации не найден после скачивания")

    def enable_key(self, key_name: str) -> None:
        """Включает ключ (если выключен)."""
        self._setup()
        try:
            self.driver.get(f"http://{self.ip}")
            time.sleep(1)

            blocks = self.driver.find_elements(By.XPATH, "//div[contains(@class,'border-b')]")
            for block in blocks:
                try:
                    block.find_element(By.XPATH, f".//span[normalize-space(text())='{key_name}']")
                    try:
                        toggle = block.find_element(By.XPATH, ".//div[@title='Enable Client']")
                        toggle.click()
                        print(f"✅ Ключ '{key_name}' включён")
                    except:
                        print(f"⚠️ Ключ '{key_name}' уже включён")
                    return
                except Exception:
                    continue
            print(f"❌ Ключ '{key_name}' не найден")
        finally:
            self.driver.quit()

    def disable_key(self, key_name: str) -> None:
        """Выключает ключ (если включён)."""
        self._setup()
        try:
            self.driver.get(f"http://{self.ip}")
            time.sleep(1)

            blocks = self.driver.find_elements(By.XPATH, "//div[contains(@class,'border-b')]")
            for block in blocks:
                try:
                    block.find_element(By.XPATH, f".//span[normalize-space(text())='{key_name}']")
                    try:
                        toggle = block.find_element(By.XPATH, ".//div[@title='Disable Client']")
                        toggle.click()
                        print(f"⛔ Ключ '{key_name}' выключен")
                    except:
                        print(f"⚠️ Ключ '{key_name}' уже выключен")
                    return
                except Exception:
                    continue
            print(f"❌ Ключ '{key_name}' не найден")
        finally:
            self.driver.quit()

