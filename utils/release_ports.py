import platform
import subprocess
import logging

logging.basicConfig(filename='port release.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S')
lgr = logging.getLogger(__name__)

PROXY_SERVER_PORT = 6277
MCP_INSPECTOR_PORT = 6274


def get_pid_by_port(port):
    """Gets the process ID (PID) listening on the specified port."""
    try:
        cmd = {
            "Windows": f"netstat -ano | findstr :{port}",
            "Linux": f"ss -lntp | grep :{port}",
            "Darwin": f"lsof -i :{port}",
        }.get(platform.system())
        if not cmd:
            lgr.error(f"Unsupported operating system: {platform.system()}")
            return None

        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if error:
            lgr.error(f"Error running command: {error.decode()}")
            return None

        lines = output.decode().splitlines()
        for line in lines:
            if str(port) in line:
                parts = line.split()
                if platform.system() == "Windows" and len(parts) > 4:
                    try:
                        return int(parts[4])
                    except ValueError:
                        lgr.error(f"Could not parse PID from line: {line}")
                        return None
                elif platform.system() == "Linux":
                    for part in parts:
                        if "pid=" in part:
                            try:
                                return int(part.split("=")[1])
                            except ValueError:
                                lgr.error(f"Could not parse PID from line: {line}")
                                return None
                elif platform.system() == "Darwin" and len(parts) > 1:
                    try:
                        return int(parts[1])
                    except ValueError:
                        lgr.error(f"Could not parse PID from line: {line}")
                        return None
        return None
    except Exception as e:
        lgr.error(f"An unexpected error occurred: {e}")
        return None


def kill_process(pid):
    """Kills the process with the specified PID."""
    try:
        cmd = {
            "Windows": f"taskkill /F /PID {pid}",
            "Linux": f"kill -9 {pid}",
            "Darwin": f"kill -9 {pid}",
        }.get(platform.system())
        if not cmd:
            lgr.error(f"Unsupported operating system: {platform.system()}")
            return False
        process = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        _, error = process.communicate()
        if process.returncode:
            lgr.error(f"Failed to kill process {pid}. Error: {error.decode()}")
            return False
        return True
    except Exception as e:
        lgr.error(f"An unexpected error occurred: {e}")
        return False


def main():
    default_ports = [PROXY_SERVER_PORT, MCP_INSPECTOR_PORT]
    try:
        ports_input = input(
            f"Enter port numbers to kill (space-separated,\nor leave blank for defaults {default_ports}): "
        )
        ports = [int(p.strip()) for p in ports_input.split()] if ports_input else default_ports

        for port in ports:
            if not isinstance(port, int):
                lgr.error(f"Invalid port number: {port}. Skipping.")
                continue

            pid = get_pid_by_port(port)
            if pid is None:
                lgr.info(f"No process found listening on port {port}.")
                continue

            lgr.info(f"Process ID (PID) found for port {port}: {pid}")
            if kill_process(pid):
                lgr.info(f"Process {pid} (on port {port}) killed successfully.")
            else:
                lgr.error(f"Failed to kill process {pid} (on port {port}).")
    except Exception as e:
        lgr.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()

