Create a Node and spin it without blocking.

Usually:
```python
import rclpy
from rclpy.node import Node
from threading import Thread

node = Node("robot", namespace="MK14QWZ024480005")
Thread(target=rclpy.spin, args=(node,), daemon=True).start()
```

Now:
```python
```

Create a publisher which publishes a message every 100ms.

Usually:
```python
msg = String()
publisher = node.create_publisher(String, "topic", 10)
timer = node.create_timer(0.1, lambda: publisher.publish(msg))
# update the message
msg.data = "Hello, world!"
```

Now:
```python
```

Wait for a message to be subscribed.

Usually:
```python
message = String()
def callback(msg):
    message.data = msg.data
subscriber = node.create_subscription(String, "topic", callback, 10)
while not message.data:
    rclpy.spin_once(node)
```

Now:
```python
```

The above comparison is just a simple example. For more complex examples, please read the following tutorial.
