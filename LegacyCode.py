from Constants import VAARTHA


# def vaartha(self):
#     try:
#         vaartha_date = self.today_date.strftime("%d/%m/%Y")
#
#         # Get the URLS from config file by section and key
#         url = self.config['newspapers']['vaartha_paper_url']
#         url = url.format(vaartha_date)
#
#         self.driver.get(url)
#         current_url = self.driver.current_url
#
#         page_no = 1
#         vaartha_files = []
#
#         print(f"Reading {VAARTHA} paper.")
#         self.driver.get(current_url)
#         while page_no <= 12:
#             page_name = self.prepare_file_name(VAARTHA, str(page_no))
#             self.get_pdf_from_html(page_name)
#             vaartha_files.append(page_name)
#
#             if page_no != 12:
#                 navigate_to_next_page(self.driver, current_url)
#                 current_url = self.driver.current_url
#
#             page_no += 1
#             time.sleep(2)  # Adding a short delay to avoid overwhelming the page with rapid navigation
#
#         self.merge_files(vaartha_files, VAARTHA)
#         print(f"{VAARTHA} pdf has been generated.")
#         self.dropbox_manager.upload_files(self.today_date_str)
#     except Exception as err:
#         print(f"Exception in {VAARTHA} paper: {err}")