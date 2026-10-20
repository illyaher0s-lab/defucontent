#!/usr/bin/env python3
"""写入飞书多维表格 - 用于德夫选题/记录回填

用法:
    python scripts/feishu_write.py <app_token> <table_id> <data.json>

数据格式: [{"文本": "...", "核心价值点": "...", ...}, ...]
字段名必须匹配表格实际字段名。
"""
import sys
import json
import os
import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *

def read_credentials():
    """从 ~/.hermes/.env 读取凭证"""
    env_file = os.path.expanduser("~/.hermes/.env")
    app_id = app_secret = None
    
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line:
                key, val = line.strip().split('=', 1)
                val = val.strip('"').strip("'")
                if 'APP_ID' in key:
                    app_id = val
                elif 'APP_SECRET' in key:
                    app_secret = val
    
    if not app_id or not app_secret:
        raise ValueError("Missing FEISHU_APP_ID or FEISHU_APP_SECRET in ~/.hermes/.env")
    
    return app_id, app_secret

def write_records(app_token, table_id, records):
    """批量写入记录"""
    app_id, app_secret = read_credentials()
    client = lark.Client.builder().app_id(app_id).app_secret(app_secret).build()
    
    success = 0
    for i, fields in enumerate(records, 1):
        request = CreateAppTableRecordRequest.builder() \
            .app_token(app_token) \
            .table_id(table_id) \
            .request_body(AppTableRecord.builder().fields(fields).build()) \
            .build()
        
        response = client.bitable.v1.app_table_record.create(request)
        
        if response.success():
            print(f"✓ {i}/{len(records)}")
            success += 1
        else:
            print(f"✗ {i}/{len(records)}: {response.code} - {response.msg}", file=sys.stderr)
    
    return success

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    
    app_token, table_id, data_file = sys.argv[1:4]
    
    with open(data_file, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    success = write_records(app_token, table_id, records)
    print(f"\n✓ {success}/{len(records)} records written")
