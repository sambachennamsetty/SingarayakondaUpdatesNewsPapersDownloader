"""
Created by Samba Chennamsetty on 6/14/2023.
"""

import os

import PyPDF2


def merge_pdfs(pdf_files, output_file):
    try:
        merger = PyPDF2.PdfMerger()
        for pdf_file in pdf_files:
            with open(pdf_file, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                merger.append(reader)

        with open(output_file, 'wb') as f:
            merger.write(f)

        # Delete the original files
        for pdf_file in pdf_files:
            os.remove(pdf_file)

    except Exception as err:
        print(f"Merge files failed:  {err}")
