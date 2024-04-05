"""
Created by Samba Chennamsetty on 6/14/2023.
"""

# File: PDFGenerator.py

import base64
import json

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def get_edge_driver():
    options = webdriver.EdgeOptions()
    options.use_chromium = True
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    driver = webdriver.Edge(options=options)
    return driver


def write_to_a_file(result_data, target):
    with open(target, "wb") as file:
        file.write(result_data)


class PDFGenerator:
    def __init__(self):
        self.driver = get_edge_driver()
        self.print_ops = {
            "pageRanges": "1-1",
        }

    def send_devtools(self, cmd, params=None):
        resource = f"/session/{self.driver.session_id}/chromium/send_command_and_get_result"
        url = self.driver.command_executor._url + resource
        body = json.dumps({"cmd": cmd, "params": params})
        response = self.driver.command_executor._request("POST", url, body)
        if not response:
            raise Exception(response.get("value"))
        return response.get("value")

    def get_pdf_from_html(self, path: str, target: str, print_options: dict = None):
        self.driver.get(path)
        try:
            WebDriverWait(self.driver, 2).until(
                staleness_of(self.driver.find_element(by=By.TAG_NAME, value="html"))
            )
        except TimeoutException:
            calculated_print_options = {
                "landscape": False,
                "displayHeaderFooter": False,
                "printBackground": True,
                "preferCSSPageSize": True,
            }
            print_options = print_options if print_options is not None else self.print_ops
            calculated_print_options.update(print_options)
            result = self.send_devtools("Page.printToPDF", calculated_print_options)
            result_data = base64.b64decode(result["data"])
            write_to_a_file(result_data, target)

    def close_driver(self):
        self.driver.quit()

    def get_driver(self):
        return self.driver
