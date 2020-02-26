#!/usr/bin/env python3

import compilation
import config
import execution
import getopt
import models
import processing
import sqlalchemy
import sys
import templates
from utils import status, status_message

from termcolor import cprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orm_classes import ThroughputSample, \
                        BatchSizeModelAccuracySample, \
                        ThroughputHeatmapSample, \
                        DOPModelAccuracySample, \
                        ThroughputWithHandImplementations, \
                        Base
import os
clear = lambda: os.system('clear')


def update_progress(progress):
    print('\r[{0}] {1}%'.format('#'*int((progress/10)), progress))


def main(argv):
    # Setup code for SQLAlchemy
    engine             = create_engine('sqlite:///rt.db')
    Base.metadata.bin  = engine
    db_session_factory = sessionmaker(bind=engine)
    session            = db_session_factory()

    opts, args = getopt.getopt(argv, 'ht:', ['type='])
    if opts[0][0] == '-h':
        print('main.py -t <experiment_type>')
        print('Experiment types: throughput, batch_size_model_accuracy, worker_model_accuracy, heatmap, hand_implementation')
    elif opts[0][0] in ('-t', '--type'):
        if opts[0][1] == 'throughput':
            throughput_experiments(session)
        elif opts[0][1] == 'batch_size_model_accuracy':
            batch_size_model_accuracy_experiments(session)
        elif opts[0][1] == 'worker_model_accuracy':
            worker_model_accuracy_experiments(session)
        elif opts[0][1] == 'heatmap':
            print('Starting heatmap experiments...')
            heatmap_experiments(session)
        elif opts[0][1] == 'hand_implementation':
            print('Starting experiments with hand implementations...')
            throughput_with_hand_implementations(session)
        else:
            print('Could not recognise the experiment type.')

        print('Done.')


