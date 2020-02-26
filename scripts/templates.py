import subprocess

sed_command_for_demo_code = 'sed ' \
    + ' -e \'s/%PERIOD%/$PERIOD$/\'' \
    + ' -e \'s/%INPUT_VECTOR_SIZE%/$INPUT_VECTOR_SIZE$/\'' \
    + ' -e \'s/%RELATIVE_DEADLINE%/$RELATIVE_DEADLINE$/\'' \
    + ' -e \'s/%WORKER_WCET%/$WORKER_WCET$/\'' \
    + ' -e \'s/%BATCH_SIZE%/$BATCH_SIZE$/\'' \
    + ' -e \'s/%WORKERS%/$WORKERS$/\'' \
    + ' demo_$APP_NAME$.h> $APP_NAME$.h'


sed_command_for_hand_implemented_code = 'sed ' \
    + ' -e \'s/%INTERARRIVAL_TIME_NS%/$INTERARRIVAL_TIME_NS$/\'' \
    + ' -e \'s/%INPUT_SIZE%/$INPUT_SIZE$/\'' \
    + ' -e \'s/%BATCH_SIZE%/$BATCH_SIZE$/\'' \
    + ' -e \'s/%WORKERS%/$WORKERS$/\'' \
    + ' -e \'s/%EXPIREMENT_TYPE%/$EXPIREMENT_TYPE$/\'' \
    + ' template_$APP_NAME$.h> $APP_NAME$.h'


sed_command_for_throughput_heatmap_experiments = 'sed ' \
    + ' -e \'s/%INTERARRIVAL_TIME_NS%/$INTERARRIVAL_TIME_NS$/\'' \
    + ' -e \'s/%INPUT_VECTOR_SIZE%/$INPUT_VECTOR_SIZE$/\'' \
    + ' -e \'s/%RELATIVE_DEADLINE%/$RELATIVE_DEADLINE$/\'' \
    + ' -e \'s/%WCET%/$WCET$/\'' \
    + ' -e \'s/%HOOK%/#define BATCH_SIZE $BATCH_SIZE$/\'' \
    + ' -e \'s/%DATA_TYPE%/$DATA_TYPE$/\'' \
    + ' -e \'s/%HOOK2%//\'' \
    + ' -e \'s/%HOOK3%/#define NUMBER_OF_WORKERS $WORKERS$/\'' \
    + ' -e \'s/%HOOK4%//\'' \
    + ' -e \'s/%HOOK5%/#define BATCH_MODEL_ACCURACY_EXPERIMENTS/\'' \
    + ' -e \'s/%HOOK6%//\'' \
    + ' -e \'s/%PESO_IMPLEMENTATION%/$PESO_IMPLEMENTATION$/\'' \
    + ' -e \'s/%PESO_SLEEP%/peso_sleep(INTERARRIVAL_TIME_NS);/\'' \
    + ' template_$APP_NAME$.h> $APP_NAME$.h'


sed_command_for_worker_model_accuracy_experiments = 'sed ' \
    + ' -e \'s/%INTERARRIVAL_TIME_NS%/$INTERARRIVAL_TIME_NS$/\'' \
    + ' -e \'s/%INPUT_VECTOR_SIZE%/$INPUT_VECTOR_SIZE$/\'' \
    + ' -e \'s/%RELATIVE_DEADLINE%/$RELATIVE_DEADLINE$/\'' \
    + ' -e \'s/%WCET%/$WCET$/\'' \
    + ' -e \'s/%DATA_TYPE%/$DATA_TYPE$/\'' \
    + ' -e \'s/%HOOK%//\'' \
    + ' -e \'s/%HOOK2%/#define BATCH_SIZE $BATCH_SIZE$/\'' \
    + ' -e \'s/%HOOK3%//\'' \
    + ' -e \'s/%HOOK4%/#define NUMBER_OF_WORKERS ($WORKERS$ - $SUBTRACT_FROM_DOP$)/\'' \
    + ' -e \'s/%HOOK5%//\'' \
    + ' -e \'s/%HOOK6%/#define THROUGHPUT_EXPERIMENTS/\'' \
    + ' -e \'s/%PESO_IMPLEMENTATION%/farm/\'' \
    + ' -e \'s/%PESO_SLEEP%/peso_sleep(INTERARRIVAL_TIME_NS);/\'' \
    + ' template_$APP_NAME$.h> $APP_NAME$.h'


