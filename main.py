#!/usr/bin/env python
# -*- coding: utf-8 -*-


import threading
import traceback
import signal
import daemon
import atexit
import os

import time

from models.initialize import logger, threads_status, config
from models.event_process import EventProcess
from models.event_loop import vir_event_loop_poll_register, vir_event_loop_poll_run
from models import Host
from models import Utils
from models import PidFile


__author__ = 'James Iter'
__date__ = '2017/3/12'
__contact__ = 'james.iter.cn@gmail.com'
__copyright__ = '(c) 2017 by James Iter.'


def main():
    pidfile = PidFile(file_name=config['pidfile'])
    pidfile.create(pid=os.getpid())
    atexit.register(pidfile.unlink)

    threads = []

    signal.signal(signal.SIGTERM, Utils.signal_handle)
    signal.signal(signal.SIGINT, Utils.signal_handle)

    host_use_for_guest_creating_progress_report_engine = Host()
    t_ = threading.Thread(
        target=host_use_for_guest_creating_progress_report_engine.guest_creating_progress_report_engine, args=())
    threads.append(t_)

#     host_use_for_guest_booting2running_report_engine = Host()
#     t_ = threading.Thread(
#         target=host_use_for_guest_booting2running_report_engine.guest_booting2running_report_engine, args=())
#     threads.append(t_)

    host_use_for_instruction_process_engine = Host()
    t_ = threading.Thread(target=host_use_for_instruction_process_engine.instruction_process_engine, args=())
    threads.append(t_)

    host_use_for_host_state_report_engine = Host()
    t_ = threading.Thread(target=host_use_for_host_state_report_engine.host_state_report_engine, args=())
    threads.append(t_)

    host_use_for_guest_performance_collection_engine = Host()
    t_ = threading.Thread(
        target=host_use_for_guest_performance_collection_engine.guest_performance_collection_engine,
        args=())
    threads.append(t_)

    host_use_for_host_performance_collection_engine = Host()
    t_ = threading.Thread(
        target=
        host_use_for_host_performance_collection_engine.host_performance_collection_engine,
        args=())
    threads.append(t_)

    vir_event_loop_poll_register()
    t_ = threading.Thread(target=vir_event_loop_poll_run, name="libvirtEventLoop")
    threads.append(t_)

    host_use_for_refresh_guest_state = Host()
    host_use_for_refresh_guest_state.refresh_guest_state()

    for t in threads:
        t.setDaemon(True)
        t.start()

    EventProcess.guest_event_register()

    while True:
        if Utils.exit_flag:
            # 主线程即将结束
            EventProcess.guest_event_deregister()
            break

        if config['DEBUG']:
            print threads_status

        time.sleep(1)

    # 等待子线程结束
    for t in threads:
        t.join()

    msg = 'Main say bye-bye!'
    print msg
    logger.info(msg=msg)


if __name__ == '__main__':

    # noinspection PyBroadException
    try:

        if config['daemon']:
            with daemon.DaemonContext(files_preserve=[logger.handlers[0].stream.fileno()]):
                main()

        else:
            main()

    except:
        logger.error(traceback.format_exc())
        exit(-1)

