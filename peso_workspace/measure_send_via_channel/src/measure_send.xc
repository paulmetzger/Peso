/*
 * measure_channel_operations.xc
 *
 *  Created on: 8 Jun 2018
 *      Author: picard
 */

#include <stdio.h>
#include <platform.h>
#include <stdlib.h>

void sender(chanend chan_out, chanend sync) {
    timer tmr;
    unsigned int time_before_receive;
    unsigned int time_after_receive;

    srand(123);
    size_t data = rand() % 100;
    size_t dummy = rand() % 100;

    printf("Waiting for sync...\n");
    sync :> dummy;

    tmr :> time_before_receive;
    chan_out <: data;
    tmr :> time_after_receive;

    printf("Time for send operation: %d\n",
                time_after_receive - time_before_receive);
    printf("Received data and dummy: %d, %d\n", data, dummy);
}

void receiver(chanend chan_in, chanend sync) {
    size_t dummy = 100;
    size_t data = 100;

    sync <: dummy;

/*    timer time;
    int timeout = 0;
    time :> timeout;
    select {
        case time when timerafter(timeout + 1 * 1000) :> void:
            break;
    }*/

    chan_in :> data;
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