def heatmap_experiments(session):
    exp_config       = config.read_config()['max_throughput_heatmap']

    app_name         = exp_config['application_name']
    deadline         = exp_config['relative_deadline']
    max_workers      = exp_config['max_workers']
    samples          = exp_config['samples']
    data_types       = exp_config['data_types']

    for data_type in data_types:
        for input_i in range(len(exp_config['input_array_size'])):
            input_array_size = exp_config['input_array_size'][input_i]
            worker_wcet      = exp_config['worker_wcet'][input_i]

            # Iterate over the batch sizes
            for dop in range(1, max_workers + 1, 1):

                # Iterate over the batch sizes
                non_viable_parameters = session.query(ThroughputHeatmapSample) \
                                               .filter(
                                               sqlalchemy.or_(
                                                   ThroughputHeatmapSample.missed_deadline == 1,
                                                   ThroughputHeatmapSample.compiled == 0,
                                                   ThroughputHeatmapSample.run_time_error == 1
                                               )) \
                                               .filter(ThroughputHeatmapSample.sample_application_name == app_name) \
                                               .filter(ThroughputHeatmapSample.input_size == input_array_size) \
                                               .filter(ThroughputHeatmapSample.relative_deadline == deadline) \
                                               .filter(ThroughputHeatmapSample.worker_wcet == worker_wcet) \
                                               .filter(ThroughputHeatmapSample.dop == dop) \
                                               .filter(ThroughputHeatmapSample.data_type == data_type) \
                                               .count()
                found_non_viable_batch_size = non_viable_parameters >= samples
                batch_size = 0
                while not found_non_viable_batch_size:
                    batch_size += 1

                    # Check if the current data point already exists
                    '''query_result = session.query(ThroughputHeatmapSample.sample).get(
                            (app_name,
                             input_array_size,
                             deadline,
                             worker_wcet,
                             batch_size,
                             dop))'''
                    sample_count = session.query(ThroughputHeatmapSample) \
                                           .filter(ThroughputHeatmapSample.sample_application_name == app_name) \
                                           .filter(ThroughputHeatmapSample.input_size              == input_array_size) \
                                           .filter(ThroughputHeatmapSample.relative_deadline       == deadline) \
                                           .filter(ThroughputHeatmapSample.worker_wcet             == worker_wcet) \
                                           .filter(ThroughputHeatmapSample.dop                     == dop) \
                                           .filter(ThroughputHeatmapSample.batch_size              == batch_size) \
                                           .filter(ThroughputHeatmapSample.data_type               == data_type) \
                                           .count()
                    print('Sample count: ' + str(sample_count))
                    print('Max. samples: ' + str(samples))
                    print('Collect more samples: ' + str(sample_count < samples))
                    print('Dop: ' + str(dop))
                    print('Batch size: ' + str(batch_size))
                    print('Data type: ' + str(data_type))
                    # input('Press...')
                    while sample_count < samples:
                        succeeded       = True
                        compiled        = True
                        run_time_error  = False
                        missed_deadline = False
                        measured_min_period = -1

                        # Measure the max. throughput
                        succeeded &= status('Creating source file from template...',
                                            templates.create_app_for_throughput_experiments(
                                                app_name,
                                                300, # Period
                                                input_array_size,
                                                deadline,
                                                worker_wcet,
                                                dop,
                                                (False if batch_size == 1 else True), # True == batching is on
                                                batch_size,
                                                dop == 1,
                                                data_type
                                            ))
                        succeeded &= status('Compiling...', compilation.compile_farm())

                        if not succeeded:
                            cprint('Measure max. throughput | Could not compile the application. DOP: {} Batch size {}'\
                                    .format(dop, batch_size), 'red')
                            compiled = False
                        else:
                            execution_status, out  = execution.execute_farm()
                            succeeded             &= status('Executing...', execution_status)

                            if not succeeded:
                                cprint('Measure max. throughput | Could not run the application. DOP: {} Batch size {}' \
                                        .format(dop, batch_size), 'red')
                                run_time_error = True
                            else:
                                internal_param, output = processing.parse_output_to_dict(out.decode('utf-8'))
                                measured_min_period    = processing.compute_interarrival_time(output, batch_size, dop)

                                # check if batch size and measured period are viable
                                succeeded &= status('Creating source file from template...',
                                                    templates.create_app_for_throughput_heatmap_experiments(
                                                        app_name,
                                                        measured_min_period,  # period
                                                        input_array_size,
                                                        deadline,
                                                        dop,
                                                        worker_wcet,
                                                        batch_size,
                                                        dop == 1,
                                                        data_type
                                                    ))

                                # Check if the current batch size is viable
                                succeeded &= status('Compiling...', compilation.compile_farm())

                            if not succeeded:
                                cprint('Check if the current batch size is viable | Could not compile the application. DOP: {} Batch size {}'\
                                        .format(dop, batch_size), 'red')
                                compiled = False
                            else:
                                execution_status, out  = execution.execute_farm()
                                succeeded             &= status('Executing...', execution_status)

                                if not succeeded:
                                    cprint('Check if the current batch size is viable | Could not run the application. DOP: {} Batch size {}' \
                                            .format(dop, batch_size), 'red')
                                    run_time_error = True
                                else:
                                    internal_param, output = processing.parse_output_to_dict(out.decode('utf-8'))
                                    missed_deadline        = processing.check_if_deadline_has_been_missed(output, deadline)

                                    if missed_deadline:
                                        cprint('Check if the current batch size is viable | Jobs miss their deadline. DOP: {} Batch size {}' \
                                               .format(dop, batch_size), 'red')
                                        succeeded = False

                        # save result
                        sample = ThroughputHeatmapSample(
                            sample_application_name=app_name,
                            input_size             =input_array_size,
                            relative_deadline      =deadline,
                            worker_wcet            =worker_wcet,
                            batch_size             =batch_size,
                            dop                    =dop,
                            min_period             =measured_min_period,
                            sample                 =sample_count + 1,
                            data_type              =data_type,
                            compiled               =compiled,
                            missed_deadline        =missed_deadline,
                            run_time_error         =run_time_error
                        )
                        session.add(sample)
                        session.commit()

                        sample_count += 1

                        found_non_viable_batch_size |= not succeeded


