"""
Raw population data exporter.

Exports per-iteration population snapshots (positions + fitness for every
member) to CSV and/or Excel files.  CSV export uses only the stdlib ``csv``
module.  Excel export requires ``pandas`` and ``openpyxl`` (imported lazily
so CSV-only workflows have zero extra dependencies).
"""

import os
import csv
from typing import List, Dict


class RawDataExporter:
    """Export raw population data captured during optimization runs.

    Parameters
    ----------
    output_dir : str
        Base directory for output files.  Created automatically if missing.
    """

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    # ── helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _build_filename(algo_name: str, func_id: int,
                        dimension: int, run_number: int, ext: str) -> str:
        """Build canonical filename: RAO2_F5_10D_RUN01_raw_data.{ext}"""
        return (
            f"{algo_name.upper()}_F{func_id}_{dimension}D"
            f"_RUN{run_number:02d}_raw_data.{ext}"
        )

    @staticmethod
    def _flatten_iteration_data(
        iteration_data: List[Dict],
    ) -> List[Dict]:
        """Flatten list-of-snapshots into a flat list of row dicts.

        Each snapshot dict has keys: iteration, fes, population, fitness.
        Returns one dict per member per iteration with keys:
          Iteration, FES, Member_ID, X1, X2, ..., Xn, Fitness
        """
        rows: List[Dict] = []
        for snap in iteration_data:
            it = snap["iteration"]
            fes = snap["fes"]
            pop = snap["population"]
            fit = snap["fitness"]

            for member_id in range(len(pop)):
                row = {
                    "Iteration": it,
                    "FES": fes,
                    "Member_ID": member_id + 1,  # 1-indexed
                }
                for dim_idx in range(len(pop[member_id])):
                    row[f"X{dim_idx + 1}"] = pop[member_id][dim_idx]
                row["Fitness"] = fit[member_id]
                rows.append(row)

        return rows

    # ── CSV export (zero extra dependencies) ─────────────────────────

    def export_to_csv(
        self,
        iteration_data: List[Dict],
        algo_name: str,
        func_id: int,
        dimension: int,
        run_number: int,
    ) -> str:
        """Write raw population data to a CSV file.

        Returns
        -------
        str
            Absolute path of the created CSV file.
        """
        filename = self._build_filename(algo_name, func_id, dimension,
                                        run_number, "csv")
        output_path = os.path.join(self.output_dir, filename)

        rows = self._flatten_iteration_data(iteration_data)
        if not rows:
            return output_path

        header = list(rows[0].keys())

        try:
            with open(output_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=header)
                writer.writeheader()
                for row in rows:
                    # Format floats for readability
                    formatted = {}
                    for k, v in row.items():
                        if isinstance(v, float):
                            formatted[k] = f"{v:.10e}"
                        else:
                            formatted[k] = v
                    writer.writerow(formatted)
            print(f"Raw data CSV saved: {output_path}")
        except PermissionError:
            print(f"\n[WARNING] Permission denied: {output_path}. "
                  f"Is it open in Excel?")

        return output_path

    # ── Excel export (requires pandas + openpyxl) ────────────────────

    def export_to_excel(
        self,
        iteration_data: List[Dict],
        algo_name: str,
        func_id: int,
        dimension: int,
        run_number: int,
    ) -> str:
        """Write raw population data to an Excel file.

        Requires ``pandas`` and ``openpyxl``.  If either is missing,
        a warning is printed and the call is skipped gracefully.

        Returns
        -------
        str
            Absolute path of the created Excel file (or intended path
            if the write was skipped).
        """
        filename = self._build_filename(algo_name, func_id, dimension,
                                        run_number, "xlsx")
        output_path = os.path.join(self.output_dir, filename)

        try:
            import pandas as pd  # noqa: F811
        except ImportError:
            print("[WARNING] pandas not installed — skipping Excel export. "
                  "Install with: pip install pandas openpyxl")
            return output_path

        rows = self._flatten_iteration_data(iteration_data)
        if not rows:
            return output_path

        df = pd.DataFrame(rows)

        try:
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="population_data", index=False)

                # Auto-fit column widths
                worksheet = writer.sheets["population_data"]
                for col_cells in worksheet.columns:
                    col_letter = col_cells[0].column_letter
                    max_len = max(
                        len(str(cell.value)) if cell.value is not None else 0
                        for cell in col_cells
                    )
                    # Include header length
                    header_len = len(str(col_cells[0].value))
                    adjusted = min(max(max_len, header_len) + 2, 50)
                    worksheet.column_dimensions[col_letter].width = adjusted

            print(f"Raw data Excel saved: {output_path}")
        except PermissionError:
            print(f"\n[WARNING] Permission denied: {output_path}. "
                  f"Is it open in Excel?")
        except ImportError:
            print("[WARNING] openpyxl not installed — skipping Excel export. "
                  "Install with: pip install openpyxl")

        return output_path

    # ── Convenience dispatcher ───────────────────────────────────────

    def export(
        self,
        iteration_data: List[Dict],
        algo_name: str,
        func_id: int,
        dimension: int,
        run_number: int,
        fmt: str = "csv",
    ) -> None:
        """Export raw data in the specified format(s).

        Parameters
        ----------
        fmt : str
            ``'csv'``, ``'excel'``, or ``'both'``.
        """
        if fmt in ("csv", "both"):
            self.export_to_csv(iteration_data, algo_name, func_id,
                               dimension, run_number)
        if fmt in ("excel", "both"):
            self.export_to_excel(iteration_data, algo_name, func_id,
                                 dimension, run_number)
