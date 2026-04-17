import os
import sys
import json
from datetime import datetime

def create_batch_plan(workspace_path, products):
    """创建批量供应商开发执行计划
    
    在提取完全部产品后，立即生成整体执行计划，然后按计划逐个执行。
    
    Args:
        workspace_path: 根目录路径
        products: 产品列表（从Excel读取或用户提供）
    """
    
    plan_path = os.path.join(workspace_path, 'batch_plan.json')
    
    # 按品类分组（基于品牌）
    brand_groups = {}
    for p in products:
        brand = p.get('brand', '未知品牌') or '未知品牌'
        if brand not in brand_groups:
            brand_groups[brand] = []
        brand_groups[brand].append(p)
    
    # 构建执行计划
    plan = {
        "type": "batch_supplier_development",
        "status": "pending",  # pending -> in_progress -> completed
        "created_at": datetime.now().isoformat(),
        "product_count": len(products),
        "brand_groups": len(brand_groups),
        "workspace": workspace_path,
        "summary": {
            "total_products": len(products),
            "total_quantity": sum(p.get('qty', 0) for p in products),
            "with_brand": sum(1 for p in products if p.get('brand')),
            "without_brand": sum(1 for p in products if not p.get('brand')),
            "urgent_count": sum(1 for p in products if '最短货期' in p.get('note', '')),
            "requester_count": len(set(p.get('requester', '') for p in products if p.get('requester')))
        },
        "products": [
            {
                "id": i + 1,
                "seq": p.get('seq'),  # Excel中的序号
                "brand": p.get('brand', ''),
                "product": p.get('product'),
                "spec": p.get('spec', ''),
                "qty": p.get('qty', 0),
                "unit": p.get('unit', ''),
                "note": p.get('note', ''),
                "requester": p.get('requester', ''),
                "is_urgent": '最短货期' in p.get('note', ''),
                "status": "pending",  # pending -> searching -> verifying -> completed -> failed
                "supplier_count": 0,
                "started_at": None,
                "completed_at": None
            }
            for i, p in enumerate(products)
        ],
        "phases": [
            {
                "id": 1,
                "name": "提取产品信息",
                "description": "从Excel或用户输入中提取所有产品",
                "status": "completed",  # 假设调用此脚本时已完成
                "products_extracted": len(products)
            },
            {
                "id": 2,
                "name": "制定执行计划",
                "description": "按品牌分组、优先级排序、生成执行清单",
                "status": "completed"
            },
            {
                "id": 3,
                "name": "并发搜索供应商",
                "description": "对每个产品全网搜索供应商（每个产品至少5家）",
                "status": "pending",
                "progress": {"done": 0, "total": len(products)}
            },
            {
                "id": 4,
                "name": "企查查核查",
                "description": "核实每家供应商的工商信息",
                "status": "pending",
                "progress": {"done": 0, "total": 0}
            },
            {
                "id": 5,
                "name": "汇总生成报告",
                "description": "汇总所有供应商数据，生成HTML报告和Excel",
                "status": "pending"
            }
        ],
        "execution_order": {
            "strategy": "优先级优先",
            "details": [
                "1. 优先处理标记'最短货期'的产品",
                "2. 同品牌产品可共享供应商信息",
                "3. 并发执行无依赖关系的产品"
            ]
        },
        "log": [
            {
                "time": datetime.now().isoformat(),
                "phase": "init",
                "message": f"批量计划初始化，共{len(products)}个产品"
            }
        ]
    }
    
    # 保存计划
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    
    return plan

