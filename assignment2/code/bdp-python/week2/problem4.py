# Copyright (c) 2022 CSCIE88 Marina Popova

# Code adapted by Mason Choi in September of 2022 for CSCIE88
# query 3: {"2022-09-04:07": {"url1": 4, "url2": 1, "url3": 99}, ...}

import argparse
from datetime import date
import multiprocessing
from multiprocessing import Process, Value, Lock
from collections import namedtuple, defaultdict
from threading import local


prog = "event_counter_shared_ctypes_mem"
desc = "run specified number of threads - use shared event counter"
parser = argparse.ArgumentParser(prog=prog, description=desc)
parser.add_argument('--thread-count', '-tc', default=4, type=int)
parser.add_argument('--logs-directory', '-ld', required=False,
                    help="Directory where the log files 01-04 are stored. "
                         "If not supplied, this program assumes that all 4 log files"
                         " are directly in the present working directory.")

parsed_args = parser.parse_args()
thread_count = parsed_args.thread_count
logs_dir = parsed_args.logs_directory
Event = namedtuple('Event',
                   ['uuid', 'timestamp', 'url', 'userid', 'country', 'ua_browser', 'ua_os', 'response_status', 'TTFB'])

parsed_args = parser.parse_args()
thread_count = parsed_args.thread_count


def do_work(shared_results, lock, file_name):
    local_dict = {}  # initialize local data dict
    with open(file_name) as file_handle:
        events = map(parse_line, file_handle)

        for event in events:
            date_hour = event[1][:event[1].find(":")]
            date_hour = date_hour.replace("T", ":")  # parse datetime into date:hour form
            url = event[2]

            # aggregate relevant data into dict of dicts
            if date_hour in local_dict:
                if url in local_dict[date_hour]:
                    local_dict[date_hour][url] += 1
                else:
                    local_dict[date_hour][url] = 1
            else:
                local_dict[date_hour] = {url: 1}

        with lock:
            shared_results.append(local_dict.copy())  # append data to shared list

        print(file_name, "has finished processing")

def parse_line(line):
    return Event(*line.split(','))

if __name__ == '__main__':
    if logs_dir is None:
        opt_dir = "logs/"
    elif logs_dir.endswith("/"):
        opt_dir = logs_dir
    else:
        opt_dir = logs_dir + "/"
    with multiprocessing.Manager() as manager:
        # declare a shared list to record each file's dict
        shared_results = manager.list()
        lock = Lock()
        jobs = []
        for thread_id in range(thread_count):
            file_name = opt_dir + "file-input%s.csv" % str(thread_id + 1)
            t = multiprocessing.Process(
                target=do_work,
                args=(shared_results, lock, file_name))

            jobs.append(t)
            t.start()

        for curr_job in jobs:
            curr_job.join()

        print("Threads finished!")  # threads have finished
        final_dict = {}  # initialize final data structure
        # compile file data into final_dict
        for file_dict in shared_results:
            for date_hour in file_dict.keys():
                if date_hour in final_dict:
                    for url in file_dict[date_hour]:
                        if url in (final_dict[date_hour]):
                            final_dict[date_hour][url] += file_dict[date_hour][url]
                        else:
                            final_dict[date_hour][url] = file_dict[date_hour][url]
                else:
                    final_dict[date_hour] = file_dict[date_hour]
        
        # QUERY 3, PROBLEM 4.2
        for url_id in ["06", "07", "09", "10", "11"]:
            date_hour = "2022-09-05:06"
            url = f"http://example.com/?url=0{url_id}"
            print(f"{date_hour}, {url}, {final_dict[date_hour][url]}")
