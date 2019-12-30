# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import RealTimeQps, RunningInsSentinel, RunningInsStandalone, RunningInsCluster
import os
# pyecharts
from jinja2 import Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig
from django.http import HttpResponse
from pyecharts import options as opts
from pyecharts.charts import Line
HTML_TEM_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CurrentConfig.GLOBAL_ENV = Environment(loader=FileSystemLoader("{0}/polls/static".format(HTML_TEM_DIR)))
# Create your views here.


# echarts
def redis_qps(request, redis_type, ins_id, redis_ip, redis_port):
    real_time_qps = RealTimeQps.objects.all()
    if redis_type == 'sentinel':
        running_ins_time = RunningInsSentinel.objects.all()
    elif redis_type == 'standalone':
        running_ins_time = RunningInsStandalone.objects.all()
    elif redis_type == 'cluster':
        running_ins_time = RunningInsCluster.objects.all()
    real_time_obj = real_time_qps.filter(redis_running_monitor_id=ins_id, redis_ip=redis_ip, redis_port=redis_port).order_by('-collect_date')[:60]
    running_ins = running_ins_time.filter(redis_ip=redis_ip, running_ins_port=redis_port)
    running_ins_name = running_ins.values('running_ins_name').first()
    # running_ins_ip = running_ins.values('redis_ip').first()
    # running_ins_port = running_ins.values('running_ins_port').first()
    real_time = [real_time.__dict__['collect_date'] for real_time in real_time_obj]
    redis_qps = [redis_qps.__dict__['redis_qps'] for redis_qps in real_time_obj]
    c = (
        Line()
        .add_xaxis(real_time)
        .add_yaxis(running_ins_name['running_ins_name'], redis_qps, is_smooth=True)
        .set_global_opts(title_opts=opts.TitleOpts(title="{0}:{1}".format(redis_ip,
                                                                          redis_port),
                                                   subtitle="Redis QPS图"),
                         toolbox_opts=opts.ToolboxOpts(),
                         datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],)
    )
    return HttpResponse(c.render_embed())


def favicon(request):
    img = "static/favicon.ico"
    image_date = open(img, "rb").read()
    return HttpResponse(image_date, content_type='image/jpg')