def update_batch_plan(workspace_path, action, data=None):
    """更新批量执行计划
    
    Actions:
    - init: 初始化计划（从产品列表）
    - update_product: 更新单个产品状态
    - update_phase: 更新阶段状态
    - log: 添加日志
    - complete: 标记完成
    """
    
    plan_path = os.path.join(workspace_path, 'batch_plan.json')
    
    if action == "init":
        return create_batch_plan(workspace_path, data.get('products', []))
    
    if not os.path.exists(plan_path):
        return {"status": "error", "message": "计划文件不存在"}
    
    with open(plan_path, 'r', encoding='utf-8') as f:
        plan = json.load(f)
    
    if action == "update_product":
        product_id = data.get('product_id')
        for p in plan['products']:
            if p['id'] == product_id:
                p.update(data)
                break
        plan['log'].append({
            "time": datetime.now().isoformat(),
            "product_id": product_id,
            "message": data.get('message', '产品状态更新')
        })
    
    elif action == "update_phase":
        phase_id = data.get('phase_id')
        for ph in plan['phases']:
            if ph['id'] == phase_id:
                ph['status'] = data.get('status', 'in_progress')
                if 'progress' in data:
                    ph['progress'] = data['progress']
                break
        plan['log'].append({
            "time": datetime.now().isoformat(),
            "phase_id": phase_id,
            "message": data.get('message', f"阶段{phase_id}状态更新")
        })
    
    elif action == "log":
        plan['log'].append({
            "time": datetime.now().isoformat(),
            **data
        })
    
    elif action == "complete":
        plan['status'] = 'completed'
        plan['completed_at'] = datetime.now().isoformat()
    
    else:
        return {"status": "error", "message": f"未知操作: {action}"}
    
    # 保存更新
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    
    return {"status": "success", "plan_path": plan_path, "plan": plan}

def get_batch_plan(workspace_path):
    """获取当前批量计划状态"""
    plan_path = os.path.join(workspace_path, 'batch_plan.json')
    if not os.path.exists(plan_path):
        return None
    with open(plan_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_next_product(workspace_path):
    """获取下一个待处理的产品（优先级：最短货期 > 无供应商 > 已有供应商少）"""
    plan = get_batch_plan(workspace_path)
    if not plan:
        return None
    
    # 按优先级排序
    pending = [p for p in plan['products'] if p['status'] == 'pending']
    if not pending:
        return None
    
    # 优先选择标记"最短货期"的产品
    urgent = [p for p in pending if p.get('is_urgent')]
    if urgent:
        return urgent[0]
    
    return pending[0]

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法:")
        print("  python batch_plan.py <工作目录> init '<JSON产品列表>'")
        print("  python batch_plan.py <工作目录> status")
        print("  python batch_plan.py <工作目录> next")
        print("  python batch_plan.py <工作目录> view")
        print("  python batch_plan.py <工作目录> update_product '<JSON数据>'")
        print("  python batch_plan.py <工作目录> update_phase '<JSON数据>'")
        print("  python batch_plan.py <工作目录> log '<JSON数据>'")
        print("  python batch_plan.py <工作目录> complete")
        sys.exit(1)
    
    workspace_path = sys.argv[1]
    action = sys.argv[2]
    
    if action == "init":
        products = json.loads(sys.argv[3]) if len(sys.argv) > 3 else []
        result = update_batch_plan(workspace_path, action, {'products': products})
    elif action == "status":
        # 查看执行状态
        plan = get_batch_plan(workspace_path)
        if not plan:
            print(json.dumps({"status": "error", "message": "无计划文件"}))
            sys.exit(1)
        
        pending = [p for p in plan['products'] if p['status'] == 'pending']
        searching = [p for p in plan['products'] if p['status'] == 'searching']
        verifying = [p for p in plan['products'] if p['status'] == 'verifying']
        completed = [p for p in plan['products'] if p['status'] == 'completed']
        failed = [p for p in plan['products'] if p['status'] == 'failed']
        
        print(json.dumps({
            "status": "ok",
            "total": len(plan['products']),
            "pending": len(pending),
            "searching": len(searching),
            "verifying": len(verifying),
            "completed": len(completed),
            "failed": len(failed),
            "progress_pct": round(len(completed) / len(plan['products']) * 100, 1),
            "next_products": [p['id'] for p in (pending + searching)[:3]]
        }, ensure_ascii=False, indent=2))
        sys.exit(0)
    elif action == "next":
        result = get_next_product(workspace_path)
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # 检查是否全部完成
            plan = get_batch_plan(workspace_path)
            if plan:
                completed = [p for p in plan['products'] if p['status'] == 'completed']
                print(json.dumps({
                    "status": "done",
                    "message": "所有产品已处理完成",
                    "completed_count": len(completed),
                    "total_count": len(plan['products'])
                }, ensure_ascii=False, indent=2))
            else:
                print(json.dumps({"status": "error", "message": "无计划文件"}))
        sys.exit(0)
    elif action == "view":
        result = get_batch_plan(workspace_path)
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("无计划文件")
        sys.exit(0)
    else:
        data = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
        result = update_batch_plan(workspace_path, action, data)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
