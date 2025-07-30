# robust-syslog-wrap
**@readwithai** - [X](https://x.com/readwithai) - [blog](https://readwithai.substack.com/) - [machine-aided reading](https://www.reddit.com/r/machineAidedReading/) - [📖](https://readwithai.substack.com/p/what-is-reading-broadly-defined
)[⚡️](https://readwithai.substack.com/s/technical-miscellany)[🖋️](https://readwithai.substack.com/p/note-taking-with-obsidian-much-of)

`robust-syslog-wrap` is a command-line tool that wraps any command, captures its output, and forwards it to a syslog server. It ensures reliable log delivery using TCP, with logs buffered locally if the syslog server is unavailable, and re-sent when possible.

Normally syslog uses UDP - but here we used TCP to ensure reliable delivery.

##  Motivation
It can be natural to use a tool like logger to redirect output to syslog, but this introduces certain unreliabilities in logging. Missing log lines are frustrating, especially when running your own syslog server for a separate process. I got annoyed with logs dropping or loggers crashing—and worse, associated processes not resuming after a logger failure. So, I decided to write a syslog wrapper to ensure that logs are consistently sent to syslog without losing messages or causing unnecessary interruptions.

## Installation
You can install robust-syslog-wrap with pipx for isolation:

```bash
pipx install robust-syslog-wrap

# Usage

You can use robust-syslog-wrap to run a command and send its output to a syslog server. The following options are available:

Command-line options:
--host <host>: The syslog server's hostname or IP address (defaults to localhost).
--port <port>: The syslog server's port (defaults to 514).
--buffer-limit <size>: Set the maximum buffer size for logs in bytes (defaults to 1GB).

Here is an example

```
robust-syslog-wrap --host 192.168.1.100 --port 514 -- /path/to/your/command --arg1 --arg2
```

Which runs the command `/path/to/your/command --arg1 --arg2` and forward output and error to the syslog server at `192.168.1.100` on port 514. If no host or port is specified it connects to localhost.

## Alternatives and Prior Work
The logger command (part of bsdutils) can read from standard input and write to syslog. However, it does not handle scenarios where the syslog process is down or restarting. Many languages also have libraries that support syslog, some with retry capabilities. However, most of the existing solutions I found on GitHub were either underdocumented or didn't offer the reliability I was looking for.

## Caveats
Though this app gracefully handles syslog restarts by buffering messages, it does not deal with the wrapped process dying. This is left to a supervisor, such as systemd, supervisor, or circus, to monitor and restart the wrapped process if necessary.

This software is reviewed vibe coding with tweaks.

## About me
I am **@readwithai**. I create tools for reading, research and agency sometimes using the markdown editor [Obsidian](https://readwithai.substack.com/p/what-exactly-is-obsidian).

I also create a [stream of tools](https://readwithai.substack.com/p/my-productivity-tools) that are related to carrying out my work.

I write about lots of things - including tools like this - on [X](https://x.com/readwithai).
My [blog](https://readwithai.substack.com/) is more about reading and research and agency.
