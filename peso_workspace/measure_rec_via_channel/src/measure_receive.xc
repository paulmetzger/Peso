/*
 * measure_channel_operations.xc
 *
 *  Created on: 8 Jun 2018
 *      Author: Paul Metzger
 */

#include <stdio.h>
#include <platform.h>
#include <stdlib.h>

void sender(chanend chan_out, chanend sync) {
    srand(123);
    size_t data = rand() % 100;
    size_t dummy = rand() % 100;

    while(1) {
        sync <: dummy;
        chan_out <: data;
    }
}

void receiver(chanend chan_in, chanend sync) {
    timer tmr;
    unsigned int time_before_receive;
    unsigned int time_after_receive;
    size_t dummy = 100;
    size_t data = 100;

    printf("Waiting for sync...\n");
    sync :> dummy;

    tmr :> time_before_receive;
    chan_in :> data;
    tmr :> time_after_receive;

    printf("Time for receive operation: %d\n",
            time_after_receive - time_before_receive);
    printf("Received data and dummy: %d, %d\n", data, dummy);
}

int main() {
    chan channel;
    chan sync;

    par {
        sender(channel, sync);
        receiver(channel, sync);
    }

    return 0;
}
