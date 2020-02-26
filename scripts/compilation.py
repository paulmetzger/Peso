import subprocess


def compile_farm():
    p = subprocess.Popen(['/home/paul/tools/XMOS/xTIMEcomposer/Community_14.3.3/bin/xmake CONFIG=Release all'],
                     cwd='/home/paul/phd/papers/Realtime/peso_workspace/peso', shell=True)
    return p.wait() == 0