def run_worker_model_accuracy_experiment(sample_application,
                                         period,
                                         input_array_size,
                                         relative_deadline,
                                         worker_wcet,
                                         subtract_from_dop):
    succeeded = True

    # Compute batch size and worker count
    computed_batch_size, computed_dop = models.compute_optimal_dop_and_batch_size(worker_wcet, period, relative_deadline)
    status_message('DEBUG | batch_size: {}, dop: {}'.format(computed_batch_size, computed_dop))

    # Generate source code from template
    succeeded &= status('Creating source files from templates...',
                        templates.create_app_for_worker_model_accuracy_experiments(
                            sample_application,
                            period,
                            input_array_size,
                            relative_deadline,
                            worker_wcet,
                            computed_batch_size,
                            computed_dop,
                            subtract_from_dop
                        ))

    # Compile
    if succeeded:
        succeeded &= status('Compiling...', compilation.compile_farm())

    # Run the experiment
    if succeeded:
        execution_status, out = execution.execute_farm()
        succeeded &= status('Executing...', execution_status)

    # Process the output
    matched_throughput = False
    if succeeded:
        internal_param, output = processing.parse_output_to_dict(out.decode('utf-8'))
        # Add 10ns to the period account for the accuracy of the board's timers
        matched_throughput     = (processing.compute_interarrival_time(
            output,
            internal_param['batch_size'],
            internal_param['dop']) <= period + 10)
        print('Measured min. period: {}'.format(processing.compute_interarrival_time(
            output,
            internal_param['batch_size'],
            internal_param['dop'])))

    return succeeded, matched_throughput, internal_param['batch_size'], internal_param['dop']


def worker_model_accuracy_experiments(session):
    benchmarks = config.read_config()['dop_model_accuracy']
    for app in benchmarks.keys():
        bench_config           = benchmarks[app]
        relative_deadline_list = bench_config['relative_deadline']
        input_array_size_list  = bench_config['input_array_size']
        worker_wcet_list       = bench_config['worker_wcet']
        period_start_list      = bench_config['period_start']
        period_end_list        = bench_config['period_end']
        period_steps_list      = bench_config['period_steps']
        samples                = bench_config['samples']

        for i in range(len(input_array_size_list)):
            relative_deadline = relative_deadline_list[i]
            input_array_size  = input_array_size_list[i]
            worker_wcet       = worker_wcet_list[i]
            period_start      = period_start_list[i]
            period_end        = period_end_list[i]
            period_steps      = period_steps_list[i]

            # Iterate over all periods
            for period in range(period_start, period_end + period_steps, period_steps):
                # Find the optimum and test predictions
                for is_oracle in [False, True]:
                    sample_count = session.query(DOPModelAccuracySample) \
                                          .filter(DOPModelAccuracySample.sample_application_name == app) \
                                          .filter(DOPModelAccuracySample.input_size              == input_array_size) \
                                          .filter(DOPModelAccuracySample.relative_deadline       == relative_deadline) \
                                          .filter(DOPModelAccuracySample.worker_wcet             == worker_wcet) \
                                          .filter(DOPModelAccuracySample.period                  == period) \
                                          .filter(DOPModelAccuracySample.is_oracle               == is_oracle) \
                                          .count()
                    print('Is oracle: {}'.format(is_oracle))
                    print('Sample count: {}'.format(sample_count))
                    while sample_count < samples:
                        if is_oracle:
                            print('Finding the minimum DOP...')
                            matched_throughput = True
                            subtract_from_dop = 0
                            while matched_throughput:
                                print('Subtract from DOP: ' + str(subtract_from_dop))
                                succeeded, matched_throughput, batch_size, dop = run_worker_model_accuracy_experiment(
                                    app,
                                    period,
                                    input_array_size,
                                    relative_deadline,
                                    worker_wcet,
                                    subtract_from_dop)
                                print('Matched throughput: ' + str(matched_throughput))

                                if not succeeded:
                                    status_message('Oracle experiments failed!')
                                    exit(0)

                                if matched_throughput and not dop == 1:
                                    subtract_from_dop += 1
                                elif matched_throughput and dop == 1:
                                    break
                                elif not matched_throughput:
                                    if subtract_from_dop == 0:
                                        status_message('ERROR | The DOP predicted by our model is too low')
                                        exit(0)

                                    dop += 1

                            matched_throughput = True

                        else:
                            succeeded, matched_throughput, batch_size, dop = run_worker_model_accuracy_experiment(
                                app,
                                period,
                                input_array_size,
                                relative_deadline,
                                worker_wcet,
                                0 # Subtract from DOP
                            )

                        if succeeded:
                            sample = DOPModelAccuracySample(
                                sample_application_name=app,
                                input_size             =input_array_size,
                                relative_deadline      =relative_deadline,
                                worker_wcet            =worker_wcet,
                                period                 =period,
                                is_oracle              =is_oracle,
                                sample                 =sample_count + 1,
                                batch_size             =batch_size,
                                dop                    =dop,
                                success                =succeeded,
                                matched_throughput     =matched_throughput
                            )
                            session.add(sample)
                            session.commit()

                            sample_count += 1
                        else:
                            status_message('Compilation or execution did not succeed. Exiting...')
                            exit(0)


