import inspect
import importlib
import json
import bomiot_token

from os.path import join
from datetime import datetime, date
from configparser import ConfigParser
from django.dispatch import receiver
from django.db import transaction
from django.conf import settings
from bomiot.cmd import create_key
from bomiot.server.core.signal import bomiot_signals, bomiot_data_signals
from bomiot.server.core.utils import receiver_callback, receiver_file_callback, receiver_server_callback
from bomiot.server.core.utils import sync_write_file
from bomiot.server.core.models import API
from bomiot.server.core.models import JobList
# from bomiot.server.core.watch import core_watch


def calculate_days_difference(expire_timestamp):
    try:
        expire_date = datetime.fromtimestamp(expire_timestamp).date()
        today = date.today()
        days_difference = (expire_date - today).days
        return days_difference
    except Exception as e:
        return None

def init():
    """
    Initialize the module by importing necessary modules and setting up signal receivers.
    """
    key = settings.KEY
    if (key == ''):
        key = create_key.auth_key_force()
    mac, expire_time = bomiot_token.verify_info(key)
    days_diff = calculate_days_difference(int(expire_time))
    if days_diff is not None:
        if days_diff <= 0:
            edit_setup = False
            CONFIG = ConfigParser()
            setup_ini_path = join(settings.WORKING_SPACE, 'setup.ini')
            CONFIG.read(setup_ini_path, encoding='utf-8')
            if CONFIG.get('database', 'name') != "sqlite":
                CONFIG.set('database', 'name', 'sqlite')
                edit_setup = True
            if CONFIG.getint('file', 'file_size') != 102400:
                CONFIG.set('file', 'file_size', str(102400))
                edit_setup = True
            if CONFIG.get('file', 'file_extension') != 'py,png,jpg,jpeg,gif,bmp,webp,txt,md,html,htm,js,css,json,xml,csv,xlsx,xls,ppt,pptx,doc,docx,pdf':
                CONFIG.set('file', 'file_extension', 'py,png,jpg,jpeg,gif,bmp,webp,txt,md,html,htm,js,css,json,xml,csv,xlsx,xls,ppt,pptx,doc,docx,pdf')
                edit_setup = True
            if edit_setup is True:
                CONFIG.write(open(join(settings.WORKING_SPACE, 'setup.ini'), "wt"))
            # core_watch.start()
        elif days_diff > 0 and days_diff < 30:
            print(f"Keys will expires in {days_diff} days")

@receiver(bomiot_data_signals)
def data_callback(**kwargs):
    """
    Signal receiver to handle the received signal
    """
    path = kwargs.get('request').path
    api_obj = API.objects.filter(api=path).first()
    if api_obj is None:
        return None
    value = api_obj.func_name
    feedback = receiver_callback(kwargs, value)
    return feedback

@receiver(bomiot_signals)
def server_callback(sender, **kwargs):
    """
    Signal receiver to handle server signal
    """
    data = kwargs.get('msg')
    if data.get('models') == 'Pids':
        receiver_server_callback(data.get('data'), 'pid_get')
    elif data.get('models') == 'Network':
        receiver_server_callback(data.get('data'), 'network_get')
    elif data.get('models') == 'Disk':
        receiver_server_callback(data.get('data'), 'disk_get')
    elif data.get('models') == 'Memory':
        receiver_server_callback(data.get('data'), 'memory_get')
    elif data.get('models') == 'CPU':
        receiver_server_callback(data.get('data'), 'cpu_get')
    elif data.get('models') == 'Files':
        receiver_file_callback(data.get('data'), 'file_get')
    elif data.get('models', '') == 'Function':
        if sender == sync_write_file:
            sync_write_file(
                kwargs.get('file_path'),
                kwargs.get('file_data')
            )
        else:
            job_func = importlib.import_module(f'{sender.__module__}')
            job_function = getattr(job_func, sender.__name__)
            sig = inspect.signature(job_function)
            if sig.parameters:
                func_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
                job_function(**func_kwargs)
            else:
                job_function()
    elif data.get('models', '') == 'JobList':
        job_data = data.get('data', {})
        job_id = f"{inspect.getmodule(sender).__name__}-{sender.__name__}-{str(job_data)}"
        with transaction.atomic():
            job, created = JobList.objects.get_or_create(
                job_id=job_id,
                defaults={
                    'module_name': inspect.getmodule(sender).__name__,
                    'func_name': sender.__name__,
                    'trigger': job_data.get('trigger'),
                    'description': job_data.get('description', ''),
                    'configuration': json.dumps(job_data)
                }
            )
            if not created:
                job.trigger = job_data.get('trigger')
                job.description = job_data.get('description', '')
                job.configuration = json.dumps(job_data)
                job.save()
    else:
        return
    return