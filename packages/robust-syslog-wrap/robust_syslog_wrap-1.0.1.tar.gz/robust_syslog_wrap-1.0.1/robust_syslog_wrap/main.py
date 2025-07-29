import argparse
import asyncio
import signal
import socket
import subprocess
import sys
import time

# Default Configurations
SYSLOG_HOST = 'localhost'
SYSLOG_PORT = 514
RETRY_INTERVAL = 5  # Retry every 5 seconds by default
BUFFER_SIZE = 1024 * 1024 * 10  # Max buffer size (e.g., 10 million messages)

# Async buffer for storing logs when syslog is down
log_queue = asyncio.Queue(maxsize=BUFFER_SIZE)

async def send_to_syslog(message, syslog_host, syslog_port):
    """Send a message directly to the syslog server using TCP."""
    try:
        # Create TCP connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((syslog_host, syslog_port))
            s.sendall(message.encode())
            return True
    except Exception as e:
        return False  # Return False if sending fails

async def writer_task(syslog_host, syslog_port, managed_process, retry_interval):
    """Async task to write messages to syslog."""
    first_write_attempt = True  # Flag to track the first write attempt
    first_write_start_time = None  # To track the time of the first write attempt

    while True:
        message = await log_queue.get()

        success = False
        while not success:  # Infinite retry loop
            if first_write_attempt:
                # Start the timer for the first write attempt
                if first_write_start_time is None:
                    first_write_start_time = time.time()

                # Attempt to write to syslog
                success = await send_to_syslog(message, syslog_host, syslog_port)

                # Check if the first write attempt has taken more than 30 seconds
                if not success and time.time() - first_write_start_time > 30:
                    print(f"Failed to connect to syslog ({syslog_host}:{syslog_port}) within 30 seconds. Attempting to shut down gracefully...", file=sys.stderr)

                    # Gracefully terminate the managed process
                    managed_process.send_signal(signal.SIGTERM)

                    # Wait for the process to exit, with a timeout of 30 seconds
                    try:
                        await asyncio.wait_for(managed_process.wait(), timeout=30)
                        print("Managed process exited gracefully.")
                    except asyncio.TimeoutError:
                        print("Managed process did not exit within 30 seconds. Sending KILL signal...", file=sys.stderr)
                        managed_process.kill()  # Forcefully kill the process if it doesn't exit
                        print("Managed process killed.")

                    sys.exit(1)  # Exit after trying to shut down gracefully
                elif success:
                    first_write_attempt = False  # After first attempt, switch to regular retries
                else:
                    print(f"Failed to write to syslog ({syslog_host}:{syslog_port}). Retrying...", file=sys.stderr)
                    await asyncio.sleep(retry_interval)  # Wait before retrying
            else:
                # Normal retry behavior after the first successful write
                success = await send_to_syslog(message, syslog_host, syslog_port)
                if not success:
                    # Log failure to stderr without the message
                    print(f"Failed to write to syslog ({syslog_host}:{syslog_port}). Retrying...", file=sys.stderr)
                    await asyncio.sleep(retry_interval)  # Wait before retrying

async def async_read_lines(stream):
    """Asynchronously read lines from the process output stream."""
    while True:
        line = await stream.readline()
        if not line:  # End of stream
            break
        yield line.decode('utf-8').strip()

async def produce_messages_from_process(process):
    """Capture stdout and stderr from a running process and push logs to syslog."""
    stdout_task = asyncio.create_task(read_stream(process.stdout, sys.stdout))
    stderr_task = asyncio.create_task(read_stream(process.stderr, sys.stderr))

    # Wait until both tasks are finished
    await asyncio.gather(stdout_task, stderr_task)

async def read_stream(stream, output_stream):
    """Read from a stream, output to sys.stdout or sys.stderr, and log to syslog."""
    async for line in async_read_lines(stream):
        print(line, file=output_stream)  # Print to stdout or stderr
        await log_queue.put(line)  # Log to syslog

async def amain():
    """Main entry point to run the syslog wrapper."""
    parser = argparse.ArgumentParser(description="Wrap a command and forward logs to syslog.")
    parser.add_argument("rest", nargs=argparse.REMAINDER, help="The command and its arguments to run and capture logs")
    parser.add_argument("--host", default=SYSLOG_HOST, help="Syslog server host (default: localhost)")
    parser.add_argument("--port", type=int, default=SYSLOG_PORT, help="Syslog server port (default: 514)")
    parser.add_argument("--buffer-size", type=int, default=BUFFER_SIZE, help="Buffer size in bytes (default: 10 million messages)")
    parser.add_argument("--retry-interval", type=int, default=RETRY_INTERVAL, help="Retry interval in seconds (default: 5)")

    args = parser.parse_args()

    # Update global configurations from CLI args
    syslog_host = args.host
    syslog_port = args.port
    buffer_size = args.buffer_size
    retry_interval = args.retry_interval

    # Update the global log_queue with the new buffer size
    global log_queue
    log_queue = asyncio.Queue(maxsize=buffer_size)

    if not args.rest:
        print("No command provided to run.")
        sys.exit(1)

    # Start the command process
    process = await asyncio.create_subprocess_exec(*args.rest,
                                                   stdout=subprocess.PIPE,
                                                   stderr=subprocess.PIPE)

    # Start the writer task in the background with the provided retry_interval
    writer_task_instance = asyncio.create_task(writer_task(syslog_host, syslog_port, process, retry_interval))

    # Create tasks for the stream reading
    stream_task = asyncio.create_task(produce_messages_from_process(process))

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(shutdown(loop, process)))
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(shutdown(loop, process)))


    await process.wait()  # This will wait forever until the process exits

    try:
        # Wait for both tasks with a timeout
        await asyncio.wait_for(
            asyncio.gather(stream_task, writer_task_instance),
            timeout=5  # Timeout applied to both tasks together
        )
    except asyncio.TimeoutError:
        print(f"Flushing logs to syslog ({syslog_host}:{syslog_port}). Giving up.", file=sys.stderr)
        # Optionally, handle cleanup or process termination here
        sys.exit(1)  # Exit with an error code


async def shutdown(loop, process):
    """Gracefully shut down on receiving a signal."""
    print("Received signal, shutting down gracefully...")
    process.send_signal(signal.SIGTERM)  # First, send a SIGTERM to gracefully terminate the process

    try:
        # Wait for process to terminate within 30 seconds
        await asyncio.wait_for(process.wait(), timeout=30)
        print("Process exited gracefully.")
    except asyncio.TimeoutError:
        # If process doesn't terminate within 30 seconds, send SIGKILL
        print("Process did not exit within 30 seconds. Sending SIGKILL...", file=sys.stderr)
        process.kill()  # Forcefully terminate the process with SIGKILL
        print("Process killed.")


def main():
    asyncio.run(amain())
