# Copyright (c) 2022 CSCIE88 Marina Popova

# Code adapted by Mason Choi in September of 2022 for CSCIE88
# {"2022-09-04:07": {"country": {url1, url2}, "country": {...}, ...}, ...}
# # redis hash: python dictionary{string: set}
"""
python problem2.py -tr 2022-09-04T02 2022-09-05T22 -f ../logs/file-input1.csv
python problem2.py -tr 2022-09-04T02 2022-09-05T22 -f ../logs/file-input2.csv
python problem2.py -tr 2022-09-04T02 2022-09-05T22 -f ../logs/file-input3.csv
python problem2.py -tr 2022-09-04T02 2022-09-05T22 -f ../logs/file-input4.csv
^C
"""

import argparse
from collections import namedtuple
import redis
import json
from dateutil.parser import parse

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
    parser.add_argument('--time-range', '-tr', required=True, type=str, nargs=2, 
                    help="Time range for query, in form YEAR-MONTH-DAYTHOUR. Inclusive.")
    parser.add_argument('--redis_url', '-ru', required=False, default="redis://localhost:6379",
                        help="Redis end point url; Eg: redis://localhost:6379")

    parsed_args = parser.parse_args()
    return parsed_args


def do_work(redis_url, file_name, time_range):
    redis_client = redis.Redis.from_url(redis_url)

    with open(file_name) as file_handle:
        events = map(parse_line, file_handle)

        #######
        # print(redis_client.hget("2022-09-04:03", "KI"))
        # print(redis_client.hget("2022-09-04:10", "DJ"))
        # print(redis_client.hget("2022-09-05:01", "AS"))
        # print(redis_client.hget("2022-09-05:16", "CH"))
        # print(redis_client.hget("2022-09-05:20", "VE"))
        # redis_client.close()
        # quit()
        #######

        for event in events:
            date_hour = event[1][:event[1].find(":")]
            # check if time is within specified range
            if parse(date_hour) >= time_range[0] and parse(date_hour) <= time_range[1]:
                date_hour = date_hour.replace("T", ":")  # parse datetime into date:hour form
                country = event[4]
                url = event[2]

                # aggregate relevant data into dict of dicts
                if redis_client.exists(date_hour):
                    if bytes(country, encoding="utf-8") in redis_client.hgetall(date_hour):
                        old_country_value = redis_client.hget(date_hour, country)
                        old_country_value = json.loads(old_country_value)  # load stringified data
                        old_country_value.append(url)
                        old_country_value = json.dumps(list(set(old_country_value)))  # restringify & dedup
                        new_country_value = old_country_value
                        redis_client.hset(date_hour, country, new_country_value)  # update hm value
                    else:
                        new_country_value = json.dumps([url])
                        redis_client.hset(date_hour, country, new_country_value)
                else:
                    new_datehour_value = json.dumps([url])
                    redis_client.hset(date_hour, country, new_datehour_value)

    redis_client.close()


def parse_line(line):
    return Event(*line.split(','))


def main():
    parsed_args = parse_arguments()
    file_name = parsed_args.file_name
    redis_url = parsed_args.redis_url
    time_range = [parse(parsed_args.time_range[0]), parse(parsed_args.time_range[1])]
    do_work(redis_url, file_name, time_range)


if __name__ == '__main__':
    main()

