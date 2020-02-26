#!/usr/bin/env python3

'''
This script generates a heatmap for the motivating example section.
The heat map has batch size on the y-axis and DOP on the x-axis.
The values in the fields of the heatmap show the max throughput in tasks per time microsecond.
'''

import getopt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sys

import models

from orm_classes import Base
from sqlalchemy import create_engine


def main(argv):
    opts, args = getopt.getopt(argv, 'ht:p:w:', ['type=', 'path=', 'worker_wcet='])
    print(opts)
    if opts[0][0] == '-h':
        print('Options:')
        print('-h')
        print('-t [heatmap type]')
        print('-p [output]')
        print('-w [worker WCET]')
    elif opts[0][0] in ('-t', '--type'):
        if opts[0][1] == 'measured':
            plot_measurements(opts[1][1])
        if opts[0][1] == 'measured_only_with_job_farm_and_batching':
            plot_measurements(opts[1][1], only_batching=True, only_job_farm=True)
        elif opts[0][1] == 'computed':
            plot_computed_minimum_period(opts[1][1], opts[2][1])
        else:
            print('Could not recognise the heatmap type.')

        print('Done.')


def plot_computed_minimum_period(path, worker_wcet):
    t_w_f = int(worker_wcet)
    min_worker_count = 1
    max_worker_count = 6
    deadline         = 15000

    data_set_dict = models.compute_min_sustainable_periods(
        t_w_f,
        min_worker_count,
        max_worker_count,
        deadline
    )
    df = pd.DataFrame(data=data_set_dict)
    plot(df, path, 'computed')


def plot_measurements(path, only_batching=False, only_job_farm=False):
    # Setup SQLAlchemy
    engine = create_engine('sqlite:////home/paul/phd/my_papers/realtime/scripts/rt.db')
    Base.metadata.bind = engine
    connection = engine.raw_connection()

    df = pd.read_sql('Select * From ThroughputHeatmapSample Where sample_application_name is '
                     '"reduction" and input_size = 30 and '
                     'relative_deadline = 15000 and '
                     'data_type like \'short\' and '
                     'sample = 1;',
                     connection)

    plot(df, path, 'measured', only_batching, only_job_farm)


def plot(df, path, type, only_batching=False, only_job_farm=False):
    # df['throughput'] = df['min_period'].apply(lambda x: 1000.0 / float(x))
    df = df[['dop', 'batch_size', 'min_period']]
    df = df.sort_values(['dop', 'batch_size'], ascending=True)
    df = df.pivot(index='batch_size', columns='dop', values='min_period')
    # Add the top row
    if type == 'measured':
        df.loc[len(df) + 1] = [np.nan for _ in range(len(df.columns))]

    yticklabels = [y_label for y_label in range(2, len(df) + 2)]
    if only_batching:
        df.drop([1])
    else:
        yticklabels = ['No batch.'] + yticklabels

    xticklabels = [x_label for x_label in range(2, len(df.columns) + 1)]
    if only_job_farm:
        del df[1]
    else:
        xticklabels = ['No farm'] + xticklabels

    print(df)

    annot = df.copy()
    annot.loc[len(df)] = ['-' for _ in range(len(df.columns))]
    ax = sns.heatmap(df,
                     annot=annot,
                     #cmap=sns.diverging_palette(133, 255, l=60, n=25),
                     cmap=sns.color_palette('BuGn_r', 100),
                     fmt='g',
                     xticklabels=xticklabels,
                     yticklabels=yticklabels,
                     cbar_kws = dict(use_gridspec=False,
                                     location="bottom",
                                     label=r'Min. Sustainable Period (ns)'))
    ax.set_facecolor('xkcd:stone')
    ax.invert_yaxis()
    ax.set_xlabel('Number of Workers')
    ax.set_ylabel('Batch Size')
    ax.tick_params(axis=u'both', which=u'both', length=0)  # Remove ticks
    '''ax.set_title('Method: computed\n' +
                 'Data type: int\n' +
                 'Deadline: 20000ns\n' +
                 'Integers reduced: 30')'''

    #plt.show()
    plt.savefig(path, bbox_inches='tight')


if __name__ == '__main__':
    main(sys.argv[1:])