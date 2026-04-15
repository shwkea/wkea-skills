import os
import sys
import json
from datetime import datetime

def collect_suppliers(workspace_path):
    """从各个供应商 info.json 汇总生成 suppliers.json（完整字段版）"""
    
    suppliers = []
    
    # 遍历所有子文件夹（供应商文件夹可以任意命名，只要含 info.json 即可）
    for item in sorted(os.listdir(workspace_path)):
        item_path = os.path.join(workspace_path, item)
        if not os.path.isdir(item_path):
            continue
        # 跳过系统文件夹
        if item in ("产品资料",):
            continue
        info_json_path = os.path.join(item_path, "info.json")
        if not os.path.exists(info_json_path):
            continue
        
        with open(info_json_path, "r", encoding="utf-8") as f:
            s = json.load(f)
        
        contact = s.get("contact", {})
        qcc = s.get("qcc_info", {})
        
        entry = {
            "id": len(suppliers) + 1,
            # 基本
            "name": s.get("name", ""),
            "short_name": s.get("short_name", ""),
            "source": s.get("source", ""),
            "source_urls": s.get("source_urls", []),
            "discovery_url": s.get("discovery_url", ""),
            "official_url": s.get("official_url", ""),
            "qcc_url": s.get("qcc_url", ""),
            # 授权 & 交易
            "is_authorized": s.get("is_authorized", False),
            "authorization_cert": s.get("authorization_cert", ""),
            "price": s.get("price", ""),
            "price_range": s.get("price_range", ""),
            "moq": s.get("moq", ""),
            "delivery": s.get("delivery", ""),
            "stock_status": s.get("stock_status", ""),
            "payment": s.get("payment", ""),
            # 联系方式（完整）
            "contact": {
                "name": contact.get("name", ""),
                "title": contact.get("title", ""),
                "phone": contact.get("phone", ""),
                "mobile": contact.get("mobile", ""),
                "email": contact.get("email", ""),
                "wechat": contact.get("wechat", ""),
                "qq": contact.get("qq", ""),
                "fax": contact.get("fax", ""),
                "address": contact.get("address", ""),
                "city": contact.get("city", ""),
                "website": contact.get("website", "")
            },
            # 企查查（完整）
            "qcc_info": {
                "full_name": qcc.get("full_name", ""),
                "credit_code": qcc.get("credit_code", ""),
                "legal_person": qcc.get("legal_person", ""),
                "registered_capital": qcc.get("registered_capital", ""),
                "paid_capital": qcc.get("paid_capital", ""),
                "established_date": qcc.get("established_date", ""),
                "business_status": qcc.get("business_status", ""),
                "business_scope": qcc.get("business_scope", ""),
                "registered_address": qcc.get("registered_address", ""),
                "org_type": qcc.get("org_type", ""),
                "industry": qcc.get("industry", ""),
                "annual_revenue": qcc.get("annual_revenue", ""),
                "employee_count": qcc.get("employee_count", ""),
                "risk_info": qcc.get("risk_info", ""),
                "penalty_count": qcc.get("penalty_count", 0),
                "lawsuit_count": qcc.get("lawsuit_count", 0),
                "dishonesty_count": qcc.get("dishonesty_count", 0),
                "abnormal_status": qcc.get("abnormal_status", False),
                "abnormal_reason": qcc.get("abnormal_reason", ""),
                "shareholders": qcc.get("shareholders", []),
                "actual_controller": qcc.get("actual_controller", ""),
                "investments": qcc.get("investments", []),
                "patent_count": qcc.get("patent_count", 0),
                "trademark_count": qcc.get("trademark_count", 0),
                "software_copyright_count": qcc.get("software_copyright_count", 0),
                "certifications": qcc.get("certifications", []),
                "honors": qcc.get("honors", [])
            },
            # 经营能力
            "main_products": s.get("main_products", ""),
            "business_years": s.get("business_years", ""),
            "service_policy": s.get("service_policy", ""),
            "after_sale": s.get("after_sale", ""),
            # 评估
            "notes": s.get("notes", ""),
            "risk_level": s.get("risk_level", ""),
            "recommendation": s.get("recommendation", ""),
            "verification_status": s.get("verification_status", "unverified"),
            "created_at": s.get("created_at", "")
        }
        suppliers.append(entry)
    
    # 读取 product.json
    product_json_path = os.path.join(workspace_path, "product.json")
    product_name = "未知产品"
    if os.path.exists(product_json_path):
        with open(product_json_path, "r", encoding="utf-8") as f:
            pd = json.load(f)
            product_name = f"{pd.get('brand','')} {pd.get('model','')} {pd.get('name','')}".strip()
    
    result = {
        "product": product_name,
        "total_suppliers": len(suppliers),
        "suppliers": suppliers,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    output_path = os.path.join(workspace_path, "suppliers.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(json.dumps({"status": "success", "path": output_path, "count": len(suppliers)}, ensure_ascii=False))
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python collect_suppliers.py <产品文件夹路径>")
        sys.exit(1)
    collect_suppliers(sys.argv[1])
