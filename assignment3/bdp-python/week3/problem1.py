# Copyright (c) 2022 CSCIE88 Marina Popova

# Code adapted by Mason Choi in September of 2022 for CSCIE88
# {"2022-09-04:07": {"url1": [clicks, {user-01, user-02}], "url2": [{...}], ...}, ...}
# redis hash: python dictionary{string: list[string, set]}
"""
python problem1.py -f ../logs/file-input1.csv
python problem1.py -f ../logs/file-input2.csv
python problem1.py -f ../logs/file-input3.csv
python problem1.py -f ../logs/file-input4.csv
^C
"""

import argparse
from collections import namedtuple
import redis
import json

event_fields = ['uuid', 'timestamp', 'url', 'userid', 'country', 'ua_browser', 'ua_os', 'response_status', 'TTFB']
Event = namedtuple('Event', event_fields)


def parse_arguments():
    prog = "counter_process_redis"
    desc = "application that reads a file, parses all lines, counts the lines and " \
           "stores/increments the counter maintained in Redis"

    parser = argparse.ArgumentParser(prog=prog, description=desc)
    # name of a simple String field in Redis - that will be use as a shared counter
    parser.add_argument('--file_name', '-f', required=False, default="../logs/file-input1.csv",
                        help="a csv log file to process")
    parser.add_argument('--redis_url', '-ru', required=False, default="redis://localhost:6379",
                        help="Redis end point url; Eg: redis://localhost:6379")

    parsed_args = parser.parse_args()
    return parsed_args


def do_work(redis_url, file_name):
    redis_client = redis.Redis.from_url(redis_url)

    with open(file_name) as file_handle:
        events = map(parse_line, file_handle)

        for event in events:
            date_hour = event[1][:event[1].find(":")]
            date_hour = date_hour.replace("T", ":")  # parse datetime into date:hour form
            url = event[2]
            user = event[3]

            # aggregate relevant data into dict of dicts
            if redis_client.exists(date_hour):
                if bytes(url, encoding="utf-8") in redis_client.hgetall(date_hour):
                    old_url_value = redis_client.hget(date_hour, url)
                    old_url_value = json.loads(old_url_value)  # load stringified data
                    old_url_value[0] += 1
                    old_url_value[1].append(user)
                    old_url_value[1] = list(set(old_url_value[1]))
                    old_url_value = json.dumps(old_url_value)  # restringify
                    new_url_value = old_url_value
                    redis_client.hset(date_hour, url, new_url_value)  # update hm value
                else:
                    new_url_value = json.dumps([1, list(set([user]))])
                    redis_client.hset(date_hour, url, new_url_value)
            else:
                new_datehour_value = json.dumps([1, list(set([user]))])
                redis_client.hset(date_hour, url, new_datehour_value)

    redis_client.close()


def parse_line(line):
    return Event(*line.split(','))


def main():
    parsed_args = parse_arguments()
    file_name = parsed_args.file_name
    redis_url = parsed_args.redis_url
    do_work(redis_url, file_name)


if __name__ == '__main__':
    main()

