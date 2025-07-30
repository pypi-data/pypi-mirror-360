# ark-framework

`ark-framework` provides a simple asynchronous task decorator that allows lightweight parallelism using Python threads. It includes support for thread pools, named task queues, and graceful task completion.

## Features

- `@asynco`: Decorator to run any function in a separate thread or pool
- `Asynco`: Singleton manager for custom thread pools

## Usage

```python
from ark import asynco, Asynco

@asynco(pool_name="my_pool")
def background_task(x):
    print(f"Running task {x}")

Asynco.create_pool("my_pool", size=5)

for i in range(10):
    background_task(i)

Asynco.complete_all_task("my_pool")
