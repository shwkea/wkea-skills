import sys
import json

def verify_supplier(supplier_data):
    """核查供应商（模拟核查流程）"""
    
    # 模拟核查逻辑
    verification = supplier_data.get("verification", {})
    
    # 这里可以接入实际的核查API或爬虫
    # 示例：核查价格
    if verification.get("price") == "pending":
        verification["price"] = "verified"
    
    # 示例：核查货期
    if verification.get("delivery") == "pending":
        verification["delivery"] = "verified"
    
    result = {
        "status": "success",
        "supplier": supplier_data.get("name"),
        "verification": verification
    }
    
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python verify_supplier.py <供应商JSON数据>")
        sys.exit(1)
    
    supplier_data = json.loads(sys.argv[1])
    verify_supplier(supplier_data)
