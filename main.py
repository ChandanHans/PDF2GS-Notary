from vcs import check_for_updates

check_for_updates()

import os
import time
import shutil
import pandas as pd

from tqdm import tqdm
from src.pdf_processing import pdf_to_images
from src.excel_util import save_table
from src.image_processing import process_image, check_for_tesseract
from src.utils import *


def main():
    check_for_tesseract()
    pdf_files = [
        file for file in os.listdir(INPUT_FOLDER) if file.lower().endswith(".pdf")
    ]

    for pdf in pdf_files:
        time_start = time.time()
        pdf_path = f"{INPUT_FOLDER}/{pdf}"
        
        print(f"\nProcess Started For {pdf}\n")

        pdf_to_images(pdf_path, IMAGE_FOLDER, 200)

        images = [
            file for file in os.listdir(IMAGE_FOLDER) if file.lower().endswith(".png")
        ]
        images = sorted(images, key=extract_number)
        data = []

        print("\nSTART :\n")
        progress_bar = tqdm(images, ncols=60, bar_format="{percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}")
        for image in progress_bar:
            result = process_image(image)
            if result:
                data.append(result)
        print()

        df = pd.DataFrame(data)
        df.columns = [
            "Name",
            "Data Of Notoriety",
            "Notary",
            "Phone",            
            "Email",
            "Status",
        ]
        excel_path = pdf_path.replace(".pdf", ".xlsx").replace(INPUT_FOLDER, OUTPUT_FOLDER)
        save_table(
            df, excel_path
        )

        shutil.move(pdf_path, f"{COMPLETED_FOLDER}/{pdf}")
        print(
            f"Completed in {int(time.time() - time_start)} sec"
        )
        
    input("\n\nAll Files Completed")

if __name__ == "__main__":
    main()
