#!/usr/bin/env python
import json
import subprocess
import sys
import threading

LOG_FILE = "mcp_session.log"


def log_write(log_f, prefix, data):
    stripped_data = data.strip()
    if not stripped_data:
        log_f.write(f"{prefix}: {data}")
        log_f.flush()
        return
    try:
        json_obj = json.loads(stripped_data)
        pretty_json = json.dumps(json_obj, indent=4)
        log_f.write(f"{prefix}:\n{pretty_json}\n")
    except json.JSONDecodeError:
        log_f.write(f"{prefix}: {data}")
    log_f.flush()


def read_from_stdin(proc_stdin, log_f):
    try:
        while True:
            user_input = sys.stdin.readline()
            if not user_input:
                break
            proc_stdin.write(user_input)
            proc_stdin.flush()
            log_write(log_f, "STDIN", user_input)
    except Exception as e:
        pass


def read_from_proc(proc_stdout, log_f):
    try:
        while True:
            server_response = proc_stdout.readline()
            if not server_response:
                break
            sys.stdout.write(server_response)
            sys.stdout.flush()
            log_write(log_f, "STDOUT", server_response)
    except Exception as e:
        pass


def read_from_proc_stderr(proc_stderr, log_f):
    try:
        while True:
            server_response = proc_stderr.readline()
            if not server_response:
                break
            log_write(log_f, "STDERR", server_response)
    except Exception as e:
        pass


def main():
    if len(sys.argv) < 2:
        print("Usage: mcp-stdin-debug <command to run>", file=sys.stderr)
        sys.exit(1)
    command = sys.argv[1:]
    with open(LOG_FILE, "a") as log_f:
        proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        t_stdin = threading.Thread(
            target=read_from_stdin, args=(proc.stdin, log_f), daemon=True
        )
        t_stdout = threading.Thread(
            target=read_from_proc, args=(proc.stdout, log_f), daemon=True
        )
        t_stderr = threading.Thread(
            target=read_from_proc_stderr, args=(proc.stderr, log_f), daemon=True
        )
        t_stdin.start()
        t_stdout.start()
        t_stderr.start()
        t_stdin.join()
        proc.stdin.close()
        t_stdout.join()
        t_stderr.join()
        proc.wait()


if __name__ == "__main__":
    main()
