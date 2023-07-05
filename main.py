#!/usr/bin/env python3
import time
from datetime import datetime
from nicegui import ui, app
import os
from ping3 import ping, verbose_ping


if 'PINGER_IPS' not in os.environ:
  print('define PINGER_IPS > 1.1.1.1,8.8.8.8')
  quit()

ips = os.getenv('PINGER_IPS').split(',')

maxTimeSec = 600
pingAlertLimitMs = 100
maxPingResponseTimeS = 0.3
chartRefreshS = 1
chart = []
pingTimer = []
pingIntervalS = 1

for ip in ips:
  chart.append(ui.chart({'title': { 'text': ip},
                  'chart': { 'type': 'area', 'zoomType': 'x' },
                  'xAxis': { 'type': 'datetime' },
                  'yAxis': { 'title': {'text':'ms'}},
                  'time': { 'timezoneOffset': 7200},
                  'legend': { 'enabled': False },
                  'series': [{'name' : ip, 'data': [], 'color': '#32a84c'}],
                  }
                  ).classes('w-full h-64'))

log = ui.log(max_lines=30).classes('w-full h-96 bg-black text-white')

def clear():
    i = -1

    for ip in ips:
      i+= 1
      chart[i].options['series'][0]['data'].clear()

    log.clear()
    log.push("Auto refresh time: " + str(chartRefreshS) + "sec")

ui.button('Clear all', on_click=clear)

def ping_internal(i):
    global ips, conn, c, maxTimeSec, maxResponseTimeMs
    ip = ips[i]

    response_time = ping(ip, timeout=maxPingResponseTimeS, unit='ms')
    if response_time is None:
      print(datetime.now().strftime('%H:%M:%S') + " no ping reply from " + ip)
      log.push(datetime.now().strftime('%H:%M:%S') + " no ping reply from " + ip)
      ui.notify(datetime.now().strftime('%H:%M:%S') + " no ping reply from " + ip, type='negative')

      chart[i].options['series'][0]['data'].append({'x': int(time.time()*1000), 'y': 0, 'marker': { 'radius': 3, 'fillColor': '#eb0909' }})

    else:
      chart[i].options['series'][0]['data'].append({'x': int(time.time()*1000), 'y': round(response_time,2), 'marker': { 'radius': 0 }})

      if len(chart[i].options['series'][0]['data']) > maxTimeSec:
        chart[i].options['series'][0]['data'].pop(0)

      if response_time > pingAlertLimitMs:
        log.push(datetime.now().strftime('%H:%M:%S') + " high ping reply time from " + ip + " > " + str(response_time) + " ms")


def updateCharts():
    global ips, conn, c, maxTimeSec, maxResponseTimeMs
    i = -1

    for ip in ips:
      i+= 1
      chart[i].update()


i = -1
for ip in ips:
    i += 1
    pingTimer.append(ui.timer(pingIntervalS, lambda iter=i: ping_internal(iter)))

# ui.timer(round(len(ips)*maxPingResponseTimeS+1), lambda: ping_internals())
chartTimer = ui.timer(chartRefreshS, lambda: updateCharts())

log.push("Auto refresh time: " + str(chartRefreshS) + "sec")
ui.run(title="pinger", show="False", favicon="📶")