sed_command_for_batch_size_accuracy_experiments = 'sed ' \
    + ' -e \'s/%INTERARRIVAL_TIME_NS%/$INTERARRIVAL_TIME_NS$/\'' \
    + ' -e \'s/%INPUT_VECTOR_SIZE%/$INPUT_VECTOR_SIZE$/\'' \
    + ' -e \'s/%RELATIVE_DEADLINE%/$RELATIVE_DEADLINE$/\'' \
    + ' -e \'s/%WCET%/$WCET$/\'' \
    + ' -e \'s/%DATA_TYPE%/$DATA_TYPE$/\'' \
    + ' -e \'s/%HOOK%//\'' \
    + ' -e \'s/%HOOK2%/#define BATCH_SIZE ($BATCH_SIZE$ + $ADD_TO_BATCH_SIZE$)/\'' \
    + ' -e \'s/%HOOK3%//\'' \
    + ' -e \'s/%HOOK4%/#define NUMBER_OF_WORKERS $WORKERS$/\'' \
    + ' -e \'s/%HOOK5%//\'' \
    + ' -e \'s/%HOOK6%/#define BATCH_MODEL_ACCURACY_EXPERIMENTS/\'' \
    + ' -e \'s/%PESO_IMPLEMENTATION%/farm/\'' \
    + ' -e \'s/%PESO_SLEEP%/peso_sleep(INTERARRIVAL_TIME_NS);/\'' \
    + ' template_$APP_NAME$.h> $APP_NAME$.h'


sed_command_for_throughput_experiments = 'sed ' \
    + ' -e \'s/%INTERARRIVAL_TIME_NS%/$INTERARRIVAL_TIME_NS$/\'' \
    + ' -e \'s/%INPUT_VECTOR_SIZE%/$INPUT_VECTOR_SIZE$/\'' \
    + ' -e \'s/%RELATIVE_DEADLINE%/$RELATIVE_DEADLINE$/\'' \
    + ' -e \'s/%WCET%/$WCET$/\'' \
    + ' -e \'s/%DATA_TYPE%/$DATA_TYPE$/\'' \
    + ' -e \'s/%HOOK%//\'' \
    + ' -e \'s/%HOOK2%/#define BATCH_SIZE $BATCH_SIZE$/\'' \
    + ' -e \'s/%HOOK3%/#define NUMBER_OF_WORKERS $WORKERS$/\'' \
    + ' -e \'s/%HOOK4%//\'' \
    + ' -e \'s/%HOOK5%/#define THROUGHPUT_EXPERIMENTS/\'' \
    + ' -e \'s/%HOOK6%//\'' \
    + ' -e \'s/%PESO_IMPLEMENTATION%/$PESO_IMPLEMENTATION$/\'' \
    + ' -e \'s/%PESO_SLEEP%//\'' \
    + ' template_$APP_NAME$.h> $APP_NAME$.h'


# This prepares the file that contains the main function
sed_command_for_farm_xc = 'sed '\
    + ' -e \'s/%APP_NAME%/$APP_NAME$/\''\
    + ' -e \'s/%DIR%/$DIR$/\''\
    + ' template_farm.temp> farm.xc'


def create_app_for_demo_purposes(app_name,
                                 period,
                                 input_size,
                                 relative_deadline,
                                 worker_wcet,
                                 batch_size,
                                 workers):
    sed_command = sed_command_for_demo_code \
                    .replace('$PERIOD$',               str(period)) \
                    .replace('$INPUT_VECTOR_SIZE$',    str(input_size)) \
                    .replace('$RELATIVE_DEADLINE$',    str(relative_deadline)) \
                    .replace('$WORKER_WCET$',          str(worker_wcet)) \
                    .replace('$BATCH_SIZE$',           str(batch_size)) \
                    .replace('$WORKERS$',              str(workers)) \
                    .replace('$APP_NAME$',             app_name)

    p1 = subprocess.Popen(sed_command,
                          shell=True,
                          cwd='/home/paul/phd/papers/Realtime/peso_workspace/peso/src/demo')
    p2 = subprocess.Popen(sed_command_for_farm_xc
                          .replace('$APP_NAME$', app_name)
                          .replace('$DIR$', '..\/demo\/'),
                          shell=True,
                          cwd='/home/paul/phd/papers/Realtime/peso_workspace/peso/src/')
    return p1.wait() == 0 and p2.wait() == 0


