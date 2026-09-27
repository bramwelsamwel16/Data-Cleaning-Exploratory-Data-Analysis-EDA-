FIFA 21 Player Dataset — Data Cleaning & EDA
Exploratory data analysis and cleaning project on the raw FIFA 21 player dataset (18,979 players, 77 columns). The raw export was heavily "dirty" — corrupted character encoding, mixed-unit text fields, and numeric values stored as text. This project diagnoses and fixes 11 distinct data-quality issues, replacing each messy column with a single clean version (no leftover duplicate "old + new" columns) using both Python (pandas) and Excel formulas.
---
📂 Project Structure
```
├── fifa21_cleaning.py                  # Python (pandas) cleaning script
├── FIFA21_Cleaned_Full_Data.xlsx       # Final cleaned dataset (18,978 rows, 78 columns)
├── FIFA21_Excel_Formulas_Demo.xlsx     # Excel-formula demo (13 sample rows)
├── FIFA21_EDA_Before_After_11_Stages.pdf   # Visual before/after report
└── README.md
```
---
📊 Dataset
Source: FIFA 21 Messy, Raw Dataset For Cleaning/Exploring — scraped from SoFIFA.com
Raw size: 18,979 rows × 77 columns
Cleaned size: 18,978 rows × 78 columns (1 exact duplicate removed; 2 messy columns dropped after being split/converted; 3 new columns added)
Key fields: `Name`, `Age`, `Nationality`, `OVA`, `Value`, `Wage`, `Release Clause`, `Height`, `Weight`, `Team`, `Contract_Years`, plus 50+ skill attributes
---
🧹 Issues Found & Fixed (11 Stages)
#	Issue	Fix
1	Corrupted column header (`â†“OVA`)	Renamed to `OVA`
2	Mojibake encoding (`â‚¬`, `â˜…`, `Ã©` instead of `€`, `★`, `é`)	Character-mapping replacement
3	Currency stored as text (`"€67.5M"`)	Converted in place: `Value`, `Wage`, `Release Clause` are now plain numbers
4	Height/Weight as mixed-unit text (`5'7"`, `159lbs`)	Converted in place: `Height` (cm), `Weight` (kg)
5	`Team & Contract` combined in one multi-line field	Split into new `Team` and `Contract_Years` columns; original column dropped
6	Star ratings as symbol text (`"4 ★"`)	Converted in place: `W/F`, `SM`, `IR` are now plain numbers
7	`Hits` column had leading whitespace/newlines	Stripped and converted to numeric
8	`Loan Date End` missing in 94.7% of rows	Replaced with a boolean `On_Loan` flag; original sparse column dropped
9	1 exact duplicate row (ID 251698)	Removed with `drop_duplicates()`
10	Age outlier (max age = 53, K. Miura)	Manually reviewed — confirmed legitimate, retained
11	Multiple numeric-looking columns stored as text (`object` dtype)	Converted to proper `float64`/`int64` types
Note: every fix replaces the messy column with its clean version — the output has no duplicate "raw vs. clean" columns for the same field. Full before/after visuals for each stage are in `FIFA21_EDA_Before_After_11_Stages.pdf`.
---
🛠️ Tools Used
Task	Tool
Initial inspection, spot-checks, sort/filter review	Excel
Encoding fixes, currency/unit parsing, deduplication, dtype conversion	Python (pandas, regex)
Formula-based proof of concept (same 11 fixes, native Excel functions)	Excel (`SUBSTITUTE`, `VALUE`, `LEFT/MID/FIND`, `COUNTIF`)
Before/after visuals	Python (matplotlib)
Python 3.11, pandas 2.x, numpy, matplotlib, openpyxl
---
▶️ How to Run
```bash
pip install pandas numpy openpyxl
python fifa21_cleaning.py
```
This reads the raw `.xlsx` file, applies all 11 fixes, and writes a cleaned Excel file with no duplicate columns.
---
🔍 Key Insights
100% of currency and physical-measurement fields were unusable text before cleaning.
Encoding corruption affected 7 of 77 columns (~10%).
Only 1 exact duplicate existed across 18,979 rows.
`Loan Date End` was populated in only 5.3% of records — better modeled as a boolean flag than a date.
The oldest player (age 53) was verified as a legitimate legend-tier record, not a data error.
---
📎 Links
Dataset: Kaggle — FIFA 21 Messy, Raw Dataset For Cleaning/Exploring
Notebook/repo: [Insert your GitHub repo link here]
---
👤 Author
[Your Name] — Data Analyst
