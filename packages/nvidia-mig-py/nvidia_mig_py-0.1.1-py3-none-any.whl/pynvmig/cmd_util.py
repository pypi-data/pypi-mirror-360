import subprocess


def exec_cmd(cmd: str) -> (str, str):  # type: ignore
    """ Execute a command and return the output and error

    Args:
        cmd (str): The command to execute

    Returns:
        exit_status (int): The exit status of the command executed
        out (str): The output of the command executed
    """
    try:
        p = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()
        out = p.stdout.read()
        exit_status = p.returncode
        return exit_status, out.decode('utf-8')
    except Exception as e:
        print(e)