def run_batch_size_accuracy_experiment(sample_application,
                                       period,
                                       input_array_size,
                                       relative_deadline,
                                       worker_wcet,
                                       add_to_batch_size=0):
    succeeded = True

    # Compute batch size and worker count
    computed_batch_size, computed_dop = models.compute_optimal_dop_and_batch_size(worker_wcet, period,
                                                                                  relative_deadline)
    status_message('DEBUG | batch_size: {}, dop: {}'.format(computed_batch_size, computed_dop))

    # Generate source code from template
    succeeded &= status('Creating source files from templates...',
                        templates.create_app_for_batch_size_accuracy_experiments(
                            sample_application,
                            period,
                            input_array_size,
                            relative_deadline,
                            worker_wcet,
                            computed_batch_size,
                            computed_dop,
                            add_to_batch_size=add_to_batch_size
                        ))

    # Compile
    if succeeded:
        status_message(('DEBUG | period: {}, input_array_size: {}, relative_deadline: {},' +
                       ' worker_wcet: {}, add_to_batch_size: {}')
                       .format(period,
                               input_array_size,
                               relative_deadline,
                               worker_wcet,
                               add_to_batch_size))
        succeeded &= status('Compiling...', compilation.compile_farm())
    else:
        status_message("Could not create the sample application.")
        exit(0)

    # Run the experiment
    if succeeded:
        execution_status, out = execution.execute_farm()
        succeeded            &= status('Executing...', execution_status)
    else:
        status_message("Could not compile the sample application.")
        exit(0)

    # Process the output
    missed_deadline = False
    if succeeded:
        internal_param, output = processing.parse_output_to_dict(out.decode('utf-8'))
        missed_deadline        = processing.check_if_deadline_has_been_missed(output, relative_deadline)
    else:
        status_message("Could not run the sample application.")
        exit(0)

    return succeeded, missed_deadline, internal_param['batch_size'], internal_param['dop']


