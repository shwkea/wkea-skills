import os
import sys
import json
import pandas as pd

# Windows PowerShell GBK 编码修复
sys.stdout.reconfigure(encoding='utf-8')

def read_excel(xlsx_path, sheet_name='询价格式'):
    """从Excel询价单读取产品列表

    读取规则（关键）：
    - 从第8行开始（Row 7 是表头：序号、品牌、产品...)
    - 有效行判断：有"序号"列有值 或 有"产品名称"列有值
    - 品牌可以为空（如序号13、28的情况），产品名称不能为空
    - 跳过序号为空且产品也为空的所有行
    - 跳过备注行、税率说明行等非产品数据
    """
    
    if not os.path.exists(xlsx_path):
        return {"status": "error", "message": f"文件不存在: {xlsx_path}"}
    
    try:
        xlsx = pd.ExcelFile(xlsx_path)
        df = pd.read_excel(xlsx, sheet_name=sheet_name, header=None)
    except Exception as e:
        return {"status": "error", "message": f"读取Excel失败: {str(e)}"}
    
    products = []
    errors = []
    
    for i in range(8, len(df)):  # 从第8行开始（索引7）
        row = df.iloc[i]
        seq = row[0]  # 序号
        brand = row[1]  # 品牌
        product = row[2]  # 产品名称
        spec = row[3] if pd.notna(row[3]) else ''  # 规格
        qty = row[4] if pd.notna(row[4]) else 0  # 数量
        unit = row[5] if pd.notna(row[5]) else ''  # 单位
        note = row[11] if pd.notna(row[11]) else ''  # 备注
        requester = row[12] if pd.notna(row[12]) else ''  # 申请人
        
        # 跳过空行
        if pd.isna(seq) and pd.isna(product):
            continue
        
        # 跳过非产品行（备注、税率说明等）
        if pd.notna(seq):
            seq_str = str(seq).strip()
            if '备注' in seq_str or '税率' in seq_str or '当国家' in seq_str:
                continue
        
        # 处理序号
        actual_seq = None
        if pd.notna(seq):
            try:
                actual_seq = int(float(seq))
            except:
                # 如果序号无法转为数字，可能是备注行
                continue
        
        # 产品名称必须存在
        if pd.isna(product):
            errors.append(f"Row {i+1}: 序号{actual_seq}缺少产品名称")
            continue
        
        # 品牌可为空
        actual_brand = ''
        if pd.notna(brand):
            actual_brand = str(brand).strip().replace('\n', '')
        
        # 数量处理
        actual_qty = 0
        if pd.notna(qty):
            try:
                actual_qty = int(float(qty))
            except:
                pass
        
        products.append({
            "seq": actual_seq,
            "brand": actual_brand,
            "product": str(product).strip(),
            "spec": str(spec).strip() if spec else '',
            "qty": actual_qty,
            "unit": str(unit).strip() if unit else '',
            "note": str(note).strip() if note else '',
            "requester": str(requester).strip() if requester else ''
        })
    
    result = {
        "status": "success",
        "xlsx_path": xlsx_path,
        "sheet_name": sheet_name,
        "total_rows": len(df),
        "product_count": len(products),
        "errors": errors,
        "products": products
    }
    
    return result

def save_products_json(products, output_path):
    """保存产品列表到JSON文件"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"products": products}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python read_excel.py <Excel文件路径> [输出JSON路径]")
        print("示例: python read_excel.py 2604179085-6.xlsx products.json")
        sys.exit(1)
    
    xlsx_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = read_excel(xlsx_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 如果指定了输出路径，保存JSON
    if output_path:
        if result["status"] == "success":
            save_products_json(result["products"], output_path)
            print(f"\n已保存到: {output_path}")
        else:
            print(f"\n保存失败: {result['message']}")
