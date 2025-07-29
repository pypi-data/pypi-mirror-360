from heros import LocalHERO, event

import random
import time
import argparse

random.seed()

class Dummy(LocalHERO):

    testme: int = 0

    def hello(self) -> str:
        self.testme += 1
        return "world"

objs = []

for i in range(100):
    objs.append(Dummy(f"test{i}"))

# keep running
while True:
    time.sleep(1)