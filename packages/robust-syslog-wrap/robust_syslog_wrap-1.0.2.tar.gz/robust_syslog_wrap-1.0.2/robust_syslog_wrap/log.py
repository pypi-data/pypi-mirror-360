import argparse
import socket
import time
import syslog
import asyncio

# Hardcoded facility and severity values
FACILITY = syslog.LOG_USER  # Log to user-level facility
SEVERITY = syslog.LOG_INFO  # Info severity level

def syslog_priority():
    """Calculate syslog priority using hardcoded facility and severity."""
    return (FACILITY * 8) + SEVERITY

def format_syslog_message(message):
    """Format the syslog message with timestamp, hostname, and priority."""
    try:
        # Validate that the message is not empty
        if not message:
            raise ValueError("Message cannot be empty.")

        priority = syslog_priority()
        timestamp = time.strftime('%b %d %H:%M:%S')  # Format: "Oct 11 22:00:00"
        hostname = socket.gethostname()

        # Ensure that the message follows the correct format
        if len(message) > 1024:
            raise ValueError("Message is too long (over 1024 characters).")

        formatted_message = f"<{priority}>{timestamp} {hostname} my_app: {message}\n"
        return formatted_message
    except ValueError as e:
        print(f"Error formatting syslog message: {e}")
        return None  # Return None if there's an error

async def send_to_syslog(message, syslog_host, syslog_port):
    """Send a message directly to the syslog server using TCP."""
    try:
        # Format the syslog message
        syslog_message = format_syslog_message(message)

        if not syslog_message:
            return False  # If the message is invalid, don't send

        # Create TCP connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((syslog_host, syslog_port))
            s.sendall(syslog_message.encode())  # Send message to syslog server
            # Wait for a possible acknowledgment (this would just be the connection closing)
            return True
    except Exception as e:
        print(f"Error sending message to syslog: {e}")
        return False  # Return False if sending fails

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Send a message to a syslog server.")
    parser.add_argument("message", help="The message to send to syslog.")
    parser.add_argument("--host", required=True, help="The syslog server hostname or IP address (required).")
    parser.add_argument("--port", type=int, default=514, help="The syslog server port (default: 514).")

    return parser.parse_args()

async def main():
    """Main function to send message to syslog."""
    # Parse command-line arguments
    args = parse_args()

    # Send the message to the syslog server
    result = await send_to_syslog(args.message, args.host, args.port)
    print(f"Message sent: {result}")

# Run the async function
if __name__ == "__main__":
    asyncio.run(main())
