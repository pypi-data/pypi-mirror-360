# release_consistency_checker/utils.py

from typing import Dict, List, Any, Optional, Tuple, Set
import pandas as pd
import numpy as np
from pathlib import Path
from ... import common as cu


# Define dataset-specific parameters
DATASETS: List[Dict[str, Any]] = [
    {
        "dataset_name": "Clinical",
        "r5_filename": "HD Release 5 Clinical.csv",
        "r6_filename": "HD Release 6 Clinical_FINAL.csv",
        "add_to_dict": {},  # No known changes yet
        "missing_values": ["-9999", "-8888"],
        "initial_drop_cols": ["Age"],
        "debug": False  # Set to True if needed
    },
    {
        "dataset_name": "Genomics",
        "r5_filename": "HD Release 5 Genomics.csv",
        "r6_filename": "HD Release 6 Genomics_FINAL.csv",
        "add_to_dict": {},
        "missing_values": ["NaT", "NULL"],
        "initial_drop_cols": ["Age"],
        "debug": False  # Set to True if needed
    },
    {
        "dataset_name": "Imaging",
        "r5_filename": "HD Release 5 Imaging.csv",
        "r6_filename": "HD Release 6 Imaging_FINAL.csv",
        "add_to_dict": {},
        "missing_values": ["NaT", "NULL"],
        "initial_drop_cols": ["Age", "ID_Gender", "ID_Education"],
        "debug": False  # Set to True if needed
    },
    {
        "dataset_name": "Biomarkers",
        "r5_filename": "HD Release 5 Biomarkers.csv",
        "r6_filename": "HD Release 6 Biomarkers_FINAL.csv",
        "add_to_dict": {},
        "missing_values": ["-9999", "-8888"],
        "initial_drop_cols": ["Age"],
        "debug": False  # Set to True if needed
    }
]

# Optional constants for clarity
RELEASE_1 = 1
RELEASE_2 = 2


def compare_datasets(
    df_old: pd.DataFrame,
    df_new: pd.DataFrame,
    dataset_name: str,
    output_path: Path
) -> None:
    """
    Compare row-level values and identify changes.
    
    Args:
        df_old: DataFrame from older release
        df_new: DataFrame from newer release
        dataset_name: Name of the dataset being compared
        output_path: Directory to save comparison results
    """
    df_old["Release"] = RELEASE_1
    df_new["Release"] = RELEASE_2

    combined = pd.concat([df_old, df_new], ignore_index=True).copy()
    combined = combined.groupby(["Med_ID", "Visit_ID", "Release"]).agg(lambda x: list(x)).reset_index()

    pivoted = combined.pivot(index=["Med_ID", "Visit_ID"], columns="Release")
    diffs = pivoted.xs(RELEASE_1, level="Release", axis=1) != pivoted.xs(RELEASE_2, level="Release", axis=1)
    changed_rows = pivoted[diffs.any(axis=1)]

    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / f"{dataset_name}_changed_rows.csv"
    changed_rows.to_csv(output_file)

    cu.log_and_print(f"🔍 {dataset_name}: {changed_rows.shape[0]} rows with changes saved to {output_file}")


