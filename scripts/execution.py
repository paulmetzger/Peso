import subprocess

command = 'xrun --adapter-id 29u0dE2N --uart /home/paul/phd/papers/Realtime/peso_workspace/peso/bin/Release/farm.xe 2>&1'

def execute_farm():
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         cwd='/home/paul/phd/papers/Realtime/peso_workspace/peso/bin/Release',
                         shell=True)
    out, _ = p.communicate()
    return (p.returncode == 1, out)