def batch_size_model_accuracy_experiments(session):
    benchmarks                   = config.read_config()['batch_size_model_accuracy']
    for sample_application in benchmarks.keys():
        bench_config             = benchmarks[sample_application]
        relative_deadline_list   = bench_config['relative_deadline']
        input_array_size_list    = bench_config['input_array_size']
        worker_wcet_list         = bench_config['worker_wcet']
        period_start_list        = bench_config['period_start']
        period_end_list          = bench_config['period_end']
        period_steps_list        = bench_config['period_steps']
        samples = bench_config['samples']

        for i in range(len(input_array_size_list)):
            relative_deadline = relative_deadline_list[i]
            input_array_size  = input_array_size_list[i]
            worker_wcet       = worker_wcet_list[i]
            period_start      = period_start_list[i]
            period_end        = period_end_list[i]
            period_steps      = period_steps_list[i]

            # Iterate over all periods
            for period in range(period_start, period_end + period_steps, period_steps):

                # Find the optimum and test predictions
                for is_oracle in [False, True]:

                    # Check if database entry for the current problem instance exists already
                    sample_count =  session.query(BatchSizeModelAccuracySample) \
                                           .filter(BatchSizeModelAccuracySample.sample_application_name == sample_application) \
                                           .filter(BatchSizeModelAccuracySample.input_size              == input_array_size) \
                                           .filter(BatchSizeModelAccuracySample.relative_deadline       == relative_deadline) \
                                           .filter(BatchSizeModelAccuracySample.worker_wcet             == worker_wcet) \
                                           .filter(BatchSizeModelAccuracySample.period                  == period) \
                                           .filter(BatchSizeModelAccuracySample.is_oracle               == is_oracle) \
                                           .count()
                    while sample_count < samples:
                        add_to_batch_size = 0
                        if is_oracle:
                            # Find the optimum
                            missed_deadline   = False

                            # TODO: Refactor duplication
                            add_to_batch_size = 0
                            while not missed_deadline:
                                succeeded, missed_deadline, batch_size, _ = run_batch_size_accuracy_experiment(
                                    sample_application,
                                    period,
                                    input_array_size,
                                    relative_deadline,
                                    worker_wcet,
                                    add_to_batch_size=add_to_batch_size)

                                if not succeeded:
                                    status_message('ERROR | Oracle experiments failed!')
                                    exit(0)

                                if not missed_deadline:
                                    add_to_batch_size += 1
                                else:
                                    if add_to_batch_size == 0:
                                        status_message('ERROR | The batch size chosen by our model is too large.')
                                        exit(0)

                                    # This value will be stored in the DB
                                    # Subtract by 1 since the application fails to meet deadlines with the current
                                    # batch size
                                    status_message('DEBUG | Missed deadlines')
                                    batch_size -= 1

                            missed_deadline = False

                        else:
                            succeeded, missed_deadline, batch_size, _ = run_batch_size_accuracy_experiment(
                                sample_application,
                                period,
                                input_array_size,
                                relative_deadline,
                                worker_wcet,
                                add_to_batch_size)

                            if missed_deadline:
                                status_message('ERROR | The batch size chosen by our model is too large.')
                                exit(0)

                        # Save results
                        if succeeded:
                            sample = BatchSizeModelAccuracySample(
                                sample_application_name=sample_application,
                                input_size             =input_array_size,
                                relative_deadline      =relative_deadline,
                                worker_wcet            =worker_wcet,
                                period                 =period,
                                is_oracle              =is_oracle,
                                sample                 =sample_count + 1,
                                batch_size             =batch_size,
                                success                =succeeded,
                                deadline_missed        =missed_deadline
                            )
                            session.add(sample)
                            session.commit()

                            sample_count += 1
                        else:
                            status_message('Compilation or execution did not succeed. Exiting...')


