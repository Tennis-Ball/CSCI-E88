import redis
import json


redis_client = redis.Redis.from_url("redis://localhost:6379")
date_times = ["2022-09-03:16", "2022-09-04:02", "2022-09-04:19", "2022-09-05:01", "2022-09-06:08"]
urls = ["http://example.com/?url=065", "http://example.com/?url=110", "http://example.com/?url=100", "http://example.com/?url=018", "http://example.com/?url=013"]

# query 1
for date_time in date_times:
    print(f"{date_time} {len(redis_client.hgetall(date_time))}")
print()

# query 2
for key in zip(date_times, urls):
    user_count = len(json.loads(redis_client.hget(key[0], key[1]))[1])
    print(f"{key[0]}:{key[1]}, {user_count}")
print()

# query 3
for key in zip(date_times, urls):
    event_count = json.loads(redis_client.hget(key[0], key[1]))[0]
    print(f"{key[0]}:{key[1]}, {event_count}")

redis_client.close()
