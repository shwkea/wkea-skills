import os
import sys
import json
from datetime import datetime

def save_product(workspace_path, product_data):
    """保存产品信息（包含产品资料、图片、多个来源网址等）"""
    
    # 创建产品资料文件夹
    product_data_dir = os.path.join(workspace_path, '产品资料')
    product_images_dir = os.path.join(product_data_dir, '产品图片')
    product_files_dir = os.path.join(product_data_dir, '产品文件')
    os.makedirs(product_images_dir, exist_ok=True)
    os.makedirs(product_files_dir, exist_ok=True)
    
    product_json = {
        "name": product_data.get("name", ""),
        "brand": product_data.get("brand", ""),
        "model": product_data.get("model", ""),
        "type": product_data.get("type", ""),
        "specs": product_data.get("specs", {}),
        "source_urls": product_data.get("source_urls", []),
        "images": product_data.get("images", []),
        "files": product_data.get("files", []),
        "created_at": datetime.now().isoformat()
    }
    
    product_json_path = os.path.join(workspace_path, 'product.json')
    
    with open(product_json_path, 'w', encoding='utf-8') as f:
        json.dump(product_json, f, ensure_ascii=False, indent=2)
    
    print(json.dumps({"status": "success", "path": product_json_path}, ensure_ascii=False))
    return product_json_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python save_product.py <工作目录> <产品JSON数据或--file 路径>")
        sys.exit(1)
    
    workspace_path = sys.argv[1]
    # 支持 --file 参数（解决 Windows PowerShell 引号问题）
    if sys.argv[2] == "--file":
        with open(sys.argv[3], encoding="utf-8") as f:
            product_data = json.load(f)
    else:
        product_data = json.loads(sys.argv[2])
    
    save_product(workspace_path, product_data)