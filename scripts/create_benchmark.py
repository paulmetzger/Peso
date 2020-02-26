#!/usr/bin/env python3

import sys
import templates


def main():
    experiment_type = sys.argv[1]
    benchmark       = sys.argv[2]
    input_size      = sys.argv[3]

    if experiment_type == 'max_throughput':
        rel_dead      = sys.argv[4]
        wcet          = sys.argv[5]
        dop           = sys.argv[6]
        with_batching = sys.argv[7]
        batch_size    = sys.argv[8]

        if templates.create_app_for_throughput_experiments(
            benchmark,
            400, # period
            input_size,
            rel_dead,
            wcet,
            dop,
            with_batching,
            batch_size):
            print('Success')
        else:
            print('Failed')

    elif experiment_type == 'batch_size_model_accuracy':
        rel_dead = sys.argv[4]
        wcet     = sys.argv[5]
        period   = sys.argv[6]
        if templates.create_app_for_batch_size_accuracy_experiments(
                benchmark,
                period,
                input_size,
                rel_dead,
                wcet):
            print('Success')
        else:
            print('Failed')

    elif experiment_type == 'comparison_with_hand_impelementations':
        batch_size      = sys.argv[4]
        period          = sys.argv[5]
        workers         = sys.argv[6]
        experiment_type = sys.argv[7]

        if templates.create_app_for_comparison_with_hand_implementations(
                benchmark,
                period,
                input_size,
                batch_size,
                workers,
                experiment_type):
            print('Success')
        else:
            print('Failed')


if __name__ == '__main__':
    main()
