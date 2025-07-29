# Bitfrog Python API
*A Python API for easy push notifications through Bitfrog.*

**IMPORTANT**: Bitfrog has not been released yet, this package will not be useful until it has.

## Installation
```
pip install bitfrog
```

## Usage

```python
import bitfrog

bitfrog.notify("WOW so concise!", "XXXX-XXXX-XXXX-XXXX")
```

Or if you have many notifications and don't want to repeat the token;

```python
project = bitfrog.Project("XXXX-XXXX-XXXX-XXXX")
project.notify("Hello project!")

# Specify custom channel
channel = project.channel("Test Channel")
channel.notify("Finger lickin' good")
```