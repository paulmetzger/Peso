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

#define NO_DEBUG_CODE
#define AVAILABLE_CORES 8

/* Macros */
#ifdef DEBUG_CODE
#define DEBUG(...) \
    printf(__VA_ARGS__);
#else
#define DEBUG(...)
#endif

/* Helper functions */
#define _DIVISION_CEIL(DIVIDEND, DIVISOR) \
    (((DIVIDEND) / (DIVISOR)) + (((DIVIDEND) % (DIVISOR)) != 0 ? 1 : 0))

#define _MAX(ARG1, ARG2) \
    ((ARG1) > (ARG2) ? (ARG1) : (ARG2))

#define _CALCULATE_RING_BUFFER_START_POSITION(BUFFER_SIZE, BATCH_SIZE)\
    ((_DIVISION_CEIL(_DIVISION_CEIL(BUFFER_SIZE, BATCH_SIZE), 2) * BATCH_SIZE) - 1)

#define _CALCULATE_BUFFER_SIZE(RETENTION_TIME, INTERARRIVAL_TIME, BATCH_SIZE) \
    (((_MAX(1, _DIVISION_CEIL(RETENTION_TIME, INTERARRIVAL_TIME)) * BATCH_SIZE) + BATCH_SIZE))

#define prepare_farm(DATA_T, RETENTION_TIME, INTERARRIVAL_TIME) \
    unsafe { \
        DATA_T context_buffer_safe[_CALCULATE_BUFFER_SIZE(RETENTION_TIME, INTERARRIVAL_TIME, BATCH_SIZE)]; \
        DATA_T * unsafe context_buffer = (DATA_T * unsafe) &context_buffer_safe[0]; \
    }\
    const size_t context_buffer_size = _CALCULATE_BUFFER_SIZE(RETENTION_TIME, INTERARRIVAL_TIME, BATCH_SIZE); \
    const size_t context_global_ring_buffer_position = _CALCULATE_RING_BUFFER_START_POSITION( \
                _CALCULATE_BUFFER_SIZE(RETENTION_TIME, INTERARRIVAL_TIME, BATCH_SIZE), BATCH_SIZE);

#define configure_farm(FARM_NAME, \
        WORKER_FUNCTION, \
        PRODUCER_FUNCTION, \
        CONSUMER_FUNCTION \
        ) \
    void start_ ## FARM_NAME() { \
        printf("-----------------------------------\n"); \
        printf("--- Start Peso Task Farm \t---\n"); \
        printf("--- Number of worker threads: %d\n--- Batch size %d\n--- Buffer size: %d\n", \
                1, \
                BATCH_SIZE, \
                context_buffer_size); \
        printf("-----------------------------------\n");\
        \
        chan p_to_w; \
        chan w_to_c;\
        unsafe{ \
            par {\
                PRODUCER_FUNCTION(p_to_w); \
                CONSUMER_FUNCTION(w_to_c); \
                \
                WORKER_FUNCTION(p_to_w, w_to_c); \
            } \
        } \
    }

#define worker_function(function_name, data_t, worker_code) \
    unsafe void function_name(chanend receiver, chanend sender) { \
        size_t pointer_to_batch; \
        \
        while(1) { \
            receiver :> pointer_to_batch; \
            DEBUG("WORKER    Received start index %d\n", pointer_to_batch); \
            _Pragma("loop unroll") \
            for(size_t batch_i = 0; batch_i < BATCH_SIZE; ++batch_i) { \
                data_t * unsafe data = &context_buffer[pointer_to_batch + batch_i]; \
                worker_code \
            } \
            sender <: pointer_to_batch; \
        } \
    }

#define consumer(function_name, data_t, consumer_code) \
    unsafe void function_name(chanend receiver) { \
        size_t context_collector_current_start = 0; \
        size_t context_collector_element_count = 0; \
        timer t; \
        \
        while(1) { \
            receive_data(data_t); \
            consumer_code \
        } \
    }

#define producer(function_name, producer_code) \
    unsafe void function_name(chanend sender) { \
        size_t context_scheduler_batched_elements = 0; \
        size_t context_producer_ring_buffer_position = context_global_ring_buffer_position;\
        \
        timer t; \
        peso_timer_init();\
        peso_sleep(1000);\
        while (1) {\
            producer_code \
        }\
    }

#define receive_data(data_t) \
    if (context_collector_element_count == 0) { \
        receiver :> context_collector_current_start; \
        DEBUG("COLLECTOR Received data: start: %d\n", context_collector_current_start); \
    } \
    size_t current_element = context_collector_current_start + context_collector_element_count; \
    ++context_collector_element_count; \
    if (context_collector_element_count == BATCH_SIZE) context_collector_element_count = 0; \
    data_t* unsafe data = &context_buffer[current_element];

#define access_data() data

#define prep_data() (&context_buffer[context_producer_ring_buffer_position])

#define submit_data() \
    ++context_producer_ring_buffer_position;\
    if(++context_scheduler_batched_elements == BATCH_SIZE) { \
        size_t pointer_to_batch = context_producer_ring_buffer_position - BATCH_SIZE; \
        sender <: pointer_to_batch; \
        DEBUG("SCHEDULER Sent data: start %d, buffered elements: %d\n", \
                pointer, context_scheduler_batched_elements); \
        \
        context_scheduler_batched_elements = 0; \
        if (context_producer_ring_buffer_position == (context_buffer_size - (BATCH_SIZE + 1))) \
            context_producer_ring_buffer_position = 0; \
    } else {\
        DEBUG("SCHEDULER Accumulated inputs %d\n", context_scheduler_batched_elements); \
    }

/* The user of this library has to flesh out the functions and structs below. */
/* Structs */
struct data;
typedef struct data Data;

#endif /* FARM_H_ */
