#ifndef REDUCTION_H_
#define REDUCTION_H_

#include <stdlib.h>

#define INPUT_VECTOR_SIZE 40

#define access_data() data

struct Data {
    int input_vector[INPUT_VECTOR_SIZE];
    int result;
    int timestamp;
};

struct Data dummy_data[10];

unsafe int reduction_worker_code(size_t worker_id, struct Data * unsafe data) {
    unsigned int result = 0;
    for (size_t i = 0; i < INPUT_VECTOR_SIZE; ++i) {
        result += access_data()->input_vector[i];
    }
    access_data()->result = result;
    return access_data()->result;
}

int reduction_benchmark() {
    unsafe {
        for (size_t i = 0; i < 1; ++i) {
            struct Data * unsafe data = &dummy_data[i];
            reduction_worker_code(1, data);
        }
    }
    return 0;
}



#endif /* REDUCTION_H_ */
