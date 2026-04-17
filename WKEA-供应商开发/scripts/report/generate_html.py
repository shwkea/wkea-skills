import os
import sys
import json
from datetime import datetime

def generate_html(workspace_path):
    """生成 HTML 报告（嵌入数据，解决本地预览 CORS 问题）
    
    统一使用多产品模板，支持单产品和多产品场景：
    - 单产品：将单个产品包装成 products 数组
    - 多产品：遍历所有产品文件夹
    """
    
    # 获取模板路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, 'templates', 'report.html')
    
    # 读取模板
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 收集 summary 数据
    summary = {
        "product_count": 0,
        "total_suppliers": 0,
        "authorized_count": 0,
        "pending_count": 0,
        "products": []
    }
    
    # 检查是否是单产品文件夹（包含 product.json 和 suppliers.json）
    product_json_path = os.path.join(workspace_path, 'product.json')
    suppliers_json_path = os.path.join(workspace_path, 'suppliers.json')
    
    if os.path.exists(product_json_path) and os.path.exists(suppliers_json_path):
        # 单产品模式：直接读取当前文件夹的数据
        with open(product_json_path, 'r', encoding='utf-8') as f:
            product_data = json.load(f)
        
        with open(suppliers_json_path, 'r', encoding='utf-8') as f:
            suppliers_data = json.load(f)
        
        suppliers = suppliers_data.get('suppliers', [])
        summary['product_count'] = 1
        summary['total_suppliers'] = len(suppliers)
        
        product_entry = {
            "name": product_data.get('name', os.path.basename(workspace_path)),
            "brand": product_data.get('brand', ''),
            "model": product_data.get('model', ''),
            "type": product_data.get('type', ''),
            "specs": product_data.get('specs', {}),
            "certifications": product_data.get('certifications', []),
            "applications": product_data.get('applications', ''),
            "category": product_data.get('category', ''),
            "source_urls": product_data.get('source_urls', []),
            "images": product_data.get('images', []),
            "image_sources": product_data.get('image_sources', ''),
            "suppliers": []
        }
        
        for s in suppliers:
            if s.get('is_authorized'):
                summary['authorized_count'] += 1
            else:
                summary['pending_count'] += 1
            # 完整透传供应商所有字段
            supplier_entry = dict(s)
            supplier_entry['brand'] = product_data.get('brand', '')
            supplier_entry['model'] = product_data.get('model', '')
            product_entry['suppliers'].append(supplier_entry)
        
        # 产品字段完整透传
        for k in ('specs', 'certifications', 'applications', 'category'):
            if k in product_data:
                product_entry[k] = product_data[k]
        
        summary['products'].append(product_entry)
    else:
        # 多产品模式：遍历所有产品文件夹
        for item in os.listdir(workspace_path):
            item_path = os.path.join(workspace_path, item)
            if not os.path.isdir(item_path):
                continue
            
            product_json_path = os.path.join(item_path, 'product.json')
            suppliers_json_path = os.path.join(item_path, 'suppliers.json')
            
            if not os.path.exists(product_json_path) or not os.path.exists(suppliers_json_path):
                continue
            
            with open(product_json_path, 'r', encoding='utf-8') as f:
                product_data = json.load(f)
            
            with open(suppliers_json_path, 'r', encoding='utf-8') as f:
                suppliers_data = json.load(f)
            
            suppliers = suppliers_data.get('suppliers', [])
            summary['product_count'] += 1
            summary['total_suppliers'] += len(suppliers)
            
            product_entry = {
                "name": product_data.get('name', item),
                "brand": product_data.get('brand', ''),
                "model": product_data.get('model', ''),
                "type": product_data.get('type', ''),
                "specs": product_data.get('specs', {}),
                "certifications": product_data.get('certifications', []),
                "applications": product_data.get('applications', ''),
                "category": product_data.get('category', ''),
                "source_urls": product_data.get('source_urls', []),
                "images": product_data.get('images', []),
                "image_sources": product_data.get('image_sources', ''),
                "suppliers": []
            }
            
            for s in suppliers:
                if s.get('is_authorized'):
                    summary['authorized_count'] += 1
                else:
                    summary['pending_count'] += 1
                supplier_entry = dict(s)
                supplier_entry['brand'] = product_data.get('brand', '')
                supplier_entry['model'] = product_data.get('model', '')
                product_entry['suppliers'].append(supplier_entry)
            
            summary['products'].append(product_entry)
    
    # 读取 execution_log
    execution_log = None
    log_path = os.path.join(workspace_path, 'execution_log.json')
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            execution_log = json.load(f)
    
    # 准备注入的数据脚本 (放在 head 中)
    data_script = f"""
    <script>
        window.SUMMARY_DATA = {json.dumps(summary, ensure_ascii=False)};
        window.EXEC_LOG_DATA = {json.dumps(execution_log, ensure_ascii=False) if execution_log else 'null'};
    </script>
    """
    
    # 插入数据脚本到 </head> 之前
    html_content = html_content.replace('</head>', data_script + '</head>')
    
    # 保存输出
    output_path = os.path.join(workspace_path, 'report.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(json.dumps({"status": "success", "path": output_path}, ensure_ascii=False))
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python generate_html.py <工作目录或产品文件夹>")
        sys.exit(1)
    
    workspace_path = sys.argv[1]
    generate_html(workspace_path)