#!/usr/bin/env python3

'''
Script to generate figures that demonstrate the throughput improvements with batching.
It either shows speed up in terms of throughput or throughput with and without batching side by side.

Code that shows throughput with and without batching side by side is commented out at the moment.
'''

import getopt
import matplotlib.pyplot as plt
import pandas as pd
import sys

from orm_classes import Base
from sqlalchemy import create_engine

BAR_PLOT_HEIGHTS = 1.5


def plot_hand_implementation_comparison(connection):
    df_hand_implementation = pd.read_sql(
        'Select sample_application_name, input_size, relative_deadline, worker_wcet, dop, AVG(min_period) AS min_period ' \
        'FROM ThroughputWithHandImplementations ' \
        'WHERE is_hand_implementation = 1 ' \
        'GROUP BY sample_application_name, input_size, relative_deadline, worker_wcet, dop', connection)
    df_peso                = pd.read_sql(
        'Select sample_application_name, input_size, relative_deadline, worker_wcet, dop, AVG(min_period) AS min_period ' \
        'From ThroughputWithHandImplementations ' \
        'Where is_hand_implementation = 0 ' \
        'GROUP BY sample_application_name, input_size, relative_deadline, worker_wcet, dop', connection)

    df = df_peso.join(
        df_hand_implementation.set_index(['sample_application_name',
                                          'input_size',
                                          'relative_deadline',
                                          'worker_wcet',
                                          'dop']),
        lsuffix='_peso',
        rsuffix='_hand_implementation',
        on=['sample_application_name',
            'input_size',
            'relative_deadline',
            'worker_wcet',
            'dop']
    )
    df = df.sort_values(['sample_application_name', 'input_size'], ascending=True)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)

        sample_application_names = []
        peso_throughput          = []
        hand_impl_throughput     = []

        for index, row in df.iterrows():
            sample_application_names.append((row['sample_application_name'] + '\ni' + str(row['input_size']))
                                            .replace('reduction', 'RED')
                                            .replace('sparse_matrix_vector_multiplication', 'SMV')
                                            .replace('dense_matrix_vector_multiplication', 'DMV'))
            peso_throughput.append(row['min_period_peso'] / 1000.0)
            hand_impl_throughput.append(row['min_period_hand_implementation'] / 1000.0)

        '''for i in range(10):
            sample_application_names.append('TBD')
            peso_throughput.append(0.1)
            hand_impl_throughput.append(0.1)'''

        df_to_plot = pd.DataFrame({
            'Peso': peso_throughput,
            'Hand impl.': hand_impl_throughput},
            index=sample_application_names)

        # Debugging output
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(df_to_plot)

        df_to_plot.plot(kind='bar',
                        figsize=(6.5, BAR_PLOT_HEIGHTS),
                        edgecolor='none',
                        color=['#0165fc', '#f1a340'],
                        legend=True)

        ax = plt.axes()
        ax.plot([1], [1])
        ax.yaxis.grid()
        ax.tick_params(axis=u'both', which=u'both', length=0)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#6F6F6F')
        ax.spines['left'].set_color('#6F6F6F')
        ax.set_ylabel('Minimum\nperiod'
                      ' ($\mu$s)')
        plt.axis('tight')
        plt.ylim([0, 1.7])
        plt.yticks([0, 0.85, 1.7])
        plt.xlim([-ax.patches[0].get_width(), 5 + ax.patches[0].get_width()])
        plt.gcf().subplots_adjust(bottom=0.4)  # Make sure the x labels are not cut off
        leg = plt.legend()
        leg.get_frame().set_linewidth(0.0)  # Remove the frame around the legend
        plt.legend(bbox_to_anchor=(0.56, 1.3), loc=2, borderaxespad=0., ncol=2, frameon=False)

        # plt.show()
        plt.savefig('../paper/figures/eval_implementation_overhead.pdf', bbox_inches='tight')


