from kafka import KafkaProducer
import time
import datetime
import uuid as id

producer = KafkaProducer(bootstrap_servers='localhost:9092')

while True:
    uuid = str(id.uuid4())
    timestamp = str(datetime.datetime.utcnow())
    userID = "Choi_Mason"

    producer.send("problem3", value=str.encode(f"{uuid}, {timestamp}, {userID}"))
    print(f"{uuid}, {timestamp}, {userID}")
    time.sleep(1)
