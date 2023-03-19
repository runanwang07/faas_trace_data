
from locust import HttpUser, TaskSet, task, stats, between
from random import randint, expovariate, choice
import time
import random
from locust.exception import StopUser
stats.CSV_STATS_INTERVAL_SEC = 1

url = "resize"


class WebTasks(HttpUser):
    @task
    def big(self):
        with open('image_url.txt') as f:
            lines = f.readlines()
        rint = randint(0, len(lines)-1)
        img_url = lines[rint].rstrip('\n')
        single_f = self.client.post(url, data=img_url, name=img_url)
        time.sleep(expovariate(1))
