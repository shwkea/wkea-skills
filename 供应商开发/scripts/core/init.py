import os
import sys
from datetime import datetime

def init_workspace(product_name, product_count=1):
    """创建供应商开发工作目录结构"""
    
    today = datetime.now().strftime('%Y%m%d_%H%M%S')
    workspace_name = f"供应商开发_{today}_{product_name}等{product_count}个产品"
    
    # 获取当前工作区路径（跨平台兼容）
    # 优先使用环境变量，其次使用当前脚本所在目录的上级目录
    workspace_base = os.environ.get('WORKBUDDY_WORKSPACE', os.getcwd())
    workspace_path = os.path.join(workspace_base, workspace_name)
    
    # 创建目录结构
    dirs = [
        workspace_path,
        os.path.join(workspace_path, '产品资料', '产品图片'),
        os.path.join(workspace_path, '产品资料', '产品文件'),
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    
    # 返回JSON格式的目录信息
    result = {
        "workspace_path": workspace_path,
        "product_name": product_name,
        "product_count": product_count,
        "created_at": datetime.now().isoformat(),
        "status": "initialized"
    }
    
    import json
    print(json.dumps(result, ensure_ascii=False))
    return workspace_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python init.py <产品名称> [产品数量]")
        sys.exit(1)
    
    product_name = sys.argv[1]
    product_count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    init_workspace(product_name, product_count)
