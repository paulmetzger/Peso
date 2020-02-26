/*
 * reduction.h
 *
 *  Created on: 18 May 2018
 *      Author: Paul Metzger
 */


#ifndef REDUCTION_H_
#define REDUCTION_H_

#include <stdlib.h>

#include <peso/%PESO_IMPLEMENTATION%.h>
#include <peso/utils.h>

#define INTERARRIVAL_TIME_NS %INTERARRIVAL_TIME_NS%
#define INPUT_VECTOR_SIZE %INPUT_VECTOR_SIZE%
#define RELATIVE_DEADLINE %RELATIVE_DEADLINE%
#define WCET %WCET%
#define RETENTION_TIME (110 * 1000)

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

typedef struct data {
    %DATA_TYPE% input_vector[INPUT_VECTOR_SIZE];
    int result;
    int timestamp;
} data_t;
prepare_farm(data_t, RETENTION_TIME, INTERARRIVAL_TIME_NS)

consumer(
    consumer_func, //Consumer name
    data_t,
    //Wo do this to avoid unrealistic compiler optimisations
    sink += access_data()->result;
#if defined(BATCH_MODEL_ACCURACY_EXPERIMENTS)
    //--- Code that can be used to check if results are delivered in time ---
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
    %DATA_TYPE% result = 0;

    for (size_t i = 0; i < INPUT_VECTOR_SIZE; ++i) {
        DEBUG("WORKER: index: %d, input: %d\n", i, access_data()->input_vector[i]);
        result += access_data()->input_vector[i];
    }
    access_data()->result = result;)

producer(
    producer_func, //Producer name

    %PESO_SLEEP%

#if defined(BATCH_MODEL_ACCURACY_EXPERIMENTS)
    //--- Code that can be used to check if results are delivered in time ---
    t :> prep_data()->timestamp;
#endif
    submit_data();

        //--- Code that can be used to check if the task farm is overloaded ---
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

int reduction_benchmark() {
    start_farm();
    return 0;
}

#endif /* REDUCTION_H_ */
