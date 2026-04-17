import os
import sys
import json
from datetime import datetime

def update_plan(workspace_path, action, data=None):
    """更新Plan进度"""
    
    plan_path = os.path.join(workspace_path, 'plan.json')
    
    if action == "init":
        # 初始化Plan
        plan = {
            "product_name": data.get("name", ""),
            "status": "in_progress",
            "created_at": datetime.now().isoformat(),
            "steps": [
                {"id": 1, "name": "分析产品信息", "status": "pending"},
                {"id": 2, "name": "全网搜索供应商", "status": "pending"},
                {"id": 3, "name": "核查供应商", "status": "pending"},
                {"id": 4, "name": "生成HTML报告", "status": "pending"},
                {"id": 5, "name": "导出Excel", "status": "pending"},
                {"id": 6, "name": "发送完成通知", "status": "pending"}
            ],
            "suppliers": [],
            "log": []
        }
    elif action == "update":
        # 更新指定步骤
        step_id = data.get("step_id")
        status = data.get("status", "done")
        
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan = json.load(f)
        
        for step in plan["steps"]:
            if step["id"] == step_id:
                step["status"] = status
                break
        
        plan["log"].append({
            "time": datetime.now().isoformat(),
            "step_id": step_id,
            "status": status
        })
    elif action == "add_supplier":
        # 添加供应商
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan = json.load(f)
        
        plan["suppliers"].append(data)
    elif action == "complete":
        # 完成
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan = json.load(f)
        
        plan["status"] = "completed"
        plan["completed_at"] = datetime.now().isoformat()
    else:
        print(json.dumps({"status": "error", "message": f"未知操作: {action}"}, ensure_ascii=False))
        return
    
    # 保存Plan
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    
    print(json.dumps({"status": "success", "plan_path": plan_path}, ensure_ascii=False))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python update_plan.py <工作目录> <init|update|add_supplier|complete> [JSON数据]")
        sys.exit(1)
    
    workspace_path = sys.argv[1]
    action = sys.argv[2]
    data = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
    
    update_plan(workspace_path, action, data)
