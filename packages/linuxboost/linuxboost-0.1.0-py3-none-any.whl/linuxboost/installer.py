import subprocess

def install_commands(commands):
    for cmd in commands:
        try:
            subprocess.run(cmd,shell=True,check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error installing: {cmd}\n{e}")
