#ifndef MATRIX_MULTIPLICATION_H_
#define MATRIX_MULTIPLICATION_H_

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

#if INPUT_VECTOR_SIZE == 15
//Matrix:
//1 2 0 0 0 0 0 0 0 0 0 0 0 0 0
//0 1 3 0 0 0 0 0 0 0 0 0 0 0 0
//0 0 1 4 0 0 0 0 0 0 0 0 0 0 0
//0 0 0 1 5 0 0 0 0 0 0 0 0 0 0
//0 0 0 0 1 6 0 0 0 0 0 0 0 0 0
//0 0 0 0 0 1 7 0 0 0 0 0 0 0 0
//0 0 0 0 0 0 1 8 0 0 0 0 0 0 0
//0 0 0 0 0 0 0 1 9 0 0 0 0 0 0
//0 0 0 0 0 0 0 0 1 0 0 0 0 0 0
//0 0 0 0 0 0 0 0 0 2 0 0 0 0 0
//0 0 0 0 0 0 0 0 0 0 2 1 0 0 0
//0 0 0 0 0 0 0 0 0 0 0 2 2 0 0
//0 0 0 0 0 0 0 0 0 0 0 0 2 2 0
//0 0 0 0 0 0 0 0 0 0 0 0 0 2 3
//0 0 0 0 0 0 0 0 0 0 0 0 0 0 1
int a[27]           = {1, 2, 1, 3, 1, 4, 1, 5, 1, 6, 1, 7, 1, 8, 1, 9, 1, 2, 2, 1, 2, 2, 2, 2, 2, 3, 1};
unsigned int ia[16] = {0, 2, 4, 6, 8, 10, 12, 14, 16, 17, 18, 20, 22, 24, 26, 27};
unsigned int ja[27] = {0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 10, 11, 11, 12, 12, 13, 13, 14, 14};

#elif INPUT_VECTOR_SIZE == 10
int a[11]           = {1, 5, 8, 3, 6, 1, 1, 1, 1, 1, 1};
unsigned int ia[11] = {0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11};
unsigned int ja[11] = {0, 0, 1, 2, 1, 4, 5, 6, 7, 8, 9};
#endif

typedef struct data {
    int input_vector[INPUT_VECTOR_SIZE];
    int output_vector[INPUT_VECTOR_SIZE];
    int timestamp;
} data_t;
prepare_farm(data_t, RETENTION_TIME, INTERARRIVAL_TIME_NS)

consumer(
    consumer_func, //Consumer name
    data_t,
    sink += access_data()->output_vector[0];
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
    for (int row = 0; row < INPUT_VECTOR_SIZE; ++row) {
        int temp_result = 0;
        for (int index = ia[row]; index <= ia[row + 1] - 1; ++index) {
            temp_result += a[index] * access_data()->input_vector[ja[index]];
        }
        access_data()->output_vector[row] = temp_result;
    }
)

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

int sparse_matrix_vector_multiplication_benchmark() {
    start_farm();
    return 0;
}

#endif /* REDUCTION_H_ */
