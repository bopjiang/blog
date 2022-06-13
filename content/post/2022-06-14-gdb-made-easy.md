---
title: "GDB made easy"
date: 2022-06-14T07:14:54+08:00
draft: false
---

## [gdbgui](https://www.gdbgui.com/)

Pros:
* can debug from remote Web UI

Cons
* can not copy/paste in the terminal of Web UI

install

```
pip install gdbgui
pip install werkzeug==2.0.0
```

run
```bash
gdbgui -r --host 0.0.0.0 -g "sudo gdb -p $(pgrep mysqld-debug) -x ./gdb.init"
```

open

[http://host_ip:5000/](http://127.0.0.1:5000)

## [GDB dashboard](https://github.com/cyrus-and/gdb-dashboard)
Pros:
* clean terminal GUI

Just a gdb init file with Python script.
Remember append config file in `/root/.gdbinit` if we use gdb to attach a process.

## VSCode + GDB
Pros:
* integation with IDE, nice experiment when debugging step by step(Just like VisualStudio).
* still can use gdb command directly.
* remote debug (TBC).

Cons:
- [ ] must append `-exec` perfix for each command in `debug console`
- [ ] must input password even with sudo when attaching
- [ ] breakpoints in UI not synced with the ones created in debug console


Install

need install an extension first [https://marketplace.visualstudio.com/items?itemName=rioj7.command-variable](https://marketplace.visualstudio.com/items?itemName=rioj7.command-variable)

Attach script(launch.json):

```json
{
"version": "0.2.0",
"configurations": [
    {
        "name": "gdb - Attach to process",
        "type": "cppdbg",
        "request": "attach",
        "MIMode": "gdb",
        "program": "/home/poweruser/code/mysql-57-bld/sql/mysqld",
        "processId": "${input:readPID}",
        "setupCommands": [
            {
                "description": "Enable pretty-printing for gdb",
                "text": "-enable-pretty-printing",
                "ignoreFailures": true,
                "set follow-fork-mode": "child"
            }
        ],
    }
],
"inputs": [
    {
      "id": "readPID",
      "type": "command",
      "command": "extension.commandvariable.file.content",
      "args": {
        "fileName": "/home/poweruser/sandboxes/dev_5_7_37/data/mysql_sandbox5737.pid"
      }
    }
]
}
```


other options:
```
1. "procreessId": "${command:pickProcess}",
2. "preLaunchTask": "writePID", # need to define pre-launch task in task.json
```

### References
* https://stackoverflow.com/questions/52981423/can-visual-studio-code-use-gdb-to-attach-to-process-without-the-program-proper

* https://stackoverflow.com/questions/66164972/vs-code-how-to-get-process-id-via-shell-command-in-launch-json
