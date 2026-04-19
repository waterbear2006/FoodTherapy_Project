import csv
from pathlib import Path
from typing import Dict, Optional

class CategoryService:
    def __init__(self):
        self.data: Dict[str, dict] = {}
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.load_data()

    def load_data(self):
        csv_path = self.base_dir / "data" / "categories_info.csv"
        if not csv_path.exists():
            print(f"⚠️ Warning: {csv_path} not found.")
            return

        try:
            with open(csv_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get("name")
                    if name:
                        self.data[name] = {
                            "name": name,
                            "type": row.get("type", "category"),
                            "summary": row.get("summary", ""),
                            "ancient_quote": row.get("ancient_quote", "")
                        }
            print(f"✅ CategoryService: Loaded {len(self.data)} categorical definitions.")
        except Exception as e:
            print(f"❌ Error loading categories_info.csv: {e}")

    def get_by_name(self, name: str) -> Optional[dict]:
        return self.data.get(name)

# Singleton instance
category_service = CategoryService()
