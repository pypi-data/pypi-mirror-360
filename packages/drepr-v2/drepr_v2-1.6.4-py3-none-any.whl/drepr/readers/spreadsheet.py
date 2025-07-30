from __future__ import annotations

from pathlib import Path

import openpyxl


class RASpreadsheet:

    def __init__(self, workbook: openpyxl.Workbook):
        self.workbook = workbook

    def __getitem__(self, name: str):
        return self.workbook[name]


def read_source_spreadsheet(infile: Path | str):
    wb = openpyxl.load_workbook(infile)
    return RASpreadsheet(wb)
