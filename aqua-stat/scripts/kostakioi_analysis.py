import sys
import pandas as pd
import numpy as np
from pathlib import Path

# ===== ΔΙΑΔΡΟΜΕΣ ΑΡΧΕΙΩΝ (Paths) =====
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = PROJECT_ROOT / 'data' / 'KOSTAKIOI'
OUTPUT_DIR = PROJECT_ROOT / 'stats'

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
file_path = BASE_DIR / 'KOSTAKIOI 1.xlsx'

print(f"🔍 Αναζήτηση αρχείου σε: {file_path}")

if not file_path.exists():
    print("❌ ΣΦΑΛΜΑ: Το αρχείο δεν βρέθηκε. Η διαδικασία διακόπηκε.")
    sys.exit(1)

print("✅ Το αρχείο βρέθηκε. Έναρξη επεξεργασίας...")

# ===== ΦΟΡΤΩΣΗ ΚΑΙ ΚΑΘΑΡΙΣΜΟΣ ΔΕΔΟΜΕΝΩΝ =====
try:
    df = pd.read_excel(file_path, usecols=[0, 1, 2, 3])
except Exception as e:
    print(f"❌ ΣΦΑΛΜΑ κατά την ανάγνωση του Excel: {e}")
    sys.exit(1)

# Εσωτερική ονομασία στηλών στα αγγλικά για ευκολία
df.columns = ["date", "aqueduct", "drilling", "output"]

# Μετατροπή ημερομηνίας και διαγραφή κενών γραμμών
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"]).copy()
df = df.sort_values(by="date").reset_index(drop=True)

