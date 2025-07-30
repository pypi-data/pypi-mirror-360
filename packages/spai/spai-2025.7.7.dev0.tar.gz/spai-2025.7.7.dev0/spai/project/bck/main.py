from ..get_services import GetServices
from .StopService import StopService
from .RunService import RunService
from .ScheduleService import ScheduleService
from .GetLogs import GetLogs
from ..install_requirements import InstallReqs

from ...repos import APIRepo


def install_reqs(config, logger):
    install = InstallReqs()
    inputs = install.Inputs(config=config, logger=logger)
    outputs = install(inputs)
    return outputs.message


def get_services(user, project):
    repo = APIRepo()
    services = GetServices(repo)
    inputs = services.Inputs(user=user, project=project)
    outputs = services(inputs)
    return outputs.services


def stop_service(user, project, service, name):
    repo = APIRepo()
    stop = StopService(repo)
    inputs = stop.Inputs(user=user, project=project, service=service, name=name)
    outputs = stop(inputs)
    return outputs.message


def run_service(user, service, files, data):
    repo = APIRepo()
    run = RunService(repo)
    inputs = run.Inputs(user=user, service=service, files=files, data=data)
    outputs = run(inputs)
    return outputs.message


def schedule_service(user, service, files, data):
    repo = APIRepo()
    schedule = ScheduleService(repo)
    inputs = schedule.Inputs(user=user, service=service, files=files, data=data)
    outputs = schedule(inputs)
    return outputs.message


def get_logs(user, project, service, name):
    repo = APIRepo()
    logs = GetLogs(repo)
    inputs = logs.Inputs(user=user, project=project, service=service, name=name)
    outputs = logs(inputs)
    return outputs.logs
