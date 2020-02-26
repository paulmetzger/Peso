/*
 * farm.h
 *
 *  Created on: 2 May 2018
 *      Author: Paul Metzger
 */

#ifndef FARM_H_
#define FARM_H_

#include <stddef.h>
#include <stdio.h>

#include <platform.h>

#define DEBUG_CODE

#define COM_TIME 100

/* Macros */
#ifdef DEBUG_CODE
#define DEBUG(...) \
    printf(__VA_ARGS__);
#else
#define DEBUG(...)
#endif

#define _DIVISION_CEIL(DIVIDEND, DIVISOR) \
    ((DIVIDEND) / (DIVISOR)) + (((DIVIDEND) % (DIVISOR)) != 0 ? 1 : 0)

#define _MAX(ARG1, ARG2) \
    (ARG1) > (ARG2) ? (ARG1) : (ARG2)

#define _CALCULATE_BATCH_SIZE(INTERARRIVAL_TIME, COM_TIME, RELATIVE_DEADLINE, WCET) \
    (RELATIVE_DEADLINE - 2 * (COM_TIME + COM_TIME) + INTERARRIVAL_TIME) / (INTERARRIVAL_TIME + WCET)

#define _CALCULATE_NUMBER_OF_WORKERS(INTERARRIVAL_TIME, COM_TIME, WCET, BATCH_SIZE) \
    _DIVISION_CEIL(2 * COM_TIME + WCET * BATCH_SIZE, INTERARRIVAL_TIME * BATCH_SIZE)

#define _CALCULATE_BUFFER_SIZE(RETENTION_TIME, INTERARRIVAL_TIME, BATCH_SIZE) \
    (_MAX(1, _DIVISION_CEIL(RETENTION_TIME, INTERARRIVAL_TIME)) * BATCH_SIZE)

#define configure_farm_with_worker_setup_code(FARM_NAME, \
        WORKER_FUNCTION, \
        PRODUCER_FUNCTION, \
        CONSUMER_FUNCTION, \
        INTERARRIVAL_TIME, \
        WCET,\
        RELATIVE_DEADLINE, \
        RETENTION_TIME, \
        DATA_T, \
        WORKER_SETUP_CODE\
        ) \
        \
        struct context { \
            size_t producer_counter;\
            size_t buffer_size;\
            DATA_T buffer[_CALCULATE_BUFFER_SIZE(RETENTION_TIME, INTERARRIVAL_TIME, _CALCULATE_BATCH_SIZE(INTERARRIVAL_TIME, COM_TIME, RELATIVE_DEADLINE, WCET))]; \
        }; \
    \
    unsafe void send_data(chanend sender, Context * unsafe context) { \
        Range range = {context->producer_counter}; \
        sender <: range; \
        context->producer_counter += 1; \
        if (context->producer_counter == context->buffer_size) context->producer_counter = 0; \
    }\
    \
    unsafe Data * unsafe prepare_data(Context * unsafe context) { \
        return &context->buffer[context->producer_counter]; \
    } \
    \
    unsafe Data * unsafe receive_result(chanend receiver, Context * unsafe context) {\
        int i;\
        receiver :> i;\
        return &context->buffer[i];\
    }\
    \
    unsafe void worker_thread(chanend receiver, chanend sender, Context * unsafe context, size_t worker_id) { \
        DEBUG("WORKER    This is worker %d\n", worker_id); \
        \
        Range range; \
        \
        while(1) { \
            _Pragma("xta label \"loop_worker\"") \
            _Pragma("xta endpoint \"chan_worker_in_start\"")\
            receiver :> range; \
            _Pragma("xta endpoint \"chan_worker_in_stop\"")\
            DEBUG("WORKER    Received start index %d\n", range.start); \
            for(size_t i = range.start; i < range.start + _CALCULATE_BATCH_SIZE(INTERARRIVAL_TIME, COM_TIME, RELATIVE_DEADLINE, WCET); ++i) { \
                _Pragma("xta label \"loop_batch\"") \
                \
                _Pragma("xta endpoint \"worker_read_data_start\"") \
                Data *data = &context->buffer[i]; \
                _Pragma("xta endpoint \"worker_read_data_stop\"") \
                \
                _Pragma("xta endpoint \"worker_function_start\"") \
                WORKER_FUNCTION(worker_id, data); \
                _Pragma("xta endpoint \"worker_function_stop\"") \
                \
            } \
            _Pragma("xta endpoint \"chan_worker_out_start\"")\
            sender <: range; \
            _Pragma("xta endpoint \"chan_worker_out_stop\"")\
        } \
    } \
    \
    void start_ ## FARM_NAME() { \
        const size_t batch_size = _CALCULATE_BATCH_SIZE(INTERARRIVAL_TIME, COM_TIME, RELATIVE_DEADLINE, WCET);\
        const size_t number_of_workers = _CALCULATE_NUMBER_OF_WORKERS(INTERARRIVAL_TIME, COM_TIME, WCET, batch_size);\
        printf("-----------------------------------\n");\
        printf("--- Start Peso Task Farm \t---\n");\
        printf("--- Number of worker threads: %d\n--- Batch size %d\n--- Buffer size: %d\n",\
                number_of_workers, \
                batch_size, \
                _CALCULATE_BUFFER_SIZE(RETENTION_TIME, INTERARRIVAL_TIME, \
                        _CALCULATE_BATCH_SIZE(INTERARRIVAL_TIME, COM_TIME, RELATIVE_DEADLINE, WCET)));\
        printf("-----------------------------------\n");\
        \
        chan s_to_w[_CALCULATE_NUMBER_OF_WORKERS(INTERARRIVAL_TIME, COM_TIME, WCET, _CALCULATE_BATCH_SIZE(INTERARRIVAL_TIME, COM_TIME, RELATIVE_DEADLINE, WCET))];\
        chan w_to_c[_CALCULATE_NUMBER_OF_WORKERS(INTERARRIVAL_TIME, COM_TIME, WCET, _CALCULATE_BATCH_SIZE(INTERARRIVAL_TIME, COM_TIME, RELATIVE_DEADLINE, WCET))];\
        chan p_to_s;\
        chan c_to_c;\
        \
        unsafe{ \
            Context context; \
            context.producer_counter = 0; \
            context.buffer_size = _CALCULATE_BUFFER_SIZE(RETENTION_TIME, INTERARRIVAL_TIME, _CALCULATE_BATCH_SIZE(INTERARRIVAL_TIME, COM_TIME, RELATIVE_DEADLINE, WCET));\
            Context * unsafe context_ptr = &context; \
            \
            par {\
                PRODUCER_FUNCTION(p_to_s, context_ptr);\
                scheduler(p_to_s, s_to_w, number_of_workers, batch_size, context.buffer_size);\
                collector(w_to_c, c_to_c, number_of_workers, batch_size);\
                CONSUMER_FUNCTION(c_to_c, context_ptr);\
                \
                par(size_t i = 0; i < _CALCULATE_NUMBER_OF_WORKERS(\
                        INTERARRIVAL_TIME, COM_TIME, WCET, \
                    _CALCULATE_BATCH_SIZE(INTERARRIVAL_TIME, COM_TIME, RELATIVE_DEADLINE, WCET)\
                    ); ++i) { \
                        worker_thread(s_to_w[i], w_to_c[i], context_ptr, i);\
                    }\
            }\
        }\
    }

