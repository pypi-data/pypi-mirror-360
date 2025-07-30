# mlslib/evaluation_utils.py

import pandas as pd
import numpy as np
import json
import os

def calculate_mrr(
    df: pd.DataFrame,
    position_col: str,
    label_col: str,
    group_by_cols: list[str] = None
) -> dict:
    """
    Calculates Mean Reciprocal Rank (MRR) overall and for specified segments.

    This function identifies relevant items (where label_col == 1), calculates their
    reciprocal rank based on the position_col, and then computes the mean for the
    entire dataset and for each group in group_by_cols.

    Args:
        df (pd.DataFrame): The input DataFrame containing predictions, labels, and segment columns.
        position_col (str): The name of the column containing the item's rank (0-indexed).
        label_col (str): The name of the column indicating the relevant item (e.g., where value is 1).
        group_by_cols (list[str], optional): A list of column names to group by for
                                             detailed MRR breakdowns. Defaults to None.

    Returns:
        dict: A dictionary containing the overall MRR and nested dictionaries for each breakdown.
              Example: {'overall_mrr': 0.5, 'mrr_by_store_id': {1: 0.6, 2: 0.4}}
    """
    if group_by_cols is None:
        group_by_cols = []

    # Identify the positively labeled items
    relevant_items = df[df[label_col] == 1].copy()

    if relevant_items.empty:
        print(f"Warning: No relevant items found with '{label_col} == 1'. Cannot calculate MRR.")
        results = {'overall_mrr': np.nan}
        for col in group_by_cols:
            results[f'mrr_by_{col}'] = {}
        return results

    # Calculate Reciprocal Rank (assuming position is 0-indexed)
    relevant_items['rr'] = 1 / (1 + relevant_items[position_col])

    # --- Calculate MRR Metrics ---
    results = {'overall_mrr': relevant_items['rr'].mean()}

    # Calculate breakdown MRRs
    for col in group_by_cols:
        if col in relevant_items.columns:
            mrr_by_col = relevant_items.groupby(col)['rr'].mean().to_dict()
            results[f'mrr_by_{col}'] = mrr_by_col
        else:
            print(f"Warning: Breakdown column '{col}' not found in DataFrame. Skipping.")
            results[f'mrr_by_{col}'] = {}

    return results


def save_metrics_to_json(metrics: dict, output_path: str):
    """
    Saves a dictionary of metrics to a JSON file, handling numpy types.

    Args:
        metrics (dict): The dictionary containing metrics data.
        output_path (str): The full path where the JSON file will be saved.
    """
    def convert_numpy_types(obj):
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj) if not np.isnan(obj) else None
        if isinstance(obj, np.ndarray): return obj.tolist()
        if isinstance(obj, dict): return {k: convert_numpy_types(v) for k, v in obj.items()}
        if isinstance(obj, list): return [convert_numpy_types(i) for i in obj]
        return obj

    serializable_metrics = convert_numpy_types(metrics)

    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(serializable_metrics, f, indent=4)
        print(f"Metrics successfully saved to: {output_path}")
    except (IOError, TypeError) as e:
        print(f"Error: Could not write or serialize metrics to {output_path}. Reason: {e}")


def display_mrr_comparison(
    results_list: list[dict],
    model_col: str = "Model",
    test_set_col: str = "Test Set"
):
    """
    Displays formatted comparison tables for a list of MRR evaluation results.

    Args:
        results_list (list[dict]): A list of dictionaries, where each dictionary
                                   represents the evaluation results for one run.
        model_col (str): The key in the dictionaries that identifies the model.
        test_set_col (str): The key in the dictionaries that identifies the test set.
    """
    if not results_list:
        print("No evaluation results were provided to display.")
        return

    results_df = pd.DataFrame(results_list)

    # --- 1. Overall MRR Summary Table ---
    print("\n\n" + "="*80)
    print(" " * 25 + "OVERALL MRR COMPARISON")
    print("="*80)

    try:
        summary_table = results_df.pivot_table(
            index=test_set_col,
            columns=model_col,
            values="overall_mrr"
        )
        print(summary_table.to_string(float_format="%.4f"))
    except Exception as e:
        print(f"Could not generate pivot table summary. Error: {e}")
        print("Raw overall MRR scores:")
        print(results_df[[test_set_col, model_col, 'overall_mrr']])

    print("="*80)

    # --- 2. Detailed Breakdown by Segment ---
    print("\n\n" + "="*80)
    print(" " * 24 + "DETAILED MRR BREAKDOWN BY SEGMENT")
    print("="*80)

    for _, row in results_df.iterrows():
        print(f"\n--- Model: {row[model_col]} | Test Set: {row[test_set_col]} ---")
        for key, value in row.items():
            if isinstance(value, dict):
                print(f"\n  MRR by {key.replace('mrr_by_', '')}:")
                if value:
                    for segment, mrr in sorted(value.items()):
                        print(f"    - {segment}: {mrr:.4f}")
                else:
                    print("    No data available.")
    print("="*80)