/*
 * reduction.h
 *
 *  Created on: 18 May 2018
 *      Author: Paul Metzger
 */


#ifndef REDUCTION_H_
#define REDUCTION_H_

#include <stdlib.h>

#include <peso/farm.h>
#include <peso/utils.h>

#define PERIOD            %PERIOD%
#define INPUT_VECTOR_SIZE %INPUT_VECTOR_SIZE%
#define RELATIVE_DEADLINE %RELATIVE_DEADLINE%
#define WORKER_WCET       %WORKER_WCET%
#define RETENTION_TIME    100 * 1000

#define BATCH_SIZE        %BATCH_SIZE%
#define NUMBER_OF_WORKERS %WORKERS%
#define MEASUREMENTS      20

size_t measurement_count = 0;
size_t dummy_data = 0;

struct data {
    int input_vector[INPUT_VECTOR_SIZE];
    int result;
};
prepare_farm(Data, RETENTION_TIME, PERIOD)

producer(
    producer_func, //Producer name

    peso_period(%PERIOD%);
    //Prepare input data. These could be values read from sensors.
    for (size_t i = 0; i < INPUT_VECTOR_SIZE; ++i) prep_data()->input_vector[i] = dummy_data;
    ++dummy_data;
)

worker_function(
    worker_func, //Worker function name

    size_t result = 0;
    //Compute the average of the "sensor data"
    //1. step: Compute the sum of the "sensor data"
    for (size_t i = 0; i < INPUT_VECTOR_SIZE; ++i) {
        //printf("Worker   | index: %d, input: %d\n", i, access_data()->input_vector[i]);
        result += access_data()->input_vector[i];
    }
    //2. step: Devide by the number of sensor readings
    result = result / INPUT_VECTOR_SIZE;

    //Store the result so that the consumer can access it
    access_data()->result = result;
)

consumer(
    consumer_func, //Consumer name

    printf("Consumer | %d\n", access_data()->result);
    if(measurement_count == MEASUREMENTS) exit(0);
    ++measurement_count;
)

configure_farm(
        farm, //Farm name
        worker_func,
        producer_func,
        consumer_func,
        PERIOD, //Interarrival time
        WORKER_WCET, //WCET of a single job
        RELATIVE_DEADLINE,
        RETENTION_TIME, //Retention time
        Data //Layout of the data that producer sennds to the farm
             //and that the consumer receives from the farm
)

int reduction_benchmark() {
    start_farm();
    return 0;
}

#endif /* REDUCTION_H_ */
