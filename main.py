"""
Created by Samba Chennamsetty on 6/14/2023.
"""

import base64
import configparser
import json
import time
from datetime import date, timedelta

import requests
from selenium.common import TimeoutException
from selenium.webdriver.support.expected_conditions import staleness_of

from Constants import PRAJASAKTI_MAIN, PRAJASAKTI_DT, VISALANDRA, VAARTHA, ANDHARAJOTHI, SAKSHI, EENADU, ANDHRA_PRABHA
from DropboxManager import DropboxManager, remove_folder
from PDFGenerator import PDFGenerator, write_to_a_file
from PdfUtils import merge_pdfs


def accept_cookies(cookie, driver):
    try:
        accept_cookies_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, cookie)))
        accept_cookies_button.click()
    except Exception as e:
        print(f"Could not find or click 'Accept Cookies' button: {e}")

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def add_right_zero_to_elements(driver):
    try:
        # Locate and modify the "Next_Page" element
        next_page_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "Next_Page"))
        )
        driver.execute_script("arguments[0].style.right = '0px';", next_page_element)

        # Locate and modify the "Prev_Page" element
        prev_page_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "Prev_Page"))
        )
        driver.execute_script("arguments[0].style.left = '0px';", prev_page_element)

    except Exception as e:
        print(f"Error modifying style: {e}")


def add_right_zero(driver):
    try:
        # Wait for the element with id 'Next_Page' to be present
        next_page_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "Next_Page"))
        )

        # Execute JavaScript to add 'right: 0px' style
        driver.execute_script("arguments[0].style.right = '0px';", next_page_element)

    except Exception as e:
        print(f"Error modifying style: {e}")

def find_and_click_buttons(driver):
    try:
        # Wait for both buttons with id 'button-1' to be present
        buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.ID, "button-1"))
        )

        # Loop through found buttons and click based on text content
        for button in buttons:
            text = button.text
            if text == "X":
                button.click()
            elif text == "x":
                button.click()

    except Exception as e:
        print(f"Could not find or click buttons: {e}")

def hide_social_share_button(driver):
    try:
        # Wait for the social share button to be present
        social_share_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "social_share_box_Container"))
        )

        # Use JavaScript to hide the element
        driver.execute_script("arguments[0].style.display = 'none';", social_share_button)
        #print("Social share button hidden.")
    except Exception as e:
        print(f"Could not find or hide social share button: {e}")

def load_page(driver, url):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.url_contains('pgid'))  # Wait until the current URL contains 'pgid'


def navigate_to_next_eenadu_page(driver):
    try:
        next_page = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@data-original-title='Next Page']")))
        next_page.click()
    except Exception as err:
        print(f"Couldn't find the next page..! Error: {err}")


def get_number_of_pages(driver):
    try:
        # Locate the select element by its ID
        select_element = driver.find_element(By.ID, "myPageList")

        # Get all options within the select element
        options = select_element.find_elements(By.TAG_NAME, "option")

        # Count the number of options
        num_options = len(options)

        return num_options
    except Exception as e:
        print(f"Error finding options: {e}")


def navigate_to_next_page(driver, next_url):
    try:
        next_page = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'Next_Page')))
        next_page.click()
        hide_social_share_button(driver)
        WebDriverWait(driver, 5).until(lambda driver: driver.current_url != next_url)
    except Exception as err:
        print(f"Couldn't find the next page..! Error: {err}")


def download_surya_pdf_files(driver, url, filename, xpath_expression):
    driver.get(url)

    try:
        if xpath_expression:
            new_elements = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath_expression)))
            new_elements.click()

            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "btn-pdfdownload")))
            href_value = element.get_attribute("href")
            response = requests.get(href_value)

            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"{filename} downloaded successfully.")
            else:
                print(f"Failed to download {filename}.")
        else:
            print("Invalid XPath expression.")

    except Exception as err:
        print(f"Exception while downloading {filename}: {err}")