def throughput_experiments(session):
    benchmarks = config.read_config()['throughput']
    for benchmark in benchmarks.keys():
        # Read config file
        bench_config    = benchmarks[benchmark]
        wcets           = bench_config['wcet']
        input_sizes     = bench_config['input_array_size']
        rel_dead_start  = bench_config['relative_deadline_start']
        rel_dead_steps  = bench_config['relative_deadline_steps']
        rel_dead_stop   = bench_config['relative_deadline_stop']
        workers_start   = bench_config['workers_start']
        workers_steps   = bench_config['workers_steps']
        workers_stop    = bench_config['workers_stop']
        samples         = bench_config['samples']

        total_number_of_experiments = 2 * len(wcets) \
                                     * len(range(workers_start, workers_stop + 1, workers_steps)) \
                                     * len(range(rel_dead_start, rel_dead_stop + rel_dead_steps, rel_dead_steps))
        experiment_count = 0

        # The baseline does not use batching
        for with_batching in [True, False]:
            # Sweep over the parameter space
            # Parameter: input sizes + corresp. WCETs
            for wcet_index in range(len(wcets)):
                wcet        = wcets[wcet_index]
                input_size  = input_sizes[wcet_index]
                batch_sizes = bench_config['batch_sizes'][wcet_index]
                for batch_size in batch_sizes:
                    if not with_batching:
                        batch_size = 1
                    # Parameter: worker count
                    for dop in range(workers_start, workers_stop + 1, workers_steps):
                        # Parameter: relative deadline
                        for rel_dead in range(rel_dead_start, rel_dead_stop + rel_dead_steps, rel_dead_steps):
                            clear()
                            update_progress(experiment_count / total_number_of_experiments)
                            print('Experiment: {}, with batching: {}, WCET: {}, DOP: {}, D: {}, Batch size: {}'.format(
                                                                                               benchmark,
                                                                                               with_batching,
                                                                                               wcet,
                                                                                               dop,
                                                                                               rel_dead,
                                                                                               batch_size))
                            # Check if data for this current parameter set exists
                            # and execute experiments if they do not exist
                            sample_count = session.query(ThroughputSample) \
                                                  .filter(ThroughputSample.experiment_name   == benchmark) \
                                                  .filter(ThroughputSample.input_size        == input_size) \
                                                  .filter(ThroughputSample.relative_deadline == rel_dead) \
                                                  .filter(ThroughputSample.worker_wcet       == wcet) \
                                                  .filter(ThroughputSample.with_batching     == int(with_batching)) \
                                                  .filter(ThroughputSample.batch_size        == batch_size) \
                                                  .count()

                            while sample_count < samples:
                                # Prepare experiments
                                status_code = True
                                status_code &= status('Creating source files from templates... ', templates.create_app_for_throughput_experiments(
                                    benchmark,
                                    300, # period. This does not set the period with which new input data arrives in this case.
                                         # This is just a dummy values that is need to compute the size of the task
                                         # farm internal buffer.
                                    input_size,
                                    rel_dead,
                                    wcet,
                                    dop,
                                    with_batching,
                                    batch_size))

                                compilation_succeeded = False
                                if status_code:
                                    status_code          &= status('Compiling... ', compilation.compile_farm())
                                    compilation_succeeded = status_code

                                # Run experiment
                                if status_code:
                                    execution_status, out = execution.execute_farm()
                                    status_code          &= status('Executing... ', execution_status)
                                    print(out)

                                # Prepare results
                                if status_code:
                                    internal_param, output = processing.parse_output_to_dict(out.decode('utf-8'))
                                    period                 = processing.compute_interarrival_time(output, batch_size, dop)

                                    # Check if the application could successfully compiled and run
                                    status_message('Compilation and execution was successful')
                                else:
                                    status_message('Compilation or execution did not succeed. Exiting...')
                                    break

                                # Print the result to the console
                                status_message('Found min. interarrival time: ' + str(period))

                                # Store the result in the database
                                sample = ThroughputSample(
                                    experiment_name  =benchmark,
                                    input_size       =input_size,
                                    relative_deadline=rel_dead,
                                    worker_wcet      =wcet,
                                    dop              =dop,
                                    with_batching    =int(with_batching),
                                    sample           =sample_count + 1,
                                    success          =int(compilation_succeeded))
                                sample.batch_size            = batch_size
                                sample.min_interarrival_time = period

                                # Save result
                                session.add(sample)
                                session.commit()

                                sample_count += 1

                            experiment_count += 1


