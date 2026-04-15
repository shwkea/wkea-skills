"""
save_execution_log.py — 追加执行日志条目
用法：
  python save_execution_log.py <工作目录> <操作类型> <消息> [来源URL]

操作类型建议：
  search      搜索操作
  fetch       抓取网页
  verify      核查供应商
  download    下载文件
  save        保存数据
  note        备注
  error       错误记录
  result      结果汇总

示例：
  python save_execution_log.py ./产品A search "百度搜索'SMC电磁阀代理商'，获得23条结果"
  python save_execution_log.py ./产品A fetch "抓取 https://xxx.com 产品页，获得价格¥120/个" "https://xxx.com"
  python save_execution_log.py ./产品A save "保存供应商：上海XX贸易有限公司"
"""
import os
import sys
import json
from datetime import datetime


def append_log(workspace_path, action_type, message, source_url=""):
    log_path = os.path.join(workspace_path, "execution_log.json")
    
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"logs": [], "created_at": datetime.now().isoformat()}
    
    entry = {
        "id": len(data["logs"]) + 1,
        "time": datetime.now().strftime("%H:%M:%S"),
        "datetime": datetime.now().isoformat(),
        "type": action_type,
        "message": message,
        "source_url": source_url
    }
    data["logs"].append(entry)
    data["updated_at"] = datetime.now().isoformat()
    
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(json.dumps({"status": "success", "log_count": len(data["logs"]), "entry": entry}, ensure_ascii=False))


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python save_execution_log.py <工作目录> <操作类型> <消息> [来源URL]")
        sys.exit(1)
    
    workspace_path = sys.argv[1]
    action_type = sys.argv[2]
    message = sys.argv[3]
    source_url = sys.argv[4] if len(sys.argv) > 4 else ""
    
    append_log(workspace_path, action_type, message, source_url)
