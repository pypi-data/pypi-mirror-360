import os
import random
import traceback
from pathlib import Path

import yaml
from starlette.responses import JSONResponse
import datetime
from fastapi import Request, status
from vllm.logger import init_logger
from starlette.middleware.base import BaseHTTPMiddleware
logger = init_logger('vllm.open_api_key')
from himile_model_middleware.db_pool import AsyncDBPool

#user_config = {
#    "user": "u_ekmp",
#    "password": "ekmptest",
#    "host": "192.168.220.152",
#    "database": "ekmp",
#    "maxconnections": 10,
#    "mincached": 2,
#    "maxcached": 5,
#    "maxshared": 3,
#}



def load_config():
    # 确定操作系统并设置配置文件路径
    if os.name == 'nt':  # Windows系统
        username = os.getenv('USERNAME')
        config_path = Path(f"C:/Users/{username}/config.yaml")
    else:  # Linux/Unix系统
        config_path = Path("/root/config.yaml")

    # 检查文件是否存在
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在于: {config_path}")

    # 读取并解析YAML文件
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config


config = load_config()

user_config = {
    "user": config['database']['user'],
    "password": config['database']['password'],
    "host": config['database']['host'],
    "database": config['database']['database'],
    "maxconnections": 10,
    "mincached": 2,
    "maxcached": 5,
    "maxshared": 3,
}

# 创建异步数据库操作对象
db = AsyncDBPool(**user_config)


class HelloMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            # all_headers = dict(request.headers)
            # print(all_headers)
            API_KEY_BEARER = request.headers.get("Authorization")
            json_data = await request.json()
            ip = request.client.host
            API_KEY = API_KEY_BEARER.split("Bearer")[-1].strip()
            logger.info(f"←←←←← 开始处理请求 | 请求参数解析 | 原始数据: {json_data} | API-KEY: {API_KEY} ←←←←←")
            if not API_KEY:
                return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"message": "Unauthorized",
                                 "details": "Invalid API Key or token"
                                 }
                        )
            select_query_count = """
                                    SELECT
                                        r.id,
                                        req.create_time AS today,
                                        req.use_count AS total_used,
                                        r.total_count AS total_allocated 
                                    FROM
                                        t_key_model r
                                        LEFT JOIN t_api_key k ON r.key_id = k.id
                                        LEFT JOIN t_chatai_model m ON r.model_id = m.id
                                        LEFT JOIN t_api_key_requests req ON r.id = req.relation_id 
                                    WHERE
                                        k.del_flag = 0 
                                        AND m.del_flag = 0 
                                        AND m.model_name = %s
                                        AND k.api_key = %s
                                    ORDER BY
                                        create_time DESC 
                                        LIMIT 1
                                    FOR UPDATE
                                """
            async with await db.select(select_query_count, (json_data['model'], API_KEY,)) as results_count:
                if not results_count:
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": "API_KEY无效"}
                    )
                
                if results_count[0]['today'] and results_count[0]['today'].date() == datetime.datetime.today().date():
                    is_used_greater_than_allocated = results_count[0]['total_used'] > results_count[0]['total_allocated']
                    if is_used_greater_than_allocated:
                        return JSONResponse(
                            status_code=status.HTTP_403_FORBIDDEN,
                            content={"detail": "API调用次数已用尽，请等待至明天0点重置"}
                        )
                else:
                    insert_query_initialize = """
                                                    INSERT INTO t_api_key_requests (
                                                        relation_id, use_count
                                                    ) VALUES (
                                                        %s, 0
                                                    )
                                                    ON DUPLICATE KEY UPDATE use_count = VALUES(use_count)
                                                """
                    async with await db.update([insert_query_initialize], [
                        (
                                results_count[0]['id'],
                        )]):
                        pass
                update_query = """
                    UPDATE t_api_key_requests 
                    SET use_count = use_count + 1 
                    WHERE relation_id = %s and DATE(create_time) = CURRENT_DATE
                """
                async with await db.update([update_query], [(results_count[0]['id'])]) as result_update:
                            pass
                insert_sql = """
                        INSERT INTO t_api_key_records (
                            relation_id, question,
                            ip_address
                        ) VALUES (
                            %s, %s,
                            %s
                        )
                    """
                if isinstance(json_data['messages'][-1]['content'], str):
                    async with await db.update([insert_sql], [(
                            results_count[0]['id'], json_data['messages'][-1]['content'][:100],
                            ip
                    )]):
                        pass
                # 继续处理请求并获取响应
                response = await call_next(request)

                # 你可以在这里修改响应，或者做其他操作
                return response
        except Exception:
            error_traceback = traceback.format_exc()
            return JSONResponse(
                status_code=status.HTTP_502_BAD_GATEWAY,
                content={"detail": f"无法连接AI服务，具体报错信息{error_traceback}"}
            )