def plot_dop_model_accuracy_experiments(connection):
    # Load data from the DB into pandas data frames
    df_baseline = pd.read_sql('Select * From DOPModelAccuracySample Where is_oracle = 0 and sample = 1',
                              connection)
    df_oracle   = pd.read_sql('Select * From DOPModelAccuracySample Where is_oracle = 1 and sample = 1',
                              connection)

    # Prepare data that will be plotted
    df = df_baseline.join(
        df_oracle.set_index(['sample_application_name',
                             'input_size',
                             'relative_deadline',
                             'worker_wcet',
                             'period']),
        lsuffix='_baseline',
        rsuffix='_oracle',
        on=['sample_application_name',
            'input_size',
            'relative_deadline',
            'worker_wcet',
            'period']
    )
    df = df.sort_values(['sample_application_name', 'input_size', 'period'], ascending=True)
    # Debugging output
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)

        # Create data arrays
        sample_application_names = []
        baseline_dop = []
        oracle_dop = []

        for index, row in df.iterrows():
            sample_application_names.append((row['sample_application_name'] + '\ni' + str(row['input_size']) + ' p' +
                                             str(float(row['period']) / 1000.0).replace('.0', ''))
                                            .replace('reduction', 'RED')
                                            .replace('sparse_matrix_vector_multiplication', 'SMV')
                                            .replace('dense_matrix_vector_multiplication', 'DMV'))
            baseline_dop.append(row['dop_baseline'])
            oracle_dop.append(row['dop_oracle'])

        '''for i in range(5):
            sample_application_names.append('TBD')
            baseline_dop.append(0.1)
            oracle_dop.append(0.1)'''

        df_to_plot = pd.DataFrame({'Our analytical framework': baseline_dop,
                                   'Experimental results': oracle_dop},
                                  index=sample_application_names)

        # Debugging output
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(df_to_plot)

        df_to_plot.plot(kind='bar',
                        figsize=(14, BAR_PLOT_HEIGHTS),
                        edgecolor='none',
                        color=['#99d594', '#f1a340'],
                        legend=True)
        ax = plt.axes()
        ax.plot([1], [1])  # Remove ticks
        ax.yaxis.grid()  # Show horizontal lines for better readability
        ax.tick_params(axis=u'both', which=u'both', length=0)  # Remove ticks
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#6F6F6F')
        ax.spines['left'].set_color('#6F6F6F')
        ax.set_ylabel('Worker\ncore count')
        # plt.xticks(rotation='horizontal')
        plt.yticks([0, 3, 6])
        plt.axis('tight')  # Remove margins on the very left and very right
        plt.ylim([0, 6])
        plt.xlim([-ax.patches[0].get_width(), 17 + ax.patches[0].get_width()])
        plt.gcf().subplots_adjust(bottom=0.4)  # Make sure the x labels are not cut off
        leg = plt.legend()
        leg.get_frame().set_linewidth(0.0)  # Remove the frame around the legend
        plt.legend(bbox_to_anchor=(0.6, 1.3), loc=2, borderaxespad=0., ncol=2, frameon=False)
        #plt.show()
        plt.savefig('../paper/figures/dop_model_oracle_study.pdf', bbox_inches='tight')


