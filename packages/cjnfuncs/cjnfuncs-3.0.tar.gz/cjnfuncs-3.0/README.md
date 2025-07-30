# cjnfuncs - A framework and collection of utility functions for script writing

## cjnfuncs is comprised of several modules (follow links to respective documentation)

NOTE:  Since relative links to other .md files do not work on PyPI, please go to the [cjnfuncs GitHub repo](https://github.com/cjnaz/cjnfuncs) to read the documentation. 

module | Description/Purpose
--|--
[core](core.md)                   | Set up the base environment
[configman](configman.md)         | Feature-rich configuration file toolset
[timevalue](timevalue.md)         | Handle time values with units, such as '5m' (5 minutes), and schedule future operations
[mungePath](mungePath.md)         | Ease-of-use pathlib extension for constructing and manipulating file paths
[rwt / run_with_timeout](rwt.md)  | Execute any function with an enforced timeout
[deployfiles](deployfiles.md)     | Push bundled setup files within a package to the proper user/system locations
[resourcelock](resourcelock.md)   | Inter-process resource lock mechanism
[SMTP](SMTP.md)                   | Send notification and email messages

Developed and tested on Python 3.9.21 and supported on all higher Python versions.
Developed on Linux.  Not supported on Windows (posix-ipc module dependency).

In this documentation, "tool script" refers to a Python project that imports and uses cjnfuncs. Some may be simple scripts, and others may themselves be installed packages.

<br/>

## Installation and usage

```
pip install cjnfuncs
```

A package template using cjnfuncs is available at https://github.com/cjnaz/tool_template, which 
is the basis of PyPI posted tools such as:
  - [lanmonitor](https://pypi.org/project/lanmonitor/)
  - [wanstatus](https://pypi.org/project/wanstatus/)
  - [routermonitor](https://pypi.org/project/routermonitor/)

Project repo:  https://github.com/cjnaz/cjnfuncs

<br/>

## Key changes since the prior major public release (version 2.5)

`run_with_timeout()` (see module `rwt`)
- If a network share (or an internet resource) is 
unavailable or extremely slow then the tool script can hang indefinitely.  `run_with_timeout()` can wrap any function call
(any callable - built-in, standard library, installed package, or defined within the tool script) with an enforced timeout
and number of retries on timeout so that your code can make rational decisions when there are access issues.

`set / restore_logging_level()` on a stack  (see module `core`)
- When you want this, you want this.  Its used in configman, for instance, to allow for debug logging within the configman code (valuable for cjnfuncs debug and regression testing).  If you are developing a hardware sensor driver for example, you can enable debug logging of calls to your driver code
and restore the level before return.
You can use `set_logging_level()` standalone, or with later `restore_logging_level()` calls.  

`periodic_log()` (see module `core`)
- `periodic_log()` solves the difficulty of finding the sweet spot of how much logging to do to avoiding flooding the log.  You can say "log this event only once every 10 minutes", for example.  So even if the log event gets triggered every 100 ms, no problem.  

`get_next_dt()` (see module `timevalue`)
- A lot of what I develop are process monitoring tools.  These typically implement a `while True` loop where various operations get triggered periodically on their own schedules.  `get_next_dt()` provides a simple and clean way to get the next `datetime` to do an operation (in my usage, as defined in a config file).  `get_next_dt()` supports arbitrary times of day and days of week.  For example, trigger generating a summary report every Thursday at 9AM:

      if now_dt > generate_summary_dt:    # I suffix datetimes with '_dt' for readability
        gen_summary()
        generate_summary_dt = get_next_dt('9:00, 'Thursday')

`mungePath(..., set_attributes=False)` switch
- On network outages, my apps would slow to a crawl.  The root of the issue was in checking if a network file exists, with no timeout mechanism. The pathlib `.exists()`, `.is_dir()`, and `is_file()` methods are all susceptible to indefinate hangs.  The set_attributues switch has been added to mungePath, with a default value of False.  _Note that this is a change to default behavior._  If set True then `refresh_stats()` is called (or you can call it directly yourself, as needed).  `refresh_stats()` and `check_file_exists()` have been rewritten to utilize `run_with_timeout()`, with a default timeout of 1.0 seconds. I then `periodic_log()` the access problem. Ah, so much more stable.

<br/>

## Revision history
- 3.0 250705 - Added run_with_timeout, set / restore_logging_level, periodic_logging, get_next_dt.  Functional change to mungePath.
- 2.5 250206 - Added multi-line and quoted string support to configman
- 2.4.1 241118 - resource_lock only init lock_info if not existing
- 2.4 241105 - Twilio support in snd_notif, resource_lock trace/debug features, check_path_exists exception fix
- 2.3 240821 - Added mungePath ./ support.
  Resolved check_path_exists() memory leak.
  Added `same_process_ok` to resourcelock.getlock()
  Added prereload_callback to config_item.loadconfig()
- 2.2 240119 - Added SMTP DKIM support.  Set SMTP server connect timeout to EmailRetryWait.
- 2.1 240104 - Partitioned to separate modules.
  Added modify_configfile. 
  Added native support for float, list, tuple, and dict in loadconfig(). 
  Added getcfg() type checking. 
  Documentation touch for logging formats in config file. 
  Improved snd_notif failure logging. 
  Added email/notif send retries.
  Added resourcelock module.
- 2.0.1 230222 - deploy_files() fix for files from package
- 2.0 230208 - Refactored and converted to installed package.  Renamed funcs3 to cjnfuncs.
- ...
- 0.1 180524 - New.  First github posting