def compare_datasets_filtered(
    df_old: pd.DataFrame,
    df_new: pd.DataFrame,
    dataset_name: str,
    output_path: Path
) -> None:
    """
    Compare datasets, excluding participants unique to one release.
    
    Args:
        df_old: DataFrame from older release
        df_new: DataFrame from newer release
        dataset_name: Name of the dataset being compared
        output_path: Directory to save comparison results
    """

    # 🛡️ Drop any existing "Release" columns before setting
    df_old = df_old.drop(columns=["Release"], errors="ignore")
    df_new = df_new.drop(columns=["Release"], errors="ignore")

    df_old["Release"] = RELEASE_1
    df_new["Release"] = RELEASE_2

    combined = pd.concat([df_old, df_new], ignore_index=True)

    # ✅ DO NOT groupby + apply — it's making things messy
    # Just pivot directly
    pivoted = combined.pivot_table(
        index=["Med_ID", "Visit_ID"], 
        columns="Release",
        aggfunc="first"
    )

    # ✅ Flatten multi-index columns
    pivoted.columns = [f"{col}_{release}" for col, release in pivoted.columns]

    # ✅ Now identify changes properly
    col_pairs = [(col.replace(f"_{RELEASE_1}", ""), col.replace(f"_{RELEASE_2}", "")) 
                 for col in pivoted.columns if f"_{RELEASE_1}" in col]

    changed_rows = []

    for col_base, _ in col_pairs:
        col_r1 = f"{col_base}_{RELEASE_1}"
        col_r2 = f"{col_base}_{RELEASE_2}"

        if col_r1 in pivoted.columns and col_r2 in pivoted.columns:
            # Compare non-missing and unequal
            mask = (pivoted[col_r1] != pivoted[col_r2]) & ~(pivoted[col_r1].isna() & pivoted[col_r2].isna())
            changed_rows.append(mask)

    if changed_rows:
        full_mask = changed_rows[0]
        for mask in changed_rows[1:]:
            full_mask |= mask
        filtered_rows = pivoted[full_mask]
    else:
        filtered_rows = pivoted.iloc[[]]  # empty DataFrame

    # ✅ Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    # ✅ Save filtered rows
    output_file = output_path / f"{dataset_name}_filtered_rows.csv"
    filtered_rows.to_csv(output_file)

    cu.log_and_print(f"🔍 {dataset_name}: {filtered_rows.shape[0]} filtered rows with true changes saved to {output_file}")


def align_dtypes(
    df_old: pd.DataFrame,
    df_new: pd.DataFrame,
    dataset_name: str,
    missing_values: List[str]
) -> None:
    """
    Align dtypes of old dataset to match new dataset for shared columns.
    
    Args:
        df_old: DataFrame from older release
        df_new: DataFrame from newer release
        dataset_name: Name of the dataset being compared
        missing_values: List of values to treat as missing/NA
    """
    common_cols = set(df_old.columns).intersection(set(df_new.columns))

    mismatches = {
        col: (df_old[col].dtype, df_new[col].dtype)
        for col in common_cols if df_old[col].dtype != df_new[col].dtype
    }

    if mismatches:
        cu.log_and_print(f"\n🔍 Fixing dtype mismatches in {dataset_name}:")
        for col, (dtype_old, dtype_new) in mismatches.items():
            cu.log_and_print(f"🔄 Converting {col}: {dtype_old} → {dtype_new}")
            try:
                df_old[col] = df_old[col].replace(missing_values, np.nan)
                df_old[col] = df_old[col].astype(dtype_new)
            except Exception as e:
                cu.log_and_print(f"⚠️ Could not convert {col}: {e}")
        cu.log_and_print(f"✅ Dtype alignment complete.")
    else:
        cu.log_and_print(f"\n✅ No dtype mismatches found in {dataset_name}.")


def analyze_column_changes(
    only_in_old: Set[str],
    only_in_new: Set[str],
    data_dir: str = "."
) -> Tuple[Dict[str, str], List[str], List[str], Set[str], Set[str]]:
    """
    Analyze variable rename/add/remove via mapping file.
    
    Args:
        only_in_old: Set of column names only in old dataset
        only_in_new: Set of column names only in new dataset
        data_dir: Directory containing the mapping file
        
    Returns:
        Tuple containing:
        - Dictionary of renamed columns (old_name -> new_name)
        - List of removed columns
        - List of added columns
        - Set of unaccounted old columns
        - Set of unaccounted new columns
    """
    map_path = Path().resolve().parent / "domains" / "RP_Variable Updates_Release.xlsx"

    # Always print the attempted map path
    cu.log_and_print(f"🗺️ Using mapping file: {map_path}")

    if not map_path.exists():
        raise FileNotFoundError(f"❌ Mapping file not found: {map_path}")

    mapping_df = pd.read_excel(map_path)
    required_cols = {"Old Variable Name", "Variable", "Type"}
    if not required_cols.issubset(mapping_df.columns):
        raise ValueError(f"Mapping file must contain: {required_cols}")

    rename_dict, removed, added = {}, [], []

    for _, row in mapping_df.iterrows():
        old, new, change_type = row["Old Variable Name"], row["Variable"], row["Type"]
        if change_type == "Changed" and old in only_in_old and new in only_in_new:
            rename_dict[old] = new
        elif change_type == "Removed" and old in only_in_old:
            removed.append(old)
        elif change_type == "Added" and new in only_in_new:
            added.append(new)

    accounted_old = set(rename_dict.keys()) | set(removed)
    accounted_new = set(rename_dict.values()) | set(added)

    unaccounted_old = only_in_old - accounted_old
    unaccounted_new = only_in_new - accounted_new

    cu.log_and_print("\n🔍 Column Changes Analysis")
    cu.log_and_print("\n🔄 Renamed Columns:")
    [cu.log_and_print(f"   🔄 {k} → {v}") for k, v in rename_dict.items()] or cu.log_and_print("   ✅ None")

    cu.log_and_print("\n❌ Removed Columns:")
    [cu.log_and_print(f"   ❌ {col}") for col in removed] or cu.log_and_print("   ✅ None")

    cu.log_and_print("\n✅ Added Columns:")
    [cu.log_and_print(f"   ✅ {col}") for col in added] or cu.log_and_print("   ✅ None")

    cu.log_and_print(f"\n⚠️ Unaccounted Old Columns ({len(unaccounted_old)}): {unaccounted_old or '✅ All accounted for.'}")
    cu.log_and_print(f"⚠️ Unaccounted New Columns ({len(unaccounted_new)}): {unaccounted_new or '✅ All accounted for.'}")

    return rename_dict, removed, added, unaccounted_old, unaccounted_new


