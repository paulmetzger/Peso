import math

T_D    = 150   # Dispatcher code
T_C    = 130   # Time to send an integer from A to B (includes 3 comm. instruction on the receiver and sender side)
T_W_C  = 250
T_W_SB = 10    # Farm internal code that is executed once before and after each batch
T_W_B  = 80    # Code that implements batching and is executed once per job
T_A    = 230   # Aggregator code that is executed once per batch
T_U    = 180   # Code that unbatches the results of a job


def _compute_dop(t_w_c, t_w_f, t_w_b, t_w_sb, period, b):
    '''

    @param t_w_se: WCET for code executed at the start and end of a batch
    @param t_w:    WCET for processing a single task in a worker
    @param period: period
    @param b:      batch size

    @return:       optimal number of workers
    '''
    # return math.ceil(((1/period) * (t_w_se + t_w * b)) / b) | old (changed on: 30/04/2019)
    return math.ceil(
        ((t_w_c + t_w_sb) / (b * period))
        +
        ((t_w_f + t_w_b) / period)
    )


def _compute_batch_size(t_w_b, t_w_f, t_d, t_a, t_c, t_u, period, d):
    '''

    @param t_w_se:     WCET for code executed at the start and end of a batch
    @param t_w:        WCET for processing a single task in a worker
    @param t_d:
    @param t_a:
    @param t_a_f:
    @param t_c:
    @param period:     period
    @param t_consumer:
    @param d:          d

    @return:           optimal batch size
    '''
    c_o = t_d + 2 * t_c + t_a

    return math.floor((d + period - c_o - t_u)/(period + t_w_b + t_w_f))


def _compute_min_sustainable_period(t_w_f, t_w_b, t_w_sb, t_w_c, m, b):
    return math.ceil(
        (t_w_c + t_w_sb + (t_w_f + t_w_b) * b) / (b * m)
    )


def _compute_response_time(t_a, t_c, t_d, t_w_f, t_w_b, t_u, b, period):
    return b * (period + t_w_b + t_w_f) - period + t_d + 2 * t_c + t_a + t_u


def compute_min_sustainable_periods(t_w_f, min_m, max_m, deadline):
    data_set = {'dop': [], 'batch_size': [], 'min_period': []}
    for m in range(min_m, max_m + 1):
        wcets = _compute_wcets(m, t_w_f)
        found_non_viable_batch_size = False
        b = 0
        while not found_non_viable_batch_size:
            b += 1
            data_set['dop'].append(m)
            data_set['batch_size'].append(b)
            min_sustainable_period = _compute_min_sustainable_period(
                wcets['t_w_f'],
                wcets['t_w_b'],
                wcets['t_w_sb'],
                wcets['t_w_c'],
                m,
                b
            )
            response_time = _compute_response_time(
                wcets['t_a'],
                wcets['t_c'],
                wcets['t_d'],
                wcets['t_w_f'],
                wcets['t_w_b'],
                wcets['t_u'],
                b,
                min_sustainable_period
            )
            found_non_viable_batch_size = response_time > deadline
            data_set['min_period'].append(None if found_non_viable_batch_size else min_sustainable_period)

    return data_set


def _compute_wcets(workers, t_w_f):
    factor = 1.0
    if workers == 4:
        factor = 1.2
    elif workers == 5:
        factor = 1.4
    elif workers == 6:
        factor = 1.6
    elif workers > 6:
        print('ERROR: Too many cores required')
        exit(0)

    wcets = dict(
        {'t_d':    T_D * factor,
         't_c':    T_C * factor,
         't_a':    T_A * factor,
         't_w_b':  T_W_B * factor,
         't_w_c':  T_W_C * factor,
         't_w_f':  t_w_f * factor,
         't_w_sb': T_W_SB * factor,
         't_u':    T_U * factor})

    return wcets


def compute_optimal_dop_and_batch_size(t_w_f, period, d):
    searching = True
    workers   = 3
    b_opt     = -1
    dop_opt   = -1

    while searching:
        wcets   = _compute_wcets(workers, int(t_w_f))
        b_opt   = _compute_batch_size(wcets['t_w_b'],
                                      wcets['t_w_f'],
                                      wcets['t_d'],
                                      wcets['t_a'],
                                      wcets['t_c'],
                                      wcets['t_u'],
                                      int(period),
                                      int(d))
        dop_opt = _compute_dop(wcets['t_w_c'],
                               wcets['t_w_f'],
                               wcets['t_w_b'],
                               wcets['t_w_sb'],
                               int(period),
                               b_opt)

        # print('DEBUG| workers {}'.format(workers))
        # print('DEBUG| b_opt {}'  .format(b_opt))
        # print('DEBUG| dop_opt {}'.format(dop_opt))
        # print('---------')

        if dop_opt <= workers:
            searching = False
        else:
            workers += 1

            if workers > 6:
                print('Could not find a parameter set')
                exit(0)

    print('Computed parameters | Worker count: {} Batch size: {}'.format(dop_opt, b_opt))

    return b_opt, dop_opt


def main():
    print(compute_optimal_dop_and_batch_size(830, 250, 10000))


if __name__ == '__main__':
    main()