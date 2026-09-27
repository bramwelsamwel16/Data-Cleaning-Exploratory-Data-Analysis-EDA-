"""
FIFA 21 Player Dataset — Data Cleaning Script
================================================
Source dataset: "FIFA 21 Messy, Raw Dataset For Cleaning/Exploring" (Kaggle)
https://www.kaggle.com/datasets/yagunnersya/fifa-21-messy-raw-dataset-for-cleaning-exploring

Cleans the raw FIFA 21 player export by fixing 11 data-quality issues.
Each messy column is REPLACED in place by its clean version (no duplicate
"old + new" columns left behind) — e.g. 'Value' goes from text "€67.5M"
straight to the number 67500000.0 in the same column.

  1. Corrupted column header ('OVA')
  2. Mojibake character encoding (€, ★, é, ü)
  3. Currency columns: text -> numeric (Value, Wage, Release Clause)
  4. Height / Weight: mixed-unit text -> numeric (cm / kg), replacing originals
  5. 'Team & Contract' multi-line field -> split into Team + Contract_Years
  6. Star ratings: symbol text -> numeric (W/F, SM, IR), replacing originals
  7. 'Hits' column whitespace/newline -> numeric
  8. 'Loan Date End' sparse column -> boolean 'On_Loan' flag (original dropped)
  9. Duplicate record removal
  10. Age outlier review (manual, documented — not auto-removed)
  11. Overall data type conversion (object -> float64 / int64)

Usage:
    python fifa21_cleaning.py

Input:  Copy_of_fifa21_raw_data.xlsx  (raw export)
Output: FIFA21_Cleaned_Full_Data.xlsx (cleaned dataset, no duplicate columns)
"""

import re
import numpy as np
import pandas as pd

INPUT_FILE = "Copy_of_fifa21_raw_data.xlsx"
OUTPUT_FILE = "FIFA21_Cleaned_Full_Data.xlsx"


def fix_mojibake(text):
    """Stage 2: Repair corrupted UTF-8 characters (mojibake)."""
    if not isinstance(text, str):
        return text
    replacements = {
        "â‚¬": "€",
        "â˜…": "★",
        "Ã©": "é",
        "Ã¡": "á",
        "Ã­": "í",
        "Ã³": "ó",
        "Ã±": "ñ",
        "Ã¼": "ü",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text


def money_to_num(x):
    """Stage 3: Convert '€67.5M' / '€560K' style text to a numeric EUR value."""
    if pd.isna(x):
        return np.nan
    x = fix_mojibake(str(x)).replace("€", "").strip()
    if x.endswith("M"):
        return float(x[:-1]) * 1_000_000
    elif x.endswith("K"):
        return float(x[:-1]) * 1_000
    try:
        return float(x)
    except ValueError:
        return np.nan


def height_to_cm(x):
    """Stage 4: Convert 5'7\" style height text to centimetres."""
    if pd.isna(x):
        return np.nan
    m = re.match(r"(\d+)'(\d+)\"", str(x))
    if m:
        feet, inches = int(m.group(1)), int(m.group(2))
        return round((feet * 12 + inches) * 2.54, 1)
    return np.nan


def weight_to_kg(x):
    """Stage 4: Convert '159lbs' style weight text to kilograms."""
    if pd.isna(x):
        return np.nan
    m = re.match(r"(\d+)lbs", str(x))
    if m:
        return round(int(m.group(1)) * 0.453592, 1)
    return np.nan


def parse_team_contract(x):
    """Stage 5: Split the combined 'Team & Contract' multi-line field."""
    if pd.isna(x):
        return pd.Series([np.nan, np.nan])
    x = fix_mojibake(x)
    lines = [l.strip() for l in str(x).split("\n") if l.strip()]
    team = lines[0] if len(lines) > 0 else np.nan
    contract = lines[1] if len(lines) > 1 else np.nan
    return pd.Series([team, contract])


def star_to_num(x):
    """Stage 6: Extract the numeric rating from '4 ★' style star-rating text."""
    if pd.isna(x):
        return np.nan
    m = re.search(r"(\d+)", str(x))
    return int(m.group(1)) if m else np.nan


def clean_fifa21(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()

    # ---- Stage 1: Fix corrupted column header ----
    clean = clean.rename(columns={"â†“OVA": "OVA"})

    # ---- Stage 2: Fix mojibake in name/nationality text columns ----
    for c in ["LongName", "Name", "Nationality"]:
        clean[c] = clean[c].apply(fix_mojibake)

    # ---- Stage 3: Currency text -> numeric (REPLACES original column) ----
    clean["Value"] = clean["Value"].apply(money_to_num)
    clean["Wage"] = clean["Wage"].apply(money_to_num)
    clean["Release Clause"] = clean["Release Clause"].apply(money_to_num)

    # ---- Stage 4: Height / Weight -> numeric (REPLACES original column) ----
    clean["Height"] = clean["Height"].apply(height_to_cm)   # now in cm
    clean["Weight"] = clean["Weight"].apply(weight_to_kg)   # now in kg

    # ---- Stage 5: Split 'Team & Contract' into two new columns, drop original ----
    clean[["Team", "Contract_Years"]] = df["Team & Contract"].apply(parse_team_contract)
    clean = clean.drop(columns=["Team & Contract"])

    # ---- Stage 6: Star ratings -> numeric (REPLACES original column) ----
    for c in ["W/F", "SM", "IR"]:
        clean[c] = clean[c].apply(star_to_num)

    # ---- Stage 7: Clean 'Hits' column ----
    clean["Hits"] = clean["Hits"].astype(str).str.strip()
    clean["Hits"] = pd.to_numeric(clean["Hits"], errors="coerce")

    # ---- Stage 8: 'Loan Date End' -> boolean flag, drop original sparse column ----
    clean["On_Loan"] = clean["Loan Date End"].notna()
    clean = clean.drop(columns=["Loan Date End"])

    # ---- Stage 9: Remove exact duplicate rows ----
    before_rows = len(clean)
    clean = clean.drop_duplicates()
    print(f"Removed {before_rows - len(clean)} duplicate row(s).")

    # ---- Stage 10: Age outlier review (documented, not auto-removed) ----
    outliers = clean[clean["Age"] > 45][["Name", "Age"]]
    if not outliers.empty:
        print("Age outliers found (reviewed, retained):")
        print(outliers.to_string(index=False))

    # ---- Stage 11: dtype conversion is implicit in the numeric parsing above ----
    return clean


def main():
    df = pd.read_excel(INPUT_FILE)
    print(f"Loaded raw data: {df.shape[0]} rows x {df.shape[1]} columns")

    cleaned = clean_fifa21(df)
    print(f"Cleaned data: {cleaned.shape[0]} rows x {cleaned.shape[1]} columns "
          f"(no duplicate 'old + new' columns — each field cleaned in place)")

    cleaned.to_excel(OUTPUT_FILE, index=False)
    print(f"Saved cleaned file to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