def plot_batch_size_model_accuracy_experiments(connection):
    # Load data from the DB into pandas data frames
    df_baseline = pd.read_sql('Select * From BatchSizeModelAccuracySample Where is_oracle = 0 and sample = 1',
                              connection)
    df_oracle   = pd.read_sql('Select * From BatchSizeModelAccuracySample Where is_oracle = 1 and sample = 1',
                              connection)

    # Prepare data that will be plotted i.e. the oracle and the 'our model' data set
    df = df_baseline.join(
        df_oracle.set_index(['sample_application_name',
                             'input_size',
                             'relative_deadline',
                             'worker_wcet',
                             'period']),
        lsuffix='_baseline',
        rsuffix='_oracle',
        on=['sample_application_name',
            'input_size',
            'relative_deadline',
            'worker_wcet',
            'period']
    )
    df = df.sort_values(['sample_application_name', 'input_size', 'period'], ascending=True)
    # Debugging output
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)

    # Create data arrays
    sample_application_names = []
    baseline_batch_size      = []
    oracle_batch_size        = []

    for index, row in df.iterrows():
        sample_application_names.append((row['sample_application_name'] + '\ni' + str(row['input_size']) + ' p' +
                                         str(float(row['period']) / 1000.0).replace('.0', ''))
                                        .replace('reduction', 'RED')
                                        .replace('sparse_matrix_vector_multiplication', 'SMV')
                                        .replace('dense_matrix_vector_multiplication',  'DMV'))
        baseline_batch_size.append(row['batch_size_baseline'])
        oracle_batch_size.append(row['batch_size_oracle'])

    '''for i in range(10):
        sample_application_names.append('TBD')
        baseline_batch_size.append(0.1)
        oracle_batch_size.append(0.1)'''

    df_to_plot = pd.DataFrame({'Our analytical framework': baseline_batch_size,
                               'Experimental results': oracle_batch_size},
                              index=sample_application_names)

    # Debugging output
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df_to_plot)

    bars = df_to_plot.plot(kind='bar',
                    figsize=(14, BAR_PLOT_HEIGHTS),
                    edgecolor='none',
                    color=['#99d594', '#f1a340'],
                    legend=False)

    # fig = plt.figure(figsize=(4, 5), dpi=100)
    ax = plt.axes()
    ax.plot([1], [1])  # Remove ticks
    ax.yaxis.grid()  # Show horizontal lines for better readability
    ax.tick_params(axis=u'both', which=u'both', length=0)  # Remove ticks
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#6F6F6F')
    ax.spines['left'].set_color('#6F6F6F')
    ax.set_ylabel('Batch size')
    # plt.xticks(rotation='horizontal')
    plt.yticks([0, 6, 12])
    plt.axis('tight')  # Remove margins on the very left and very right
    plt.ylim([0, 12])
    plt.xlim([-ax.patches[0].get_width(), 17 + ax.patches[0].get_width()])
    plt.gcf().subplots_adjust(bottom=0.4)  # Make sure the x labels are not cut off
    # leg = plt.legend()
    # leg.get_frame().set_linewidth(0.0) # Remove the frame around the legend
    # plt.legend(bbox_to_anchor=(0.6, 1.3), loc=2, borderaxespad=0., ncol=2, frameon=False)
    # plt.show()
    plt.savefig('../paper/figures/batch_size_model_oracle_study.pdf', bbox_inches='tight')


