# Lewis' Lazy Logger
For when you're too lazy to setup loggers every time.

## How to use
* Install the logger package by running `pip install lewis-lazy-logger`
* Import into your logger file like so: `from lewis_lazy_logger import simple_logger_setup`
* You can then initialise your logger and pick which options you want to enable:
```python
logger = simple_logger_setup(
    level="info", (default = "debug")
    name="my_app", (default = None)
    use_rich=True, (default = False)
    log_to_file=True, (default = False)
    file_path="test.log", (default = "app.log")
    json_output=False, (default = False)
    max_bytes=10000, (default = 1000000)
    backup_count=5, (default = 3)
)
```

The available fields are:
* level: str - The log level you want to log (ie debug, info, etc)
* name: str - The name of your logger instance
* use_rich: bool - Make use of the Rich package for 'rich text and beautiful formatting in the terminal' (Overwrites json_output)
* log_to_file: bool - Write your logs to a log file
* file_path: str - The file path for your logs
* json_output: bool - Output logs in json format (Not usable with use_rich = True)
* max_bytes: int - The maximum file size of your log files
* backup_count: int - The number of backup log files allowed to be created

---

## Example Output

### use_rich = False
```log
[13:02:32] [ERROR] my_app: Division by zero!
Traceback (most recent call last):
  File "E:\Projects\LOGGER_TEST\main.py", line 19, in <module>
    1 / 0
    ~~^~~
ZeroDivisionError: division by zero
```

### use_rich = True
```log
[07/05/25 13:00:44] ERROR    Division by zero!                                           main.py:21
                             ╭─────────── Traceback (most recent call last) ───────────╮
                             │ E:\Projects\LOGGER_TEST\main.py:19 in <module>          │
                             │                                                         │
                             │   16 # logger.error("Oops, something went wrong!")      │
                             │   17                                                    │
                             │   18 try:                                               │
                             │ ❱ 19 │   1 / 0                                          │
                             │   20 except ZeroDivisionError:                          │
                             │   21 │   logger.exception("Division by zero!")          │
                             │   22                                                    │
                             ╰─────────────────────────────────────────────────────────╯
                             ZeroDivisionError: division by zero
```

### json_output = True
```log
{"time": "2025-07-05T13:02:59", "level": "ERROR", "logger": "my_app", "message": "Division by zero!", "exception": "Traceback (most recent call last):\n  File \"E:\\Projects\\LOGGER_TEST\\main.py\", line 19, in <module>\n    1 / 0\n    ~~^~~\nZeroDivisionError: division by zero"}
```
