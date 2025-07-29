import json
import csv
import os

def export_to_txt(entry, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Item Name: {entry['name']}\n\n")
        f.write("Full Card:\n")
        f.write(f"Name:         {entry['name']}\n")
        f.write(f"Item Type:    {entry['type']}\n")
        f.write(f"Introduced:   {entry['introduced']}\n")
        f.write(f"Weight:       {entry['weight_kg']} kg\n")
        f.write(f"Dimensions:   {entry['dimensions']}\n")

def export_to_json(entry, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False, indent=4)

def export_to_csv(entry, filepath):
    file_exists = os.path.exists(filepath)
    with open(filepath, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=entry.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)

def export_entry(entry, filepath, format="txt"):
    format = format.lower()
    if format == "txt":
        export_to_txt(entry, filepath)
    elif format == "json":
        export_to_json(entry, filepath)
    elif format == "csv":
        export_to_csv(entry, filepath)
    else:
        raise ValueError(f"Unsupported format: {format}")
