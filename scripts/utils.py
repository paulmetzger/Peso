from termcolor import cprint


def compute_batch_size():
    print('TBD')


def status(message, code):
    cprint(message, 'blue', end='')
    if code:
        cprint('Success', 'green')
        return True
    else:
        cprint('Failed', 'red')
        return False


def status_message(message, colour='yellow'):
    cprint(message, colour)