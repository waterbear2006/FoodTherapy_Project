import pandas as pd
import os

def check_csv(file_path):
    print(f"--- Checking {file_path} ---")
    try:
        # Try different encodings
        for encoding in ['utf-8', 'gbk', 'utf-8-sig']:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                print(f"Successfully read with encoding: {encoding}")
                print("Columns:", df.columns.tolist())
                print("Sample Data:")
                print(df.head(2))
                return
            except Exception:
                continue
        print("Failed to read with common encodings")
    except Exception as e:
        print(f"Error: {e}")

data_dir = r"d:\bupt\Project\FoodTherapy_Project-main\FoodTherapy_Project-main\Backened\data"
check_csv(os.path.join(data_dir, "caipu_enriched.csv"))
check_csv(os.path.join(data_dir, "shicai_enriched.csv"))
