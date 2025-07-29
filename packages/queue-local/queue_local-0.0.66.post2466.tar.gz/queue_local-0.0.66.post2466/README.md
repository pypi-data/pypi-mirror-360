# queue-local-python-package

## Usage:

Install:

```bash
pip install queue-local
``` 

- It's recommended to add `queue-local` to your `requirements.txt` file if you're using it as part of your project
  dependencies.

### Using the `DatabaseQueue` Class:

```py
from queue_local.database_queue import DatabaseQueue

q = DatabaseQueue()  # you can also pass some parameters here, see the class definition for more info

# Push items into the queue
q.push({"item_description": "test 1", "action_id": 1, "parameters_json": "{'a': 1, 'b': 2}"})
q.push({"item_description": "test 2", "action_id": 2, "parameters_json": {'a': 1, 'b': 2}})

# Peek at the first item in the queue (without removing it)
result1 = q.peek()  # "test 1" is still in the queue

# Get an item from the queue (and remove it) based on action_id
result2 = q.get(action_ids=(2,))  # Gets "test 2" (the first item with action_id=2)

# Get an item from the queue (and remove it)
result3 = q.get()  # Gets "test 1"

q.close()  # close the database connection
```

### Inheriting from the Abstract `OurQueue` Class:

```py
from queue_local.our_queue import OurQueue


class YourCustomQueue(OurQueue):
    def __init__(self):
        pass

    def push(self, item):
        """Push an item to the queue"""
        pass

    def get(self):
        """Get an item from the queue (and delete)"""
        pass

    def peek(self):
        """Peek at the head of the queue (without deleting)"""
        pass
    # Add any additional functions you need, such as is_empty()
```