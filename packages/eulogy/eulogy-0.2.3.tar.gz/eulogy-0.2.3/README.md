# Introduction
A number of platforms, typically related to Data Science and its friends, automatically pipe _everything_ (`stdout`, `stderr`, build commands of containers, Java messages in the case of, e.g. Spark) into a single file. This can make it difficult to find debugging information for your program, where custom `print()` messages are scattered throughout a _lot_ of noise.

That's the issue that `eulogy` aims to alleviate. Unlike traditional `logging`, it stores a history of messages, function calls and tracebacks that will only be reported via `stdout` **right at the point that the program crashes**. This means that, regardless of all the other information being dumped into the log file that you can't control, you will receive an uninterrupted/consolidated report of whatever you chose to trace, right at the end of the log file. You just need to look for the recital right at the end (RIP program). It is therefore not a replacement for traditional logging but, rather, a debugging aid.

# Usage

## Unhandled Exceptions
```python
from eulogy import eulogy, eulogise

@eulogise() # Note the brackets here
def some_func():
    int("a")

# Add a custom message to the eulogy
eulogy.add("This seems like fun")

if __name__ == "__main__":
    some_func()
```

That gives:
```python
Traceback (most recent call last):
  File "<path>/delete_me.py", line 11, in <module>
    some_func()
  File "<path>/eulogy/src/eulogy/__init__.py", line 26, in add_function_log
    return func(*args, **kwargs)
  File "<path>/eulogy/delete_me.py", line 5, in some_func
    a = int("a")
ValueError: invalid literal for int() with base 10: 'a'

--- RECITAL ---
[2025-07-05 11:01:21.995427+00:00] This seems like fun
[2025-07-05 11:01:21.995578+00:00] Function: __main__.some_func
```

## Handled Exceptions
```python
from eulogy import eulogy, eulogise

@eulogise()
def some_func():
    try:
        int("a")
    except(ValueError):
        pass

eulogy.add("This seems like fun")

if __name__ == "__main__":
    some_func()
```
This gives no output because there is nothing to report; nothing crashed. But what if we wanted to see the report anyway? You can force a printout of the eulogy contents at any time. Forcing the output does **not** clear the eulogy deque so it won't affect the output on an actual crash later on.
```python
if __name__ == "__main__":
    some_func()
    eulogy.recite(force=True)
```

## Tracking Handled Exceptions
What if you wanted to know whether the code handled an exception, even if it didn't crash the program?
```python
from eulogy import eulogy, eulogise

@eulogise()
def some_func():
    try:
        int("a")
    except(ValueError):
        eulogy.add_tb() # Add the traceback to the eulogy and move on

@eulogise()
def other_func():
    int("b")

eulogy.add("This seems like fun")

if __name__ == "__main__":
    some_func() # This will still work
    eulogy.add("Still looks good")
    other_func() # Crash the program and trigger the recital
```

## Further Configuration
There is a config object for fine-tuning reporting if it's needed for your output. It can be used to turn off certain recorded events. Creating the config with its default params is demonstrated below.

```python
from eulogy import eulogy
from eulogy.config import Config

config = Config(
    max_report_length=50,
    ignore_functions=False,
    ignore_manual=False,
    ignore_tracebacks=False
)

eulogy.set_config(config)
```
It is possible to turn off reporting in any portion of the program by re-defining config and then set it back on later. You can use `.set_config()` as many times as desired throughout the program. The `max_report_length` is implemented as a queue to report the last `n` number of events, which by default is 50, to not consume inordinate amounts of memory in cases where there might be tight loops or very stable programs accumulating reported events indefinitely. However, you can set this to `None` to create an infinitely expanding record.

## Tags
In case multiple runs are merged into a single log file, you can mark function calls with custom messages for easier searching. So, for example:
```python
from eulogy import eulogise

@eulogise(tags=["Run 1", "Meaning of life"])
def some_func():
    return 42

some_func()
# Crash the program
int("a")
```

## Contributing
The project is currently in Beta and all contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome. This is a project that is hard to test across platforms that require paid access, which I don't currently have and indeed some are proprietary platforms for individual companies.