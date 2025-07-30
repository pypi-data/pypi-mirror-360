# aceparse

An argument parser that wraps python's built-in `argparse`, allowing it to parse command lines into
dataclasses.

Advantages over argparse:

* you get a dataclass so you can use an IDE to find out where your command line options are used
* nicer specification of default values
* can be combined with pydantic dataclasses to type check arguments

## Examples

```python
from dataclasses import dataclass
from aceparse import AceParser, AceArg

@dataclass
class Arguments:
    hello: str = AceArg(help="Name of thing to say hello to")

a = AceParser(Arguments)
args = a.parse_args_into_dataclasses(["--hello=name"])

print(f"Hello {args.hello}")
```
