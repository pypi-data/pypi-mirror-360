import threading
from random import randint
from time import sleep

from ecmind_blue_client.client import Job
from ecmind_blue_client.tcp_pool_client import TcpPoolClient

client = TcpPoolClient(
    "localhost:4001:1#127.0.0.1:4000:1#10.0.2.15:4000:1",
    "TestClient",
    "root",
    "optimal",
    True,
)


def thread_function(_name):
    for _ in range(0, 100):
        sleep(randint(0, 1) / 10)
        test_job = Job("krn.CheckServerConnection", Flags=0)
        result = client.execute(test_job)
        print(result.values)


threads = list()
for i in range(0, 10):
    x = threading.Thread(target=thread_function, args=(i,))
    threads.append(x)
    x.start()

for index, thread in enumerate(threads):
    thread.join()
