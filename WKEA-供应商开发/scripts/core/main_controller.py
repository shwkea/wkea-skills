#!/usr/bin/env python3
"""
供应商开发主控脚本
用于 WorkBuddy Team 模式的主控任务，协调多个子代理并发执行
"""

import json
import os
import sys
import subprocess
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))

def run_command(cmd):
    """执行命令并返回结果"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def main_controller(action, workspace_path, max_workers=3):
    """主控函数"""
    
    batch_plan_path = os.path.join(workspace_path, 'batch_plan.json')
    
    if not os.path.exists(batch_plan_path):
        print(json.dumps({
            "status": "error",
            "message": "batch_plan.json 不存在，请先初始化"
        }, ensure_ascii=False))
        return
    
    with open(batch_plan_path, 'r', encoding='utf-8') as f:
        batch_plan = json.load(f)
    
    if action == "status":
        # 显示当前状态
        pending = [p for p in batch_plan['products'] if p['status'] == 'pending']
        completed = [p for p in batch_plan['products'] if p['status'] == 'completed']
        failed = [p for p in batch_plan['products'] if p['status'] == 'failed']
        
        print(json.dumps({
            "status": "ok",
            "total": len(batch_plan['products']),
            "pending": len(pending),
            "completed": len(completed),
            "failed": len(failed),
            "pending_list": pending[:5]
        }, ensure_ascii=False, indent=2))
        
    elif action == "next":
        # 获取下一个待处理产品
        pending = [p for p in batch_plan['products'] if p['status'] == 'pending']
        if pending:
            # 按紧急程度和序号排序
            urgent = [p for p in pending if p.get('is_urgent')]
            normal = [p for p in pending if not p.get('is_urgent')]
            next_product = (urgent + normal)[0]
            print(json.dumps({
                "status": "ok",
                "product": next_product
            }, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({
                "status": "done",
                "message": "所有产品已处理完成"
            }))
    
    elif action == "batch":
        # 生成批量任务（每个产品一个任务）
        pending = [p for p in batch_plan['products'] if p['status'] == 'pending']
        urgent = sorted([p for p in pending if p.get('is_urgent')], key=lambda x: x['id'])
        normal = sorted([p for p in pending if not p.get('is_urgent')], key=lambda x: x['id'])
        
        # 优先处理紧急产品
        all_tasks = urgent + normal
        
        tasks = []
        for i, p in enumerate(all_tasks[:max_workers]):  # 限制并发数
            folder_name = f"{p['id']}_{p['brand']}_{p['product']}"
            folder_name = folder_name[:50].strip()  # 限制长度
            
            task = {
                "task_id": i + 1,
                "product": p,
                "folder": os.path.join(workspace_path, folder_name),
                "skill_dir": SKILL_DIR
            }
            tasks.append(task)
        
        print(json.dumps({
            "status": "ready",
            "task_count": len(tasks),
            "tasks": tasks,
            "remaining": len(all_tasks) - len(tasks)
        }, ensure_ascii=False, indent=2))
    
    elif action == "update":
        # 更新产品状态
        if len(sys.argv) < 5:
            print(json.dumps({"status": "error", "message": "缺少参数"}))
            return
        
        product_id = int(sys.argv[4])
        new_status = sys.argv[5] if len(sys.argv) > 5 else "completed"
        
        for p in batch_plan['products']:
            if p['id'] == product_id:
                p['status'] = new_status
                break
        
        with open(batch_plan_path, 'w', encoding='utf-8') as f:
            json.dump(batch_plan, f, ensure_ascii=False, indent=2)
        
        print(json.dumps({
            "status": "ok",
            "product_id": product_id,
            "new_status": new_status
        }))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法:")
        print("  python main_controller.py <工作目录> status")
        print("  python main_controller.py <工作目录> next")
        print("  python main_controller.py <工作目录> batch [最大并发数]")
        print("  python main_controller.py <工作目录> update <产品ID> <状态>")
        sys.exit(1)
    
    workspace_path = sys.argv[1]
    action = sys.argv[2]
    max_workers = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    
    main_controller(action, workspace_path, max_workers)
