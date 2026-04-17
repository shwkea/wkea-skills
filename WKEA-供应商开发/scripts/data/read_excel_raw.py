#!/usr/bin/env python3
"""
Excel原始数据提取脚本
只提取表格内容为原始文本，不做解析判断
由AI根据原始数据进行结构化分析
"""

import sys
import json
import pandas as pd
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def read_excel_raw(xlsx_path: str) -> dict:
    """提取Excel所有sheet的原始文本数据"""
    
    xlsx_path = Path(xlsx_path)
    if not xlsx_path.exists():
        return {
            "status": "error",
            "error": f"文件不存在: {xlsx_path}",
            "xlsx_path": str(xlsx_path)
        }
    
    xlsx = pd.ExcelFile(xlsx_path)
    sheets = {}
    
    for sheet_name in xlsx.sheet_names:
        df = pd.read_excel(xlsx, sheet_name=sheet_name, header=None)
        
        rows = []
        for idx, row in df.iterrows():
            # 提取每行所有非空单元格
            cells = []
            for col_idx, cell in enumerate(row):
                if pd.notna(cell):
                    cell_str = str(cell).strip()
                    if cell_str:
                        cells.append({
                            "row": idx,
                            "col": col_idx,
                            "value": cell_str
                        })
            
            if cells:  # 只保留有内容的行
                rows.append({
                    "row_index": idx,
                    "cells": cells
                })
        
        sheets[sheet_name] = {
            "total_rows": len(df),
            "total_cells": sum(len(r["cells"]) for r in rows),
            "content_rows": len(rows),
            "rows": rows
        }
    
    return {
        "status": "success",
        "xlsx_path": str(xlsx_path),
        "sheet_names": xlsx.sheet_names,
        "sheets": sheets
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "status": "error", 
            "error": "用法: python read_excel_raw.py <xlsx文件路径>"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    result = read_excel_raw(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