def create_app_for_comparison_with_hand_implementations(app_name,
                                                        period,
                                                        input_size,
                                                        batch_size,
                                                        workers,
                                                        exp_type):
    sed_command = sed_command_for_hand_implemented_code \
                    .replace('$INTERARRIVAL_TIME_NS$', str(period)) \
                    .replace('$INPUT_SIZE$',           str(input_size)) \
                    .replace('$BATCH_SIZE$',           str(batch_size)) \
                    .replace('$WORKERS$',              str(workers)) \
                    .replace('$APP_NAME$',             app_name)

    if exp_type == 'throughput':
        sed_command = sed_command.replace('$EXPIREMENT_TYPE$', 'THROUGHPUT_EXPERIMENTS')
    elif exp_type == 'batch_size_accuracy':
        sed_command = sed_command.replace('$EXPIREMENT_TYPE$', 'BATCH_MODEL_ACCURACY_EXPERIMENTS')
    else:
        print('ERROR: Unrecognised experiment type')
        exit(0)

    p1 = subprocess.Popen(sed_command,
                          shell=True,
                          cwd='/home/paul/phd/papers/Realtime/peso_workspace/peso/src/benchmarks/hand_implementations')
    p2 = subprocess.Popen(sed_command_for_farm_xc
                          .replace('$APP_NAME$', app_name)
                          .replace('$DIR$', 'hand_implementations\/'),
                          shell=True,
                          cwd='/home/paul/phd/papers/Realtime/peso_workspace/peso/src/')
    return p1.wait() == 0 and p2.wait() == 0


# This is used to test if a DOP + batch size combination is viable i.e. if results are delivered within the deadline
def create_app_for_throughput_heatmap_experiments(app_name,
                                                  period,
                                                  input_size,
                                                  relative_deadline,
                                                  workers,
                                                  worker_wcet,
                                                  batch_size,
                                                  use_pipeline=False,
                                                  data_type="int"):
    if use_pipeline:
        peso_implementation_name = 'pipeline' if batch_size != 1 else 'pipeline_without_batching'
    else:
        peso_implementation_name = 'farm'     if batch_size != 1 else 'farm_without_batching'
    p1 = subprocess.Popen(sed_command_for_throughput_heatmap_experiments
                          .replace('$INTERARRIVAL_TIME_NS$', str(period))
                          .replace('$INPUT_VECTOR_SIZE$',    str(input_size))
                          .replace('$RELATIVE_DEADLINE$',    str(relative_deadline))
                          .replace('$BATCH_SIZE$',           str(batch_size))
                          .replace('$WORKERS$',              str(workers))
                          .replace('$WCET$',                 str(worker_wcet))
                          .replace('$DATA_TYPE$',            str(data_type))
                          .replace('$PESO_IMPLEMENTATION$',  peso_implementation_name)
                          .replace('$APP_NAME$',             app_name),
                          shell=True,
                          cwd='/home/paul/phd/papers/Realtime/peso_workspace/peso/src/benchmarks')
    p2 = subprocess.Popen(sed_command_for_farm_xc
                          .replace('$APP_NAME$', app_name)
                          .replace('$DIR$', ''),
                          shell=True,
                          cwd='/home/paul/phd/papers/Realtime/peso_workspace/peso/src/')
    return p1.wait() == 0 and p2.wait() == 0