def skip_ads(driver):
    try:
        button = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//button[text()='SKIP']"))
        )
        button.click()
    except Exception as err:
        print(f"Exception in Skip ads: {err}")


class NewspaperDownloader:
    def __init__(self):
        # Loading config file
        self.config = configparser.ConfigParser()
        self.config.read('config.properties')

        # Today date in String format
        self.today_date = date.today()
        self.today_date = self.today_date + timedelta(days=1)
        self.today_date_str = self.today_date.strftime("%Y-%m-%d")

        # Initializing PDFGenerator Class
        self.pdf_generator = PDFGenerator()
        self.driver = self.pdf_generator.get_driver()

        # Initializing DropboxManager Class
        self.dropbox_manager = DropboxManager()
        self.dropbox_manager.create_folder(self.today_date_str)
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

    def get_pdf_from_html(self, target: str, print_options: dict = None):
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

            try:
                result = self.send_devtools("Page.printToPDF", calculated_print_options)

                if "data" not in result:
                    raise ValueError("Expected 'data' key in result, but it was not found.")

                result_data = base64.b64decode(result["data"])
                write_to_a_file(result_data, target)
            except Exception as e:
                print(f"Error in PDF generation: {e}")

    def prepare_file_name(self, paper_name, page_no):
        return f"{self.today_date_str}/{paper_name}_{page_no}.pdf"

    def merge_files(self, files, paper_name):
        merge_pdfs(files, f"{self.today_date_str}/{paper_name}.pdf")

    def download_prajasakti_paper(self, url, paper_title):
        try:
            print(f"Reading {paper_title} paper.")
            praja_sakti_files = []
            for page_no in range(1, 9):
                page_name = self.prepare_file_name(paper_title, page_no)
                praja_sakti_files.append(page_name)
                self.pdf_generator.get_pdf_from_html(url.format(self.today_date_str, page_no), page_name)
            self.merge_files(praja_sakti_files, paper_title)
            print(f"{paper_title} pdf has been generated.")
            self.dropbox_manager.upload_files(self.today_date_str)
        except Exception as err:
            print(f"Exception in {paper_title} paper: {err}")

    def prajasakthi(self):
        # Get the URLS from config file by section and key
        main_paper_url = self.config['newspapers']['prajasakthi_main_paper_url']
        district_paper_url = self.config['newspapers']['prajasakthi_district_paper_url']

        self.download_prajasakti_paper(main_paper_url, PRAJASAKTI_MAIN)
        self.download_prajasakti_paper(district_paper_url, PRAJASAKTI_DT)

    def surya(self):

        # Get the URLS from config file by section and key
        main_paper_url = self.config['newspapers']['surya_main_paper_url']
        district_paper_url = self.config['newspapers']['surya_district_paper_url']

        main_paper_name = f"{self.today_date_str}/SuryaMain.pdf"
        district_paper_name = f"{self.today_date_str}/SuryaDistrict.pdf"

        main_paper_xpath_expression = "//a[@data-linktype='edition-link' and @data-cat_ids='8']"
        district_paper_xpath_expression = "//a[@data-linktype='edition-link' and @data-cat_ids='18']"

        download_surya_pdf_files(self.driver, main_paper_url, main_paper_name, main_paper_xpath_expression)
        download_surya_pdf_files(self.driver, district_paper_url, district_paper_name, district_paper_xpath_expression)

        self.dropbox_manager.upload_files(self.today_date_str)

    def andhra_jyothi(self):
        try:
            abn_date = self.today_date.strftime("%d/%m/%Y")

            # Get the URLS from config file by section and key
            url = self.config.get('newspapers', 'abn_paper_url')
            url = url.format(abn_date)

            load_page(self.driver, url)
            current_url = self.driver.current_url

            accept_cookies("gdprContinue", self.driver)
            hide_social_share_button(self.driver)

            page_no = 1
            abn_files = []

            print(f"Reading {ANDHARAJOTHI} paper.")
            self.driver.get(current_url)
            hide_social_share_button(self.driver)
            add_right_zero(self.driver)
            while page_no <= 7:
                page_name = self.prepare_file_name(ANDHARAJOTHI, str(page_no))
                self.get_pdf_from_html(page_name)
                # self.pdf_generator.get_pdf_from_html(current_url, page_name)
                abn_files.append(page_name)

                if page_no != 7:
                    navigate_to_next_page(self.driver, current_url)
                    add_right_zero_to_elements(self.driver)
                    current_url = self.driver.current_url

                page_no += 1
                time.sleep(2)  # Adding a short delay to avoid overwhelming the page with rapid navigation

            self.merge_files(abn_files, ANDHARAJOTHI)
            print(f"{ANDHARAJOTHI} pdf has been generated.")
            self.dropbox_manager.upload_files(self.today_date_str)

        except Exception as err:
            print(f"Exception in {ANDHARAJOTHI} paper: {err}")

    def sakshi(self):
        try:
            sakshi_date = self.today_date.strftime("%d/%m/%Y")

            # Get the URLS from config file by section and key
            url = self.config['newspapers']['sakshi_paper_url']
            print(self.config)
            url = url.format(sakshi_date)

            load_page(self.driver, url)
            current_url = self.driver.current_url

            find_and_click_buttons(self.driver)
            accept_cookies("gdprContinue", self.driver)
            skip_ads(self.driver)
            hide_social_share_button(self.driver)

            page_no = 1
            sakshi_files = []

            print(f"Reading {SAKSHI} paper.")
            self.driver.get(current_url)
            hide_social_share_button(self.driver)
            add_right_zero(self.driver)
            while page_no <= 8:
                page_name = self.prepare_file_name(SAKSHI, str(page_no))
                self.get_pdf_from_html(page_name)
                # self.pdf_generator.get_pdf_from_html(current_url, page_name)
                sakshi_files.append(page_name)

                if page_no != 8:
                    navigate_to_next_page(self.driver, current_url)
                    add_right_zero_to_elements(self.driver)
                    current_url = self.driver.current_url

                page_no += 1
                time.sleep(2)  # Adding a short delay to avoid overwhelming the page with rapid navigation

            self.merge_files(sakshi_files, SAKSHI)
            print(f"{SAKSHI} pdf has been generated.")
            self.dropbox_manager.upload_files(self.today_date_str)

        except Exception as err:
            print(f"Exception in {SAKSHI} paper: {err}")

    def eenadu(self):
        try:
            eenadu_date = self.today_date.strftime("%d/%m/%Y")

            # Get the URLS from config file by section and key
            url = self.config['newspapers']['eenadu_paper_url']
            url = url.format(eenadu_date)

            self.driver.get(url)
            current_url = self.driver.current_url

            page_no = 1
            eenadu_files = []

            print(f"Reading {EENADU} paper.")
            self.driver.get(current_url)
            no_of_pages = get_number_of_pages(self.driver)
            while page_no <= no_of_pages:
                page_name = self.prepare_file_name(EENADU, str(page_no))
                self.get_pdf_from_html(page_name)
                eenadu_files.append(page_name)

                if page_no != no_of_pages:
                    navigate_to_next_eenadu_page(self.driver)
                page_no += 1
                time.sleep(3)  # Adding a short delay to avoid overwhelming the page with rapid navigation

            self.merge_files(eenadu_files, EENADU)
            print(f"{EENADU} pdf has been generated.")
            self.dropbox_manager.upload_files(self.today_date_str)
        except Exception as err:
            print(f"Exception in {EENADU} paper: {err}")

    def vaartha(self):
        try:
            vaartha_paper_name = f"{self.today_date_str}/Vaartha.pdf"

            # Get the URLS from config file by section and key
            # url = self.config['newspapers']['vaartha_paper_url']
            # url = "https://epaper.vaartha.com/epaper/default/open?id=20"
            url = "https://epaper.vaartha.com/"

            self.driver.get(url)
            # Locate the link by its text
            element = self.driver.find_element(By.LINK_TEXT, "Ongole main")
            # Get the href attribute value
            href_value = element.get_attribute("href")
            self.driver.get(href_value)
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "btn-pdfdownload")))
            pdf_href_value = element.get_attribute("href")
            response = requests.get(pdf_href_value)
            if response.status_code == 200:
                with open(vaartha_paper_name, 'wb') as f:
                    f.write(response.content)
                print(f"{vaartha_paper_name} downloaded successfully.")
            else:
                print(f"Failed to download {vaartha_paper_name}.")
            self.dropbox_manager.upload_files(self.today_date_str)
        except Exception as err:
            print(f"Exception in {VAARTHA} paper: {err}")


    def visalandra(self):
        try:
            visalandra_date = self.today_date.strftime("%d/%m/%Y")

            # Get the URLS from config file by section and key
            url = self.config['newspapers']['visalandra_paper_url']
            url = url.format(visalandra_date)

            self.driver.get(url)
            current_url = self.driver.current_url
            accept_cookies("gdprContinue", self.driver)
            hide_social_share_button(self.driver)
            add_right_zero(self.driver)

            page_no = 1
            visalandra_files = []

            print(f"Reading {VISALANDRA} paper.")
            while page_no <= 8:
                page_name = self.prepare_file_name(VISALANDRA, str(page_no))
                self.get_pdf_from_html(page_name)
                visalandra_files.append(page_name)

                if page_no != 8:
                    navigate_to_next_page(self.driver, current_url)
                    add_right_zero_to_elements(self.driver)
                    current_url = self.driver.current_url

                page_no += 1

            self.merge_files(visalandra_files, VISALANDRA)
            print(f"{VISALANDRA} pdf has been generated.")
            self.dropbox_manager.upload_files(self.today_date_str)
        except Exception as err:
            print(f"Exception in {VISALANDRA} paper: {err}")

    def andhra_prabha(self):
        try:
            andhra_prabha_date = self.today_date.strftime("%d/%m/%Y")

            # Get the URLS from config file by section and key
            url = self.config['newspapers']['andhra_prabha_paper_url']
            url = url.format(andhra_prabha_date)

            load_page(self.driver, url)
            current_url = self.driver.current_url

            accept_cookies("gdprContinue", self.driver)
            hide_social_share_button(self.driver)

            page_no = 1
            andhra_prabha_files = []

            print(f"Reading {ANDHRA_PRABHA} paper.")
            self.driver.get(current_url)
            hide_social_share_button(self.driver)
            add_right_zero(self.driver)
            while page_no <= 12:
                page_name = self.prepare_file_name(ANDHRA_PRABHA, str(page_no))
                self.get_pdf_from_html(page_name)
                # self.pdf_generator.get_pdf_from_html(current_url, page_name)
                andhra_prabha_files.append(page_name)

                if page_no != 12:
                    navigate_to_next_page(self.driver, current_url)
                    add_right_zero_to_elements(self.driver)
                    current_url = self.driver.current_url

                page_no += 1
                time.sleep(3)  # Adding a short delay to avoid overwhelming the page with rapid navigation

            self.merge_files(andhra_prabha_files, ANDHRA_PRABHA)
            print(f"{ANDHRA_PRABHA} pdf has been generated.")
            self.dropbox_manager.upload_files(self.today_date_str)

        except Exception as err:
            print(f"Exception in {ANDHRA_PRABHA} paper: {err}")

    def execute_download(self):
        self.prajasakthi()
        self.andhra_prabha()
        self.surya()
        self.visalandra()
        self.vaartha()
        self.eenadu()
        self.sakshi()
        self.andhra_jyothi()
        # time.sleep(600)
        remove_folder()


# Usage:
downloader = NewspaperDownloader()
downloader.execute_download()
