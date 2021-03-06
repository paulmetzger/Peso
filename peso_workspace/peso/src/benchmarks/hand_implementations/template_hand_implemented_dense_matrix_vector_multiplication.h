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

#define %EXPIREMENT_TYPE%

#define MEASUREMENTS      (10 * %WORKERS% * %BATCH_SIZE%)
#define RETENTION_TIME    (110*1000)
#define BATCH_SIZE        %BATCH_SIZE%
#define NUMBER_OF_WORKERS %WORKERS%

int timing_results_index = 0;
int timingresults[MEASUREMENTS];
int time_received        = -1;
int sink                 = -1;

int matrix[10 * 10] =  {1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                        5, 8, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 3, 0, 0, 0, 0, 0, 0, 0,
                        0, 6, 0, 0, 0, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 1, 0, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 1, 0, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 1, 0, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 1};

struct data {
    int input_vector[%INPUT_SIZE%];
    int output_vector[%INPUT_SIZE%];
    int timestamp;
};
typedef struct data Data;

unsafe {
    Data context_buffer_safe[_CALCULATE_BUFFER_SIZE(
                                 RETENTION_TIME,
                                 %INTERARRIVAL_TIME_NS%,
                                 %BATCH_SIZE%)];
    Data * unsafe context_buffer = (Data * unsafe) &context_buffer_safe[0];
}

const size_t context_buffer_size = _CALCULATE_BUFFER_SIZE(RETENTION_TIME,
                                                          %INTERARRIVAL_TIME_NS%,
                                                          %BATCH_SIZE%);

unsafe void consumer_func(chanend receiver[]) {
    size_t context_collector_current_start    = 0;
    size_t context_collector_element_count    = 0;
    size_t context_collector_worker_id        = 0;
    timer t;

    while (1) {
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
        Data* unsafe data = &context_buffer[context_collector_current_start];
        sink += data->output_vector[0];
        asm volatile("" ::: "memory");
        t :> time_received;
        timingresults[timing_results_index] = time_received - data->timestamp;
        asm volatile("" ::: "memory");
        ++timing_results_index;

        //--- Code that can be used to check if results are delivered in time ---
        for (size_t element_count = 1; element_count < BATCH_SIZE; ++element_count) {
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
    size_t context_producer_ring_buffer_position = _CALCULATE_RING_BUFFER_START_POSITION( \
            _CALCULATE_BUFFER_SIZE(RETENTION_TIME, %INTERARRIVAL_TIME_NS%, BATCH_SIZE), BATCH_SIZE);

    timer t;
#if defined(THROUGHPUT_EXPERIMENTS)
    int previous_timestamp = -1;
    int current_timestamp = -1;
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
                timeout += %INTERARRIVAL_TIME_NS% / 10;
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

unsafe void worker_func(chanend receiver, chanend sender, size_t worker_id) {
    size_t pointer_to_batch;

    while (1) {
        receiver :> pointer_to_batch;
        for (size_t i = 0; i < BATCH_SIZE; ++i) {
            Data * unsafe data = &context_buffer[i + pointer_to_batch];

            for (int y = 0; y < %INPUT_SIZE%; ++y) {
                int new_value = 0;
                for (int x = 0; x < %INPUT_SIZE%; ++x) {
                    new_value += matrix[y * %INPUT_SIZE% + x] * data->input_vector[x];
                }
                data->output_vector[y] = new_value;
            }
        }
        sender <: pointer_to_batch;
    }
}

void start_farm() {
    printf("-----------------------------------\n");
    printf("--- Start Peso Task Farm \t---\n");
    printf(
            "--- Number of worker threads: %d\n--- Batch size %d\n--- Buffer size: %d\n",
            NUMBER_OF_WORKERS, BATCH_SIZE, context_buffer_size);
    printf("-----------------------------------\n");
    chan p_to_w[%WORKERS%];
    chan w_to_c[%WORKERS%];
    unsafe {
        par {
            producer_func(p_to_w);
            consumer_func(w_to_c);
            par(size_t i = 0; i < %WORKERS%; ++i) {
                worker_func(p_to_w[i], w_to_c[i], i);
            }
        }
    }
}

int hand_implemented_dense_matrix_vector_multiplication_benchmark() {
    start_farm();
    return 0;
}

