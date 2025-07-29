# logprof - Simple logging profiler

Simple logging of timing and memory usage with decorator or context manager.


## Installation

```bash
pip install logprof
```

## Usage

Below is an example usage

```python
import logging
from logprof import logprof

logging.basicConfig(level="INFO")

# tf can be seconds (default) or "full"
@logprof("bar", tf="breakdown")
def function():
    print("The bit in the middle")

function()
# INFO:logprof:>>> 'bar' started..
# The bit in the middle
# INFO:logprof:<<< 'bar' finished. Took 15us 860ns

class Foo:
    @logprof("class func", tf="nanoseconds")
    def bar(self, x=1):
        print(f"bar got x = {x}")

Foo().bar()
# INFO:logprof:>>> 'class func' started..
# bar got x = 1
# INFO:logprof:<<< 'class func' finished. Took 15339ns

with logprof("foo", tf="breakdown", mf="breakdown"):
    from time import sleep
    sleep(1)
    x = [1] * 2**25  ## 256MB?
    x.append(1000)
    print("The bit in the middle")
# INFO:logprof:>>> 'foo' started..
# The bit in the middle
# INFO:logprof:<<< 'foo' finished. Took 1s 111ms 947us 614ns. Used 255mib 1004kib.
```

## Development

Before commit run following format commands in project folder:

```bash
nox --session do-lint
```
