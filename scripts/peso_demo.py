#!/usr/bin/env python3

import getopt
import sys

import compilation
import execution
import models
import templates
import utils


def main(argv):
    opts, args = getopt.getopt(argv, 'h', ['app_name=',
                                          'period=',
                                          'input_size=',
                                          'relative_deadline=',
                                          'worker_wcet=',
                                          'models-only',
                                          'help'])
    opts = dict(opts)

    if '--help' in opts.keys():
        print('Arguments: \n'
              + '--app_name=\n'
              + '--period=\n'
              + '--relative_deadline=\n'
              + '--worker_wcet=\n'
              + '--models-only\n'
              + '--help\n'
              + 'Example:'
              + './peso_demo.py --app_name=reduction --period=800 --input_siz=40 --relative_deadline=10000 --worker_wcet=2030'
              )
        exit(0)
    elif len(opts.keys()) < 5:
        print('ERROR: Wrong arguments')
        exit(0)

    batch_size, dop = models.compute_optimal_dop_and_batch_size(opts['--worker_wcet'],
                                                                opts['--period'],
                                                                opts['--relative_deadline'])
    templates.create_app_for_demo_purposes(opts['--app_name'],
                                           opts['--period'],
                                           opts['--input_size'],
                                           opts['--relative_deadline'],
                                           opts['--worker_wcet'],
                                           batch_size,
                                           dop)
    if not ('--models-only' in opts.keys()):
        utils.status_message('Compiling...', colour='blue')
        compilation.compile_farm()
        utils.status_message('Executing...', colour='blue')
        execution_status, out = execution.execute_farm()
        utils.status_message('Output:', colour='blue')
        print(out.decode('utf-8'))


if __name__ == '__main__':
    main(sys.argv[1:])