# Μετατροπή σε αριθμούς και αντικατάσταση κενών με 0
for col in ["aqueduct", "drilling", "output"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# ===== ΗΜΕΡΗΣΙΟΙ ΥΠΟΛΟΓΙΣΜΟΙ =====
df["input_total"] = df["aqueduct"] + df["drilling"]
df["diff"] = df["input_total"] - df["output"]

# Ποσοστό διαφοράς με προστασία διαίρεσης με το 0
df["diff_pct"] = np.where(
    df["input_total"] > 0, 
    (df["diff"] / df["input_total"]) * 100, 
    0
).round(2)

# Βοηθητική στήλη μήνα (χρησιμοποιεί το datetime πριν αφαιρέσουμε την ώρα)
df["month"] = df["date"].dt.strftime("%Y-%m")
df["year"] = df["date"].dt.strftime("%Y")

# ΑΦΑΙΡΕΣΗ ΤΗΣ ΩΡΑΣ: Κρατάμε ΜΟΝΟ την ημερομηνία για το Excel
df["date"] = df["date"].dt.date

# ===== ΜΗΝΙΑΙΑ ΣΥΝΟΛΑ =====
monthly = df.groupby("month")[["aqueduct", "drilling", "output", "input_total", "diff"]].sum()

monthly["diff_pct"] = np.where(
    monthly["input_total"] > 0, 
    (monthly["diff"] / monthly["input_total"]) * 100, 
    0
).round(2)

monthly = monthly.reset_index()

# ===== ΕΤΗΣΙΑ ΣΥΝΟΛΑ =====
yearly = df.groupby("year")[["aqueduct", "drilling", "output", "input_total", "diff"]].sum()

yearly["diff_pct"] = np.where(
    yearly["input_total"] > 0, 
    (yearly["diff"] / yearly["input_total"]) * 100, 
    0
).round(2)

yearly = yearly.reset_index()

# ===== ΑΝΩΜΑΛΙΕΣ (Anomalies) =====
std_dev = df["diff"].std() if not pd.isna(df["diff"].std()) else 0
threshold = df["diff"].mean() + (2 * std_dev)

anomalies = df[df["diff"] > threshold].copy()

# ===== ΣΥΝΟΠΤΙΚΗ ΑΝΑΦΟΡΑ (Summary) =====
summary = pd.DataFrame({
    "ΜΕΤΡΗΣΗ": [
        "Συνολική Είσοδος Νερού (Όγκος)",
        "Συνολική Έξοδος Νερού (Όγκος)",
        "Συνολική Διαφορά (Όγκος)",
        "Μέση Ημερήσια Διαφορά",
        "Μέγιστη Ημερήσια Διαφορά (Χειρότερη Μέρα)",
        "Συνολικό Ποσοστό Διαφοράς (%)"
    ],
    "ΤΙΜΗ": [
        df["input_total"].sum().round(2),
        df["output"].sum().round(2),
        df["diff"].sum().round(2),
        df["diff"].mean().round(2),
        df["diff"].max().round(2),
        (df["diff"].sum() / df["input_total"].sum() * 100).round(2) if df["input_total"].sum() > 0 else 0
    ]
})

# ===== ΕΞΑΓΩΓΗ ΣΕ JSON ΓΙΑ ΤΟ FRONTEND =====
import json

json_df = df.copy()
json_df["date"] = json_df["date"].astype(str)
json_monthly = monthly.copy()
json_yearly = yearly.copy()
json_anomalies = anomalies.copy()
json_anomalies["date"] = json_anomalies["date"].astype(str)

# ===== ΕΞΑΓΩΓΗ ΜΟΤΙΒΩΝ (PATTERNS) =====
# 1. Μήνας Αιχμής Κατανάλωσης
highest_consumption_month_row = monthly.loc[monthly["output"].idxmax()] if not monthly.empty else None
highest_consumption_month = highest_consumption_month_row["month"] if highest_consumption_month_row is not None else ""
highest_consumption_val = highest_consumption_month_row["output"] if highest_consumption_month_row is not None else 0

# 2. Μήνας Υψηλότερης Διαφοράς Όγκου
highest_diff_month_row = monthly.loc[monthly["diff"].idxmax()] if not monthly.empty else None
highest_diff_month = highest_diff_month_row["month"] if highest_diff_month_row is not None else ""
highest_diff_val = highest_diff_month_row["diff"] if highest_diff_month_row is not None else 0

# 3. Κύρια Πηγή Τροφοδοσίας
total_aqueduct = df["aqueduct"].sum()
total_drilling = df["drilling"].sum()
total_input = df["input_total"].sum()

if total_input > 0:
    aqueduct_pct = (total_aqueduct / total_input) * 100
    drilling_pct = (total_drilling / total_input) * 100
    if aqueduct_pct > drilling_pct:
        primary_source_name = "Υδραγωγείο"
        primary_source_pct = aqueduct_pct
    else:
        primary_source_name = "Γεώτρηση"
        primary_source_pct = drilling_pct
else:
    primary_source_name = "Άγνωστο"
    primary_source_pct = 0.0

# 4. Ημέρες Αδειάσματος και Γεμίσματος
negative_diff_days = len(df[df["diff"] < 0])
positive_diff_days = len(df[df["diff"] > 0])
total_days = len(df)
negative_diff_pct = (negative_diff_days / total_days) * 100 if total_days > 0 else 0
positive_diff_pct = (positive_diff_days / total_days) * 100 if total_days > 0 else 0

patterns_data = {
    "highest_consumption_month": {"month": str(highest_consumption_month), "value": float(highest_consumption_val)},
    "highest_diff_month": {"month": str(highest_diff_month), "value": float(highest_diff_val)},
    "primary_source": {"name": primary_source_name, "percentage": float(primary_source_pct)},
    "tank_draw": {"days": int(negative_diff_days), "percentage": float(negative_diff_pct)},
    "tank_fill": {"days": int(positive_diff_days), "percentage": float(positive_diff_pct)}
}

json_data = {
    "daily_data": json_df.to_dict(orient="records"),
    "monthly_totals": json_monthly.to_dict(orient="records"),
    "yearly_totals": json_yearly.to_dict(orient="records"),
    "anomalies": json_anomalies.to_dict(orient="records"),
    "patterns": patterns_data,
    "summary": {
        "total_input": float(df["input_total"].sum()),
        "total_output": float(df["output"].sum()),
        "total_diff": float(df["diff"].sum()),
        "avg_daily_diff": float(df["diff"].mean()),
        "max_daily_diff": float(df["diff"].max()),
        "diff_pct": float((df["diff"].sum() / df["input_total"].sum() * 100)) if df["input_total"].sum() > 0 else 0.0
    }
}

json_output_file = OUTPUT_DIR / 'kostakioi_data.json'
with open(json_output_file, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)

print(f"💾 Αποθηκεύτηκε JSON δεδομένων: {json_output_file}")

# ===== ΜΕΤΑΦΡΑΣΗ ΣΤΗΛΩΝ ΣΤΑ ΕΛΛΗΝΙΚΑ =====
df = df.drop(columns=["month"])
anomalies = anomalies.drop(columns=["month"])

greek_columns = {
    "date": "ΗΜΕΡΟΜΗΝΙΑ",
    "aqueduct": "ΑΠΟ ΥΔΡΑΓΩΓΕΙΟ",
    "drilling": "ΑΠΟ ΓΕΩΤΡΗΣΗ",
    "output": "ΕΞΟΔΟΣ",
    "input_total": "ΣΥΝΟΛΟ ΕΙΣΟΔΟΥ",
    "diff": "ΔΙΑΦΟΡΑ ΟΓΚΟΥ",
    "diff_pct": "ΠΟΣΟΣΤΟ ΔΙΑΦΟΡΑΣ (%)",
    "month": "ΜΗΝΑΣ"
}

df = df.rename(columns=greek_columns)
monthly = monthly.rename(columns=greek_columns)
anomalies = anomalies.rename(columns=greek_columns)

# ===== ΑΠΟΘΗΚΕΥΣΗ ΣΕ EXCEL =====
output_file = OUTPUT_DIR / 'kostakioi_analysis.xlsx'

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name="Ημερήσια Δεδομένα", index=False)
    monthly.to_excel(writer, sheet_name="Μηνιαία Σύνολα", index=False)
    anomalies.to_excel(writer, sheet_name="Ανωμαλίες", index=False)
    summary.to_excel(writer, sheet_name="Συνοπτική Αναφορά", index=False)

print(f"\n📊 Η ανάλυση ολοκληρώθηκε!")
print(f"💾 Αποθηκεύτηκε επιτυχώς στο: {output_file}")