def throughput_with_hand_implementations(session):
    benchmarks = config.read_config()['throughput_with_hand_implementations']
    for benchmark_in_config in benchmarks.keys():

        # Read config file
        bench_config  = benchmarks[benchmark_in_config]
        wcets         = bench_config['wcets']
        input_sizes   = bench_config['input_array_sizes']
        rel_deadlines = bench_config['relative_deadlines']
        samples       = bench_config['samples']

        total_number_of_experiments = 2 * \
                                      len(input_sizes) * \
                                      len(rel_deadlines)

        experiment_count = 1

        for is_hand_implementation in [False, True]:
            if is_hand_implementation:
                benchmark = 'hand_implemented_' + benchmark_in_config
            else:
                benchmark = benchmark_in_config

            for input_size_index in range(len(input_sizes)):
                dop        = 6
                wcet       = wcets[input_size_index]
                input_size = input_sizes[input_size_index]
                rel_dead   = rel_deadlines[input_size_index]

                clear()
                update_progress((experiment_count / total_number_of_experiments) * 100)
                print('Experiment: {}, WCET: {}, DOP: {}, D: {}'.format(
                        benchmark,
                        wcet,
                        dop,
                        rel_dead
                ))

                sample_count = session.query(ThroughputWithHandImplementations) \
                                       .filter(ThroughputWithHandImplementations.sample_application_name == benchmark_in_config) \
                                       .filter(ThroughputWithHandImplementations.input_size              == input_size) \
                                       .filter(ThroughputWithHandImplementations.relative_deadline       == rel_dead) \
                                       .filter(ThroughputWithHandImplementations.worker_wcet             == wcet) \
                                       .filter(ThroughputWithHandImplementations.dop                     == dop) \
                                       .filter(ThroughputWithHandImplementations.is_hand_implementation  == is_hand_implementation) \
                                       .count()

                while sample_count < samples:
                    # Find max. batch size
                    batch_size = 1
                    if not is_hand_implementation:
                        while True:
                            succeeded = True
                            if is_hand_implementation:
                                succeeded &= status('Creating source files from template...',
                                                    templates.create_app_for_comparison_with_hand_implementations(
                                                        benchmark,
                                                        250, # period
                                                        input_size,
                                                        batch_size,
                                                        dop,
                                                        'batch_size_accuracy'
                                                    ))
                            else:
                                succeeded &= status('Creating source files from template...',
                                                    templates.create_app_for_batch_size_accuracy_experiments(
                                                        benchmark,
                                                        250,  # period
                                                        input_size,
                                                        rel_dead,
                                                        wcet,
                                                        batch_size,
                                                        dop,
                                                        0 # subtract_from_dop
                                                    ))

                            if not succeeded:
                                cprint('ERROR: Could not generate source file', 'red')
                                exit(0)

                            succeeded &= status('Compiling...', compilation.compile_farm())
                            if not succeeded:
                                cprint('Check if the current batch size is viable | Could not compile the application', 'blue')
                                break

                            execution_status, out = execution.execute_farm()
                            succeeded            &= status('Executing...', execution_status)
                            if not succeeded:
                                cprint('Check if the current batch size is viable | Could not run the application', 'blue')
                                break

                            internal_param, output = processing.parse_output_to_dict(out.decode('utf-8'))
                            missed_deadline        = processing.check_if_deadline_has_been_missed(output, rel_dead)

                            if missed_deadline:
                                cprint('Check if the current batch size is viable | ' +
                                       'Jobs miss their deadline. DOP: {} Batch size {}'.format(dop, batch_size), 'blue')
                                break

                            batch_size += 1

                            clear()
                            update_progress((experiment_count / total_number_of_experiments) * 100)

                        batch_size -= 1

                    else:
                        instance = session.query(ThroughputWithHandImplementations) \
                                          .filter(ThroughputWithHandImplementations.sample_application_name == benchmark_in_config) \
                                          .filter(ThroughputWithHandImplementations.input_size              == input_size) \
                                          .filter(ThroughputWithHandImplementations.relative_deadline       == rel_dead) \
                                          .filter(ThroughputWithHandImplementations.worker_wcet             == wcet) \
                                          .filter(ThroughputWithHandImplementations.dop                     == dop) \
                                          .filter(ThroughputWithHandImplementations.is_hand_implementation  == 0) \
                                          .first()

                        batch_size = instance.batch_size
                        print('Batch size in DB: {}'.format(batch_size))

                    if batch_size == 0:
                        cprint('ERROR: Could not compile or run an application with batch size 1', 'red')
                        exit(0)

                    clear()
                    update_progress((experiment_count / total_number_of_experiments) * 100)

                    cprint('Finding maximum throughput with the found maximum batch size...', 'blue')
                    # Measure max. throughput with the found batch size
                    # Prepare experiments
                    status_code = True
                    if is_hand_implementation:
                        status_code &= status('Creating source files from templates... ',
                                              templates.create_app_for_comparison_with_hand_implementations(
                                                  benchmark,
                                                  250,  # period
                                                  input_size,
                                                  batch_size,
                                                  dop,
                                                  'throughput'
                                              ))
                    else:
                        status_code &= status('Create source file from templates...',
                                              templates.create_app_for_throughput_experiments(
                                                  benchmark,
                                                  250,  # period,
                                                  input_size,
                                                  rel_dead,
                                                  wcet,
                                                  dop,
                                                  True, # with_batching
                                                  batch_size
                                              ))

                    if status_code:
                        status_code &= status('Compiling... ', compilation.compile_farm())
                    else:
                        cprint('ERROR: Could not generate source code for a sample application', 'red')
                        exit(0)

                    # Run experiment
                    if status_code:
                        execution_status, out = execution.execute_farm()
                        status_code          &= status('Executing... ', execution_status)
                        print(out)
                    else:
                        cprint('ERROR: Could not compile a sample application', 'red')
                        exit(0)

                    # Prepare results
                    if status_code:
                        internal_param, output = processing.parse_output_to_dict(out.decode('utf-8'))
                        period                 = processing.compute_interarrival_time(output, batch_size, dop)

                        # Check if the application could successfully compiled and run
                        status_message('Compilation and execution was successful')
                    else:
                        cprint('ERROR: Could not execute a sample application', 'red')
                        exit(0)

                    # Print the result to the console
                    status_message('Found min. period: ' + str(period))

                    # Store the result in the database
                    sample = ThroughputWithHandImplementations(
                        sample_application_name=benchmark_in_config,
                        input_size             =input_size,
                        relative_deadline      =rel_dead,
                        worker_wcet            =wcet,
                        dop                    =dop,
                        is_hand_implementation =is_hand_implementation,
                        sample_count           =sample_count+1,
                        batch_size             =batch_size,
                        min_period             =period)

                    # Save result
                    session.add(sample)
                    session.commit()

                    sample_count += 1

                experiment_count += 1


'''The below experiment likely does not make sense'''
'''def throughput_loss_due_to_non_optimal_batch_size_experiments(session):
    experiments = session.query(BatchSizeModelAccuracySample).all()
    for experiment in experiments:
        app_name = experiment.sample_application_name
        input_size = experiment.input_size
        relative_deadline = experiment.relative_deadline
        worker_wcet = experiment.worker_wcet
        period = experiment.period
        is_oracle = experiment.is_oracle
        batch_size = experiment.batch_size

    print(experiments[0].sample_application_name)'''


if __name__ == '__main__':
    main(sys.argv[1:])