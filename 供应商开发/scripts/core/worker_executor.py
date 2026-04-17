#!/usr/bin/env python3
"""
子代理执行器 - 单产品供应商开发
每个产品单独执行，避免超时和状态丢失
"""

import json
import os
import sys
import subprocess
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, SCRIPT_DIR)

def run_python(script_path, *args):
    """执行 Python 脚本"""
    cmd = ['python', script_path] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    return result.returncode, result.stdout, result.stderr

def init_product_folder(product_dir, skill_dir):
    """初始化产品文件夹"""
    script = os.path.join(skill_dir, 'scripts', 'core', 'init.py')
    rc, out, err = run_python(script, product_dir, '1')
    return rc == 0, out, err

def save_product(product_dir, product_data, skill_dir):
    """保存产品信息"""
    # 写入临时文件
    tmp_file = os.path.join(os.path.dirname(product_dir), '_tmp_product.json')
    with open(tmp_file, 'w', encoding='utf-8') as f:
        json.dump(product_data, f, ensure_ascii=False, indent=2)
    
    script = os.path.join(skill_dir, 'scripts', 'data', 'save_product.py')
    rc, out, err = run_python(script, product_dir, '--file', tmp_file)
    
    # 删除临时文件
    if os.path.exists(tmp_file):
        os.remove(tmp_file)
    
    return rc == 0, out, err

def save_supplier(product_dir, supplier_data, skill_dir):
    """保存供应商信息"""
    # 写入临时文件
    tmp_file = os.path.join(os.path.dirname(product_dir), f"_tmp_supplier_{datetime.now().strftime('%H%M%S')}.json")
    with open(tmp_file, 'w', encoding='utf-8') as f:
        json.dump(supplier_data, f, ensure_ascii=False, indent=2)
    
    script = os.path.join(skill_dir, 'scripts', 'data', 'save_supplier.py')
    rc, out, err = run_python(script, product_dir, '--file', tmp_file)
    
    return rc == 0, out, err

def collect_and_report(product_dir, skill_dir):
    """汇总并生成报告"""
    # 汇总供应商
    script1 = os.path.join(skill_dir, 'scripts', 'data', 'collect_suppliers.py')
    rc1, out1, err1 = run_python(script1, product_dir)
    
    # 生成HTML报告
    script2 = os.path.join(skill_dir, 'scripts', 'report', 'generate_html.py')
    rc2, out2, err2 = run_python(script2, product_dir)
    
    return {
        "collect": rc1 == 0,
        "report": rc2 == 0,
        "errors": [err1, err2]
    }

def update_batch_status(workspace_path, product_id, status, supplier_count=0):
    """更新 batch_plan.json 状态"""
    batch_path = os.path.join(workspace_path, 'batch_plan.json')
    if not os.path.exists(batch_path):
        return False
    
    with open(batch_path, 'r', encoding='utf-8') as f:
        batch = json.load(f)
    
    for p in batch['products']:
        if p['id'] == product_id:
            p['status'] = status
            p['supplier_count'] = supplier_count
            p['completed_at'] = datetime.now().isoformat()
            break
    
    with open(batch_path, 'w', encoding='utf-8') as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)
    
    return True

def execute_single_product(product_info, workspace_path, skill_dir):
    """执行单个产品的供应商开发"""
    
    product_id = product_info['id']
    product_name = product_info['product']
    brand = product_info.get('brand', '')
    
    # 创建产品目录
    folder_name = f"{product_id}_{brand}_{product_name}"[:50].strip()
    folder_name = folder_name.replace('/', '_').replace('\\', '_')
    product_dir = os.path.join(workspace_path, folder_name)
    
    os.makedirs(product_dir, exist_ok=True)
    
    result = {
        "product_id": product_id,
        "product_name": product_name,
        "folder": product_dir,
        "status": "running",
        "suppliers": [],
        "errors": []
    }
    
    try:
        # 1. 初始化
        ok, out, err = init_product_folder(product_dir, skill_dir)
        if not ok:
            result['errors'].append(f"初始化失败: {err}")
        
        # 2. 保存产品信息
        ok, out, err = save_product(product_dir, product_info, skill_dir)
        if not ok:
            result['errors'].append(f"保存产品失败: {err}")
        
        # 3-6. 供应商开发（由子代理的AI执行，这里只是框架）
        # 实际搜索、抓取、企查查由AI通过web_search/web_fetch执行
        # 供应商数据通过 save_supplier.py 保存
        
        result['status'] = "ready_for_search"
        result['message'] = "产品目录已就绪，请执行供应商搜索"
        
    except Exception as e:
        result['status'] = "error"
        result['errors'].append(str(e))
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法:")
        print("  python worker_executor.py <工作目录> <产品JSON文件>")
        print("  python worker_executor.py <工作目录> status <产品ID>")
        sys.exit(1)
    
    workspace_path = sys.argv[1]
    action = sys.argv[2]
    
    if action == "status":
        # 查看状态
        pass
    else:
        # 执行单个产品
        product_file = sys.argv[2]
        with open(product_file, 'r', encoding='utf-8') as f:
            product_info = json.load(f)
        
        result = execute_single_product(product_info, workspace_path, SKILL_DIR)
        print(json.dumps(result, ensure_ascii=False, indent=2))
