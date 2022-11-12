from kafka import KafkaConsumer

partition_spread = [0, 0, 0]
while True:
    consumer = KafkaConsumer(bootstrap_servers='localhost:9092',group_id='p3consumer',auto_offset_reset='latest')
    consumer.subscribe(['problem3'])

    for message in consumer:
        print(f"offset={message.offset}, partition={message.partition}, key={message.key}, value={message.value}")
        partition_spread[message.partition] += 1
        print("Partition spread:", partition_spread)
