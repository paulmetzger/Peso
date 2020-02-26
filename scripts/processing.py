import math


def parse_output_to_dict(out):
    print('__parse_out_to_dict__')
    print(out)
    setup = dict()
    results = []
    outputs = out\
        .replace('-\n', '')\
        .replace('-', '')\
        .replace('- ', '')\
        .replace('-', '')\
        .replace('\t', '')\
        .replace(' Start Peso Task Farm ', '')\
        .split('\n')
    try:
        count = 1
        for output in outputs:
            if count == 1:
                setup['dop'] = int(output.split(' ')[5])
            elif count == 2:
                setup['batch_size'] = int(output.split(' ')[3])
            elif count == 3:
                setup['buffer_size'] = int(output.split(' ')[3])
            elif output is not '':
                key, value = output.split(': ')
                results.append(int(value))
            count += 1
    except Exception as e:
        print('Caught an exception')
        print(e)
        print(output)
        raise

    return setup, results # results contains all measurements


def compute_interarrival_time(out, batch_size, dop):
    slice_to_reduce = out[dop * batch_size * (-1):]
    return math.ceil(sum(slice_to_reduce) / len(slice_to_reduce))


def check_if_deadline_has_been_missed(out, deadline):
    return any(sample > deadline for sample in out)