def monitor_changes(
    dataset_name: str,
    r5_filename: str,
    r6_filename: str,
    data_dir: str = ".",
    add_to_dict: Optional[Dict[str, Any]] = None,
    missing_values: Optional[List[str]] = None,
    initial_drop_cols: Optional[List[str]] = None,
    debug: bool = False,
    mode: str = "old_only"
) -> None:
    """
    Monitor and analyze changes between two dataset releases.
    
    Args:
        dataset_name: Name of the dataset being compared
        r5_filename: Filename of R5 (old) dataset
        r6_filename: Filename of R6 (new) dataset
        data_dir: Directory containing the datasets
        add_to_dict: Additional configuration options
        missing_values: List of values to treat as missing
        initial_drop_cols: Columns to drop before comparison
        debug: Enable debug mode for more detailed output
        mode: Comparison mode ('old_only' or 'standard')
    """
    cu.log_and_print(f"\n🔍 Monitoring changes for {dataset_name}...")
    cu.log_and_print(f"📂 Data Directory: {data_dir}")
    cu.log_and_print(f"📄 R5 File: {r5_filename}")
    cu.log_and_print(f"📄 R6 File: {r6_filename}")
    cu.log_and_print(f"🔄 Mode: {mode}")
    df_old, df_new = cu.load_datasets(r5_filename, r6_filename, data_dir, mode=mode)

    if df_old is None or df_new is None:
        cu.log_and_print(f"⚠️ Skipping {dataset_name} due to loading failure.\n")
        return

    # Use the compare_dataframes function which handles all comparisons
    comparison_result = cu.compare_dataframes(df_old, df_new, dataset_name=dataset_name)
    
    # Extract results from the comparison
    only_in_old = comparison_result.only_in_first
    only_in_new = comparison_result.only_in_second
    
    rename_dict, removed, added, unaccounted_old, unaccounted_new = analyze_column_changes(only_in_old, only_in_new, data_dir)

    if add_to_dict:
        rename_dict.update(add_to_dict)

    df_old.rename(columns=rename_dict, inplace=True)

    columns_to_drop = (initial_drop_cols or []) + removed + added + list(unaccounted_old) + list(unaccounted_new)
    df_old.drop(columns=columns_to_drop, errors="ignore", inplace=True)
    df_new.drop(columns=columns_to_drop, errors="ignore", inplace=True)

    # Compare again after adjustments if in debug mode
    if debug:
        debug_comparison = cu.compare_dataframes(
            df_old, 
            df_new, 
            dataset_name=f"{dataset_name} (Post-Adjustments)",
            steps=["columns", "dtypes"]
        )

    # Get paths for output
    if dataset_name == "Manual_Run":
        qc_output_path = Path("output")  # Or make it configurable
    else:
        domain_paths = cu.get_domain_paths(cu.get_project_root())
        qc_output_path = domain_paths[dataset_name]["qc_output"]
        
    cu.log_and_print(f"📁 Output path for {dataset_name}: {qc_output_path}")

    compare_datasets(df_old, df_new, dataset_name, qc_output_path)
    compare_datasets_filtered(df_old, df_new, dataset_name, qc_output_path)