def plot_max_throughput_experiments(connection):
    # Load data from the DB into pandas data frames
    df_with_batching    = pd.read_sql('Select * From ThroughputSample Where with_batching = 1 and sample = 1;', connection)
    df_without_batching = pd.read_sql('Select * From ThroughputSample Where with_batching = 0 and sample = 1;', connection)

    # Prepare data that will be plotted
    df = df_with_batching.join(
        df_without_batching.set_index(['input_size', 'relative_deadline', 'worker_wcet', 'dop']),
        lsuffix='_with',
        rsuffix='_without',
        on=['input_size', 'relative_deadline', 'worker_wcet', 'dop'])
    # pd.to_numeric(df['batch_size_with'])
    df = df.sort_values(['experiment_name_with', 'input_size', 'batch_size_with'], ascending=True)

    # Create data arrays
    # throughput_with_batching = []
    # throughput_without_batching = []
    low_throughput_improvement = []
    low_improv_sample_application_name = []
    high_throughput_improvement  = []
    high_improv_sample_application_name = []

    for index, row in df.iterrows():
        sample_application_name = ((row['experiment_name_with'] + '\ni' + str(row['input_size'])
                                        + ' b' + str(row['batch_size_with']))
                                       .replace('reduction', 'RED')
                                       .replace('sparse_matrix_vector_multiplication', 'SMV')
                                       .replace('dense_matrix_vector_multiplication', 'DMV'))
        # throughput_with_batching.append(1000.0 / float(row['min_interarrival_time_with']))
        # throughput_without_batching.append(1000.0 / float(row['min_interarrival_time_without']))
        # Compute speed up in %
        throughput_improvement = (1 - float(row['min_interarrival_time_with']) / float(row['min_interarrival_time_without'])) * 100.0
        if throughput_improvement > 15.0:
            high_throughput_improvement.append(throughput_improvement)
            high_improv_sample_application_name.append(sample_application_name)
        else:
            low_throughput_improvement.append(throughput_improvement)
            low_improv_sample_application_name.append(sample_application_name)

    # Plot data
    '''df_to_plot = pd.DataFrame({'With batching': throughput_with_batching,
                               'Without batching': throughput_without_batching},
                              index=sample_application_name)'''

    high_improv_df_to_plot = pd.DataFrame({'throughput_improvement': high_throughput_improvement},
                                           index=high_improv_sample_application_name)
    low_improv_df_to_plot  = pd.DataFrame({'throughput_improvement': low_throughput_improvement},
                                           index=low_improv_sample_application_name)

    print('High:')
    print(high_improv_df_to_plot)
    print('Low:')
    print(low_improv_df_to_plot)
    for plot_high_throughput in [True, False]:
        (high_improv_df_to_plot if plot_high_throughput else low_improv_df_to_plot).plot(kind='bar',
                                                                                         figsize=(6, BAR_PLOT_HEIGHTS),
                                                                                         edgecolor='none',
                                                                                         color=['#99d594', '#f1a340'],
                                                                                         legend=False)
        ax = plt.axes()
        ax.plot([1], [1])  # Remove ticks
        ax.yaxis.grid()  # Show horizontal lines for better readability
        ax.tick_params(axis=u'both', which=u'both', length=0)  # Remove ticks
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#6F6F6F')
        ax.spines['left'].set_color('#6F6F6F')
        ax.set_ylabel('Period\nImprov. (%)')
        # plt.xticks(rotation='horizontal')
        plt.yticks([0, 25, 50] if plot_high_throughput else [0, 5, 10])
        plt.axis('tight')  # Remove margins on the very left and very right
        plt.ylim([0, 50 if plot_high_throughput else 10])
        plt.xlim([-ax.patches[0].get_width() / 2.0, 7.78 + ax.patches[0].get_width()])
        plt.gcf().subplots_adjust(bottom=0.4)  # Make sure the x labels are not cut off
        # leg = plt.legend()
        # leg.get_frame().set_linewidth(0.0) # Remove the frame around the legend
        #plt.show()
        plt.savefig('../paper/figures/' + ('high' if plot_high_throughput else 'low') + '_throughput.pdf', bbox_inches='tight')


def main(argv):
    # Setup SQLAlchemy
    engine             = create_engine('sqlite:////home/paul/phd/papers/Realtime/scripts/rt.db')
    Base.metadata.bind = engine
    connection         = engine.raw_connection()

    opts, args = getopt.getopt(argv, 'ht:', ['type='])
    if opts[0][0] == '-h':
        print('main.py -t <plot type>')
        print('Available types: max_throughput, batch_size_model_accuracy, dop_model_accuracy, plot_hand_implementation_comparison')
    elif opts[0][0] in ('-t', '--type'):
        if opts[0][1] == 'max_throughput':
            plot_max_throughput_experiments(connection)
        elif opts[0][1] == 'batch_size_model_accuracy':
            plot_batch_size_model_accuracy_experiments(connection)
        elif opts[0][1] == 'dop_model_accuracy':
            plot_dop_model_accuracy_experiments(connection)
        elif opts[0][1] == 'plot_hand_implementation_comparison':
            plot_hand_implementation_comparison(connection)


if __name__ == '__main__':
    main(sys.argv[1:])
