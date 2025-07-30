""" server """
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pydantic import BaseModel # 导入 BaseModel
from fastapi import FastAPI
from .core import ReallifeClient

async def perform_startup_tasks():
    """ 1 """
    print("Performing startup tasks...")
    scheduler.start()
    print("APScheduler 启动")
    # Your existing startup logic here

async def perform_shutdown_tasks():
    """ 1 """
    print("Performing shutdown tasks...")
    scheduler.shutdown()
    print("APScheduler 关闭")
    # Your existing shutdown logic here

class TaskRequest(BaseModel):
    """ 1 """
    task: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    """_summary_

    Args:
        app (FastAPI): _description_
    """
    await perform_startup_tasks()
    yield
    await perform_shutdown_tasks()


app = FastAPI(lifespan=lifespan)

scheduler = BackgroundScheduler()

reallife = ReallifeClient()

scheduler.add_job(reallife.kanban, CronTrigger(hour=9, minute=40, day_of_week='mon-fri'))


@app.get("/build_kanban")
async def build_kanban():
    """_summary_

    Args:
        app (FastAPI): _description_
    """
    result = reallife.kanban()
    return {"message": result}

@app.get("/add_kanban")
async def add_kanban():
    """_summary_

    Args:
        app (FastAPI): _description_
    """
    result = reallife.add_kanban(6)
    return {"message": result}


class BuildFlexibleConfigRequest(BaseModel):
    """ 1 """
    task: str = None
    type: str = 'flex' # or pool
    action: bool = True



@app.post("/build_flexible")
async def build_flexible(build_flexible_config: BuildFlexibleConfigRequest):
    """_summary_

    Args:
        build_flexible_config (BuildFlexibleConfigRequest): _description_
    """
    result = reallife.build_flexible(
        task=build_flexible_config.task,
        type=build_flexible_config.type,
        action=build_flexible_config.action
    )
    return {"message": result}

@app.post("/tips")
async def tips(task_request:TaskRequest):
    """_summary_

    Args:
        task_request (TaskRequest): _description_

    Returns:
        _type_: _description_
    """
    task = task_request.task
    reallife.tips(task)
    return {"message": '以添加'}

@app.get("/receive")
async def query_the_current_task():
    """_summary_

    Returns:
        _type_: _description_
    """
    result = reallife.query_the_current_task()
    # return {"message": result}
    if result[1] == "!":
        messages = result.split(' ',1)
        if len(messages) == 1:
            return {"message": messages[0]}
        else:
            return {"message":messages[1]}
    else:
        return {"message": result}


@app.get("/start")
async def start():
    """_summary_

    Returns:
        _type_: _description_
    """
    result = reallife.start()
    # return {"message": result}
    if result[1] == "!":
        messages = result.split(' ',1)
        if len(messages) == 1:
            return {"message": messages[0]}
        else:
            return {"message":messages[1]}
    else:
        return {"message": result}

@app.get("/close")
async def close():
    """_summary_

    Returns:
        _type_: _description_
    """
    result = reallife.close()
    return {"message": result}

@app.get("/run")
async def run():
    """_summary_

    Returns:
        _type_: _description_
    """
    result = reallife.run()
    return {"message": result}
    



if __name__ == "__main__":
    import argparse
    import uvicorn
    from .log import Log

    parser = argparse.ArgumentParser(
        description="Start a simple HTTP server similar to http.server."
    )
    parser.add_argument(
        'port',
        metavar='PORT',
        type=int,
        nargs='?',  # 端口是可选的
        default=8021,
        help='Specify alternate port [default: 8000]'
    )
    # 创建一个互斥组用于环境选择
    group = parser.add_mutually_exclusive_group()

    # 添加 --dev 选项
    group.add_argument(
        '--dev',
        action='store_true', # 当存在 --dev 时，该值为 True
        help='Run in development mode (default).'
    )

    # 添加 --prod 选项
    group.add_argument(
        '--prod',
        action='store_true', # 当存在 --prod 时，该值为 True
        help='Run in production mode.'
    )

    # parser.add_argument(
    #     '--env',
    #     type=str,
    #     default='dev', # 默认是开发环境
    #     choices=['dev', 'prod'],
    #     help='Set the environment (dev or prod) [default: dev]'
    # )

    args = parser.parse_args()


    if args.prod:
        env = "prod"
    else:
        # 如果 --prod 不存在，默认就是 dev
        env = "dev"


    reload = False # 默认不热重载

    port = args.port
    if env == "dev":
        port += 100
        Log.reset_level('debug',env = env)
        reload = True
        app_import_string = "src.reallife_client_mac.server:app" # <--- 关键修改：传递导入字符串
    elif env == "prod":
        Log.reset_level('info',env = env)# ['debug', 'info', 'warning', 'error', 'critical']
        reload = False
        app_import_string = app
    else:
        reload = False
        app_import_string = app

    uvicorn.run(
        # app, # 要加载的应用，格式是 "module_name:variable_name"
        app_import_string,
        host="0.0.0.0",
        port=port,
        reload=reload  # 启用热重载
    )
