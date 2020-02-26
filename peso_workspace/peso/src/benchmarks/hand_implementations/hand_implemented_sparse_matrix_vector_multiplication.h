#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

#include <platform.h>

#define _DIVISION_CEIL(DIVIDEND, DIVISOR) \
    (((DIVIDEND) / (DIVISOR)) + (((DIVIDEND) % (DIVISOR)) != 0 ? 1 : 0))

#define _MAX(ARG1, ARG2) \
    ((ARG1) > (ARG2) ? (ARG1) : (ARG2))

#define _CALCULATE_BUFFER_SIZE(RETENTION_TIME, INTERARRIVAL_TIME, BATCH_SIZE) \
    (((_MAX(1, _DIVISION_CEIL(RETENTION_TIME, INTERARRIVAL_TIME)) * BATCH_SIZE) + BATCH_SIZE))

#define _CALCULATE_RING_BUFFER_START_POSITION(BUFFER_SIZE, BATCH_SIZE)\
    ((_DIVISION_CEIL(_DIVISION_CEIL(BUFFER_SIZE, BATCH_SIZE), 2) * BATCH_SIZE))

#define THROUGHPUT_EXPERIMENTS

#define RETENTION_TIME    (100*1000)
#define MEASUREMENTS      (3 * 6 * 5)
#define BATCH_SIZE        5
#define NUMBER_OF_WORKERS 6

const size_t context_buffer_size  = _CALCULATE_BUFFER_SIZE(RETENTION_TIME,
                                                          250,
                                                          5);

int timing_results_index = 0;
int time_received        = -1;
int timingresults[MEASUREMENTS];
int sink                 = -1;

#if 15 == 15
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

#elif 15 == 10
int a[11]           = {1, 5, 8, 3, 6, 1, 1, 1, 1, 1, 1};
unsigned int ia[11] = {0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11};
unsigned int ja[11] = {0, 0, 1, 2, 1, 4, 5, 6, 7, 8, 9};
#endif

struct data {
    int input_vector[15];
    int output_vector[15];
    int timestamp;
};
typedef struct data Data;

unsafe {
    Data context_buffer_safe[_CALCULATE_BUFFER_SIZE(
                             RETENTION_TIME,
                             250,
                             5)];
    Data * unsafe context_buffer = (Data * unsafe) &context_buffer_safe[0];
}

unsafe void consumer_func(chanend receiver[]) {
    size_t context_collector_worker_id     = 0;
    size_t context_collector_current_start = 0;

    while (1) {
        timer t;

        receiver[context_collector_worker_id] :> context_collector_current_start;
        ++context_collector_worker_id;
        if (context_collector_worker_id == NUMBER_OF_WORKERS) context_collector_worker_id = 0;

#if defined(THROUGHPUT_EXPERIMENTS)
        for (size_t element_count = 0; element_count < BATCH_SIZE; ++element_count) {
            Data* unsafe data = &context_buffer[context_collector_current_start + element_count];
            sink += data->output_vector[0];
        }
#endif

#if defined(BATCH_MODEL_ACCURACY_EXPERIMENTS)
        //--- Code that can be used to check if results are delivered in time ---
        for (size_t element_count = 0; element_count < BATCH_SIZE; ++element_count) {
            Data* unsafe data = &context_buffer[context_collector_current_start + element_count];
            sink += data->output_vector[0];
            asm volatile("" ::: "memory");
            t :> time_received;
            timingresults[timing_results_index] = time_received - data->timestamp;
            asm volatile("" ::: "memory");
            ++timing_results_index;
        }

        if(timing_results_index == MEASUREMENTS) {
            for (int i = 0; i < MEASUREMENTS; ++i) printf("%d: %d\n", i, timingresults[i] * 10);
            timing_results_index = 0;
            exit(1);
        }
#endif
    }
}

unsafe void producer_func(chanend sender[]) {
    size_t context_scheduler_worker_id           = 0;
    size_t context_scheduler_batched_elements    = 0;
    size_t context_producer_ring_buffer_position = _CALCULATE_RING_BUFFER_START_POSITION(
                                                        _CALCULATE_BUFFER_SIZE(
                                                            RETENTION_TIME,
                                                            250,
                                                            5),
                                                        5);

    timer t;
#if defined(THROUGHPUT_EXPERIMENTS)
    int previous_timestamp = -1;
    int current_timestamp  = -1;
#endif

    timer time;
    unsigned int timeout = 0;
    time :> timeout;
    select {
        case time when timerafter(timeout) :> void:
            timeout += 500 / 10;
            break;
    }

    while (1) {
#if defined(BATCH_MODEL_ACCURACY_EXPERIMENTS)
        select {
            case time when timerafter(timeout) :> void:
                timeout += 250 / 10;
                break;
        }
#endif

#if defined(BATCH_MODEL_ACCURACY_EXPERIMENTS)
        //--- Code that can be used to check if results are delivered in time ---
        t :> (&context_buffer[context_producer_ring_buffer_position])->timestamp;
#endif
        ++context_producer_ring_buffer_position;
        if (++context_scheduler_batched_elements == BATCH_SIZE) {
            size_t pointer_to_batch = context_producer_ring_buffer_position - BATCH_SIZE;
            sender[context_scheduler_worker_id] <: pointer_to_batch;
            ++context_scheduler_worker_id;
            if (context_scheduler_worker_id == NUMBER_OF_WORKERS) context_scheduler_worker_id = 0;
            context_scheduler_batched_elements = 0;
            if (context_producer_ring_buffer_position == context_buffer_size - 1) context_producer_ring_buffer_position = 0;
        }
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
    }
}

unsafe void worker_thread(chanend receiver, chanend sender, size_t worker_id) {
    size_t pointer_to_batch;

    while (1) {
        receiver :> pointer_to_batch;
        for (size_t i = pointer_to_batch; i < pointer_to_batch + BATCH_SIZE; ++i) {
            Data * unsafe data = &context_buffer[i];

            for (int row = 0; row < 15; ++row) {
                int temp_result = 0;
                for (int index = ia[row]; index <= ia[row + 1] - 1; ++index) {
                    temp_result += a[index] * data->input_vector[ja[index]];
                }
                data->output_vector[row] = temp_result;
            }
        }
        sender <: pointer_to_batch;
    }
}

void start_farm() {
    printf("-----------------------------------\n");
    printf("--- Start Peso Task Farm \t---\n");
    printf("--- Number of worker threads: %d\n--- Batch size %d\n--- Buffer size: %d\n",
            NUMBER_OF_WORKERS, BATCH_SIZE, context_buffer_size);
    printf("-----------------------------------\n");
    chan p_to_w[6];
    chan w_to_c[6];
    unsafe {
        par {
            producer_func(p_to_w);
            consumer_func(w_to_c);
            par(size_t i = 0; i < 6; ++i) {
                worker_thread(p_to_w[i], w_to_c[i], i);
            }
        }
    }
}

int hand_implemented_sparse_matrix_vector_multiplication_benchmark() {
    start_farm();
    return 0;
}