def create_app_for_worker_model_accuracy_experiments(app_name,
                                                     period,
                                                     input_size,
                                                     relative_deadline,
                                                     worker_wcet,
                                                     batch_size,
                                                     workers,
                                                     subtract_from_dop,
                                                     data_type="int"):
    p1 = subprocess.Popen(sed_command_for_worker_model_accuracy_experiments
                          .replace('$INTERARRIVAL_TIME_NS$', str(period))
                          .replace('$INPUT_VECTOR_SIZE$',    str(input_size))
                          .replace('$RELATIVE_DEADLINE$',    str(relative_deadline))
                          .replace('$SUBTRACT_FROM_DOP$',    str(subtract_from_dop))
                          .replace('$WCET$',                 str(worker_wcet))
                          .replace('$DATA_TYPE$', str(data_type))
                          .replace('$BATCH_SIZE$',           str(batch_size))
                          .replace('$WORKERS$',              str(workers))
                          .replace('$APP_NAME$',             app_name),
                          shell=True,
                          cwd='/home/paul/phd/papers/Realtime/peso_workspace/peso/src/benchmarks')

    p2 = subprocess.Popen(sed_command_for_farm_xc
                          .replace('$APP_NAME$', app_name)
                          .replace('$DIR$', ''),
                          shell=True,
                          cwd='/home/paul/phd/papers/Realtime/peso_workspace/peso/src/')

    return p1.wait() == 0 and p2.wait() == 0


def create_app_for_batch_size_accuracy_experiments(app_name,
                                                   period,
                                                   input_size,
                                                   relative_deadline,
                                                   worker_wcet,
                                                   batch_size,
                                                   workers,
                                                   add_to_batch_size=0,
                                                   data_type="int"):
    p1 = subprocess.Popen(sed_command_for_batch_size_accuracy_experiments
                          .replace('$INTERARRIVAL_TIME_NS$', str(period))
                          .replace('$INPUT_VECTOR_SIZE$',    str(input_size))
                          .replace('$RELATIVE_DEADLINE$',    str(relative_deadline))
                          .replace('$ADD_TO_BATCH_SIZE$',    str(add_to_batch_size))
                          .replace('$WCET$',                 str(worker_wcet))
                          .replace('$BATCH_SIZE$',           str(batch_size))
                          .replace('$DATA_TYPE$',            str(data_type))
                          .replace('$WORKERS$',              str(workers))
                          .replace('$APP_NAME$',             app_name),
                          shell=True,
                          cwd='/home/paul/phd/papers/Realtime/peso_workspace/peso/src/benchmarks')

    p2 = subprocess.Popen(sed_command_for_farm_xc
                          .replace('$APP_NAME$', app_name)
                          .replace('$DIR$', ''),
                          shell=True,
                          cwd='/home/paul/phd/papers/Realtime/peso_workspace/peso/src/')

    return p1.wait() == 0 and p2.wait() == 0


def create_app_for_throughput_experiments(app_name,
                                          period,
                                          input_vector_size,
                                          relative_deadline,
                                          wcet,
                                          workers,
                                          with_batching,
                                          batch_size,
                                          use_pipeline=False,
                                          data_type="int"):
    if use_pipeline:
        peso_implementation_name = 'pipeline' if with_batching else 'pipeline_without_batching'
    else:
        peso_implementation_name = 'farm' if with_batching else 'farm_without_batching'
    p1 = subprocess.Popen(sed_command_for_throughput_experiments
                          .replace('$INTERARRIVAL_TIME_NS$', str(period))
                          .replace('$INPUT_VECTOR_SIZE$',    str(input_vector_size))
                          .replace('$RELATIVE_DEADLINE$',    str(relative_deadline))
                          .replace('$WCET$',                 str(wcet))
                          .replace('$DATA_TYPE$',            str(data_type))
                          .replace('$WORKERS$',              str(workers))
                          .replace('$BATCH_SIZE$',           str(batch_size))
                          .replace('$NEWLINE',               '\n')
                          .replace('$PESO_IMPLEMENTATION$',  peso_implementation_name)
                          .replace('$APP_NAME$',             app_name),
                          shell=True,
                          cwd='/home/paul/phd/papers/Realtime/peso_workspace/peso/src/benchmarks')
    p2 = subprocess.Popen(sed_command_for_farm_xc
                          .replace('$APP_NAME$', app_name)
                          .replace('$DIR$', ''),
                          shell=True,
                          cwd='/home/paul/phd/papers/Realtime/peso_workspace/peso/src/')
    return p1.wait() == 0 and p2.wait() == 0