#define configure_farm(FARM_NAME, \
        WORKER_FUNCTION, \
        PRODUCER_FUNCTION, \
        CONSUMER_FUNCTION, \
        INTERARRIVAL_TIME, \
        WCET,\
        RELATIVE_DEADLINE, \
        RETENTION_TIME, \
        DATA_T \
        ) \
        \
        configure_farm_with_worker_setup_code(FARM_NAME, \
        WORKER_FUNCTION, \
        PRODUCER_FUNCTION, \
        CONSUMER_FUNCTION, \
        INTERARRIVAL_TIME, \
        WCET,\
        RELATIVE_DEADLINE, \
        RETENTION_TIME, \
        DATA_T, \
        ;)

#define worker_function(function_name, worker_code) \
    unsafe void function_name(size_t worker_id, Data *data) { \
        worker_code \
    }

#define worker_function_with_setup_code(function_name, worker_code, SETUP_CODE) \
    unsafe void function_name(size_t worker_id, Data *data) { \
        worker_code \
    }

#define consumer(function_name, consumer_code) \
    unsafe void function_name(chanend receiver, Context * unsafe context) { \
        while(1) { \
            consumer_code \
        } \
    }

#define producer(function_name, producer_code) \
    unsafe void function_name(chanend sender, Context * unsafe context) { \
        producer_code \
    }

#define receive_data() \
    receive_result(receiver, context)

#define access_data() \
    data

#define prep_data() \
    prepare_data(context)

#define submit_data() \
    send_data(sender, context)

/* Structs */
struct data;
typedef struct data Data;

typedef struct context Context;

struct range {
    size_t start;
};
typedef struct range Range;

/* Functions */
unsafe Data * unsafe receive_result(chanend receiver, Context * unsafe context);
unsafe Data * unsafe prepare_data(Context * unsafe context);
unsafe void send_data(chanend sender, Context * unsafe context);

void scheduler(chanend receiver, chanend sender[], const size_t number_of_workers,
        const size_t batch_size, const size_t buffer_size) {
    DEBUG("SCHEDULER This is the scheduler\n");
    size_t worker_id = 0;
    Range range_in;
    Range range_out;
    range_out.start = 0;
    size_t buffered_elements = 0;

    while(1) {
        DEBUG("SCHEDULER Buffered elements: %d\n", buffered_elements);
# pragma xta endpoint "chan_scheduler_in"
        receiver :> range_in;

        if(++buffered_elements == batch_size) {
            //Assign work to a worker thread
# pragma xta endpoint "chan_scheduler_out"
            sender[worker_id] <: range_out;

            DEBUG("SCHEDULER Sent data: start %d, worker: %d\n", range_out.start, worker_id);

            range_out.start += batch_size;
            if (range_out.start >= buffer_size) range_out.start -= buffer_size;

            //Compute the index of the next worker thread
            ++worker_id;
            if (worker_id == number_of_workers) worker_id = 0;
            buffered_elements = 0;
        }
    }
}

void collector(chanend receiver[number_of_workers], chanend sender, const size_t number_of_workers, size_t batch_size) {
    DEBUG("COLLECTOR This is the collector\n");
    int worker_cnt = 0;
    Range range;

    while(1) {
# pragma xta endpoint "chan_collector_in"
        receiver[worker_cnt] :> range;
        DEBUG("COLLECTOR Received data: start: %d, worker %d\n", range.start, worker_cnt);

        for (size_t i = range.start; i < range.start + batch_size; ++i) {
# pragma xta endpoint "chan_collector_out"
            sender <: i;
        }

        worker_cnt += 1;
        if (worker_cnt == number_of_workers) worker_cnt = 0;
    }
}
#endif /* FARM_H_ */
