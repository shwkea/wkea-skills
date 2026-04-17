#!/usr/bin/env python3
"""
并发供应商开发执行器
使用 WorkBuddy Team 模式，同时启动多个子代理处理不同产品
"""

import json
import os
import sys
from datetime import datetime

# 添加脚本目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

def create_parallel_plan(workspace_path, products, max_workers=3):
    """创建并发执行计划
    
    Args:
        workspace_path: 工作目录
        products: 产品列表
        max_workers: 最大并发数（子代理数量）
    """
    
    plan_path = os.path.join(workspace_path, 'parallel_plan.json')
    
    # 将产品分组，每个组分配给一个子代理
    groups = []
    for i in range(0, len(products), max_workers):
        group = products[i:i + max_workers]
        groups.append({
            "group_id": len(groups) + 1,
            "products": group,
            "status": "pending"
        })
    
    plan = {
        "type": "parallel_supplier_development",
        "created_at": datetime.now().isoformat(),
        "max_workers": max_workers,
        "product_count": len(products),
        "group_count": len(groups),
        "groups": groups,
        "workspace": workspace_path
    }
    
    # 保存计划
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    
    return plan


def generate_worker_prompts(plan, skill_base_dir):
    """生成每个子代理的工作指令"""
    
    prompts = []
    
    for group in plan['groups']:
        # 为每个组生成详细的工作指令
        prompt = f"""# 子任务：供应商开发（组 {group['group_id']}）

## 工作目录
{plan['workspace']}

## 技能目录
{skill_base_dir}

## 产品列表
{json.dumps(group['products'], ensure_ascii=False, indent=2)}

## 执行要求

对每个产品执行完整的供应商开发流程：

1. **初始化产品目录**
   ```bash
   python "{skill_base_dir}/scripts/core/init.py" "<产品目录>" 1
   ```

2. **保存产品信息**
   ```bash
   python "{skill_base_dir}/scripts/data/save_product.py" "<产品目录>" --file <临时JSON文件>
   ```

3. **全网搜索供应商**
   - 使用 web_search 搜索产品关键词
   - 每个产品至少找到 5 家供应商
   - 记录每次搜索到 execution_log

4. **抓取核实**
   - 使用 web_fetch 打开每个供应商页面
   - 提取联系方式、价格、货期、授权状态

5. **企查查核查**
   - 搜索供应商工商信息
   - 提取法人、注册资本、风险信息

6. **保存供应商**
   - 每个供应商调用 save_supplier.py
   - 保存到对应公司名文件夹的 info.json

7. **汇总生成报告**
   ```bash
   python "{skill_base_dir}/scripts/data/collect_suppliers.py" "<产品目录>"
   python "{skill_base_dir}/scripts/report/generate_html.py" "<产品目录>"
   ```

## 注意事项
- 所有文件写入必须调用脚本
- 每次操作记录日志
- 产品目录以 "产品序号_品牌_产品名" 命名
"""
        
        prompts.append({
            "group_id": group['group_id'],
            "prompt": prompt
        })
    
    return prompts


def execute_parallel(workspace_path, max_workers=3):
    """执行并发供应商开发
    
    这是一个规划函数，实际执行需要通过 WorkBuddy Team 模式
    """
    
    # 读取已有的 batch_plan.json
    batch_plan_path = os.path.join(workspace_path, 'batch_plan.json')
    if not os.path.exists(batch_plan_path):
        print(json.dumps({
            "status": "error",
            "message": "batch_plan.json 不存在，请先运行 batch_plan.py init"
        }, ensure_ascii=False))
        return
    
    with open(batch_plan_path, 'r', encoding='utf-8') as f:
        batch_plan = json.load(f)
    
    # 按状态分组
    pending_products = [p for p in batch_plan['products'] if p['status'] == 'pending']
    completed_products = [p for p in batch_plan['products'] if p['status'] == 'completed']
    
    print(json.dumps({
        "status": "ready",
        "workspace": workspace_path,
        "total_products": len(batch_plan['products']),
        "pending_products": len(pending_products),
        "completed_products": len(completed_products),
        "max_workers": max_workers,
        "suggestion": "使用 WorkBuddy Team 模式启动多个子代理并发处理待处理产品",
        "pending_list": pending_products[:10]  # 显示前10个
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python parallel_executor.py <工作目录> plan [最大并发数]")
        print("  python parallel_executor.py <工作目录> execute [最大并发数]")
        sys.exit(1)
    
    workspace_path = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else "execute"
    max_workers = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    
    skill_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if action == "plan":
        # 读取 batch_plan
        batch_plan_path = os.path.join(workspace_path, 'batch_plan.json')
        if os.path.exists(batch_plan_path):
            with open(batch_plan_path, 'r', encoding='utf-8') as f:
                batch_plan = json.load(f)
            plan = create_parallel_plan(workspace_path, batch_plan['products'], max_workers)
            prompts = generate_worker_prompts(plan, skill_base_dir)
            print(json.dumps({
                "status": "success",
                "plan": plan,
                "prompts": prompts
            }, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"status": "error", "message": "batch_plan.json 不存在"}))
    else:
        execute_parallel(workspace_path, max_workers)
