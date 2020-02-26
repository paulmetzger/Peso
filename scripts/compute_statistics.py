#!/usr/bin/env python3

import config
import getopt
import sys

from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker
from orm_classes    import ThroughputWithHandImplementations, \
                           Base


def hand_implementations(session):
    maximum_reduction = 0.0
    period_reductions = []
    period_differences = []

    # Read the config file
    benchmarks = config.read_config()['throughput_with_hand_implementations']
    for benchmark_in_config in benchmarks.keys():
        bench_config  = benchmarks[benchmark_in_config]
        wcets         = bench_config['wcets']
        input_sizes   = bench_config['input_array_sizes']
        rel_deadlines = bench_config['relative_deadlines']

        for input_size_index in range(len(input_sizes)):
            input_size = input_sizes[input_size_index]
            rel_dead   = rel_deadlines[input_size_index]

            peso_instances = session.query(ThroughputWithHandImplementations) \
                                   .filter(ThroughputWithHandImplementations.is_hand_implementation  == 0) \
                                   .filter(ThroughputWithHandImplementations.sample_application_name == benchmark_in_config) \
                                   .filter(ThroughputWithHandImplementations.input_size              == input_size) \
                                   .filter(ThroughputWithHandImplementations.relative_deadline       == rel_dead) \
                                   .all()
            peso_min_period_sum     = 0.0
            peso_min_period_counter = 0.0
            for peso_instance in peso_instances:
                print(peso_instance.min_period)
                peso_min_period_sum     += peso_instance.min_period
                peso_min_period_counter += 1.0
            peso_min_period_avg = peso_min_period_sum / peso_min_period_counter

            hand_impl_instances = session.query(ThroughputWithHandImplementations) \
                                   .filter(ThroughputWithHandImplementations.is_hand_implementation  == 1) \
                                   .filter(ThroughputWithHandImplementations.sample_application_name == benchmark_in_config) \
                                   .filter(ThroughputWithHandImplementations.input_size              == input_size) \
                                   .filter(ThroughputWithHandImplementations.relative_deadline       == rel_dead) \
                                   .all()
            hand_min_period_sum     = 0.0
            hand_min_period_counter = 0.0
            for hand_instance in hand_impl_instances:
                print(hand_instance.min_period)
                hand_min_period_sum     += hand_instance.min_period
                hand_min_period_counter += 1
            hand_min_period_avg = hand_min_period_sum / hand_min_period_counter

            if peso_min_period_avg >= hand_min_period_avg:
                reduction = (1.0 - hand_min_period_avg / peso_min_period_avg) * 100.0
                if reduction >= maximum_reduction: maximum_reduction = reduction
                period_reductions.append(reduction)
                period_differences.append(abs(hand_min_period_avg - peso_min_period_avg))

    print(period_reductions)
    print(period_differences)
    avg_reduction = sum(period_reductions) / len(period_reductions)

    print('Average period reduction over Peso implementations: {}%'.format(avg_reduction))
    print('Maximum period reduction over Peso implementations: {}%'.format(maximum_reduction))


def main(argv):
    # Setup code for SQLAlchemy
    engine = create_engine('sqlite:///rt.db')
    Base.metadata.bin = engine
    db_session_factory = sessionmaker(bind=engine)
    session = db_session_factory()

    opts, args = getopt.getopt(argv, 'ht:', ['type='])
    if opts[0][0] == '-h':
        print('main.py -t <experiment_type>')
        print('Experiment types: hand_implementations')
    elif opts[0][0] in ('-t', '--type'):
        if opts[0][1] == 'hand_implementations':
            hand_implementations(session)


if __name__ == '__main__':
    main(sys.argv[1:])