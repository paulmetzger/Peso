/*
 * reduction.h
 *
 *  Created on: 18 May 2018
 *      Author: picard
 */


#ifndef MATRIX_MULTIPLICATION_H_
#define MATRIX_MULTIPLICATION_H_

#include <stdlib.h>

#include <peso/%PESO_IMPLEMENTATION%.h>
//#include <peso/farm.h>
//#include <peso/farm_dummy_for_wcet_measurements_without_batching.h>
//#include <peso/farm_with_fused_scheduler_and_collector.h>
#include <peso/utils.h>

//#define INTERARRIVAL_TIME_NS 754
#define INTERARRIVAL_TIME_NS %INTERARRIVAL_TIME_NS%
//#define INPUT_VECTOR_SIZE 12
#define INPUT_VECTOR_SIZE %INPUT_VECTOR_SIZE%
//#define RELATIVE_DEADLINE 50000
#define RELATIVE_DEADLINE %RELATIVE_DEADLINE%
//#define WCET 780
#define WCET %WCET%
#define RETENTION_TIME (1000 * 110)

#define INTEGER int

//Hook for other templated defines
%HOOK%
%HOOK2%
%HOOK3%
%HOOK4%
%HOOK5%
%HOOK6%

#if defined(THROUGHPUT_EXPERIMENTS)
    int previous_timestamp = -1;
    int current_timestamp = -1;
#endif

#define MEASUREMENTS (10 * NUMBER_OF_WORKERS * BATCH_SIZE)
int timing_results_index = 0;
int timingresults[MEASUREMENTS];
int time_received = -1;
int sink = -1;

INTEGER matrix[10 * 10] =  {1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            5, 8, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 3, 0, 0, 0, 0, 0, 0, 0,
                            0, 6, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 1, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 1, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 1};

typedef struct data {
    int input_vector[INPUT_VECTOR_SIZE];
    int output_vector[INPUT_VECTOR_SIZE];
    int timestamp;
} data_t;
prepare_farm(data_t, RETENTION_TIME, INTERARRIVAL_TIME_NS)


consumer(
    consumer_func, //Consumer name
    data_t,
    //Wo do this to avoid unrealistic compiler optimisations
    sink += access_data()->output_vector[0];
#if defined(BATCH_MODEL_ACCURACY_EXPERIMENTS)
    asm volatile("" ::: "memory");
    t :> time_received;
    timingresults[timing_results_index] = time_received - data->timestamp;
    asm volatile("" ::: "memory");
    ++timing_results_index;
    if(timing_results_index == MEASUREMENTS) {
        for (int i = 0; i < MEASUREMENTS; ++i)
            printf("%d: %d\n", i, timingresults[i] * 10);
        timing_results_index = 0;
        exit(1);
    }
#endif
    )

worker_function(
    worker_func, //Worker function name
    data_t,
    for (int y = 0; y < INPUT_VECTOR_SIZE; ++y) {
        int new_value = 0;
        for (int x = 0; x < INPUT_VECTOR_SIZE; ++x) {
            new_value += matrix[y * INPUT_VECTOR_SIZE + x] * access_data()->input_vector[x];
        }
        access_data()->output_vector[y] = new_value;
    })

producer(
    producer_func, //Producer name
    %PESO_SLEEP%

#if defined(BATCH_MODEL_ACCURACY_EXPERIMENTS)
    //--- Code that can be used to check if results are delivered in time ---
    t :> prep_data()->timestamp;
#endif

    submit_data();
    //for (size_t i = 0; i < INPUT_VECTOR_SIZE; ++i) prep_data()->input_vector[i] = dummy_input;

#if defined(THROUGHPUT_EXPERIMENTS)
    asm volatile("" ::: "memory");
    t :> current_timestamp;
    timingresults[timing_results_index] = current_timestamp - previous_timestamp;
    asm volatile("" ::: "memory");
    previous_timestamp = current_timestamp;
    ++timing_results_index;
    if(timing_results_index == MEASUREMENTS) {
        for (int i = 1; i < MEASUREMENTS; ++i)
            printf("%d: %d\n", i, timingresults[i] * 10);
        timing_results_index = 0;
        exit(1);
    }
#endif
    )

configure_farm(
        farm, //Farm name
        worker_func,
        producer_func,
        consumer_func)

int dense_matrix_vector_multiplication_benchmark() {
    start_farm();
    return 0;
}

#endif
