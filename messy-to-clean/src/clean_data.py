"""Clean a CSV dataset without changing the original file.

Run from anywhere:
    python messy-to-clean/src/clean_data.py --demo
    python messy-to-clean/src/clean_data.py --input path/to/file.csv

Install dependency:
    python -m pip install pandas
"""

from pathlib import Path
import argparse
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of a dataset."""
    result = df.copy()

    # Make column names consistent and readable.
    result.columns = [
        str(name).strip().lower().replace(" ", "_")
        for name in result.columns
    ]

    # Trim whitespace and convert empty strings to missing values.
    for column in result.select_dtypes(include=["object", "string"]).columns:
        result[column] = result[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )
        result[column] = result[column].replace("", pd.NA)

    # Remove duplicate rows, keeping the first occurrence.
    result = result.drop_duplicates().reset_index(drop=True)

    # Fill missing text with "Unknown" and numeric values with the median.
    for column in result.columns:
        if pd.api.types.is_numeric_dtype(result[column]):
            median = result[column].median()
            if pd.notna(median):
                result[column] = result[column].fillna(median)
        else:
            result[column] = result[column].fillna("Unknown")

    return result


def demo_dataframe() -> pd.DataFrame:
    """Make sample data in memory; do not store it in raw/."""
    return pd.DataFrame(
        {
            " Student Name ": [" Alice ", "Bob", " Alice ", "Cara", ""],
            " Age ": [20, 22, 20, None, 21],
            " City ": [" Taipei ", "", " Taipei ", "Taichung", None],
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean a CSV dataset.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--demo", action="store_true", help="Use sample data.")
    source.add_argument("--input", type=Path, help="Path to an existing CSV file.")
    args = parser.parse_args()

    if args.demo:
        original = demo_dataframe()
        filename = "demo_cleaned.csv"
    else:
        input_path = args.input.expanduser().resolve()
        if not input_path.is_file():
            parser.error(f"Input file not found: {input_path}")
        if input_path.suffix.lower() != ".csv":
            parser.error("Input must be a CSV file.")
        original = pd.read_csv(input_path)
        filename = input_path.stem + "_cleaned.csv"

    cleaned = clean_dataframe(original)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / filename
    if output_path.exists():
        parser.error(f"Output already exists; will not overwrite: {output_path}")
    cleaned.to_csv(output_path, index=False)

    print(f"Original rows: {len(original)}")
    print(f"Cleaned rows:  {len(cleaned)}")
    print(f"Saved to: {output_path}")
    print("\nCleaned preview:")
    print(cleaned.to_string(index=False))


if __name__ == "__main__":
    main()
