/*
 * measure_channel_communication_time.xc
 *
 * Measure the communication latency between cores.
 * Max. measured latency 130ns. (24/05/2019)
 *
 *  Created on: 18 May 2018
 *      Author: Paul Metzger
 */

#include <stdio.h>
#include <platform.h>

#define MEASURMENTS 10000
#define PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION 2

static unsigned int measurments[MEASURMENTS];

/**
 * The producer and consumer function are used to measure the communication latency.
 */
void producer(chanend chan_out, chanend sync_with_ping[3]) {
    timer tmr;
    unsigned time = 0;
    unsigned sync_with_ping_sink;
    for (int i = 0; i < 3; ++i) sync_with_ping[i] :> sync_with_ping_sink;

    while(1) {
        tmr :> time;
        chan_out <: time;
    }
}

void consumer(chanend chan_in) {
    timer tmr;
    for (int i = 0; i < MEASURMENTS; ++i) {
        unsigned received_time = 0;
        unsigned local_time = 0;

        chan_in :> received_time;
        tmr :> local_time;

        measurments[i] = local_time - received_time;
    }
    unsigned highest_measurement = 0;
    for (int i = 0; i < MEASURMENTS; ++i) {
        if (measurments[i] > highest_measurement) highest_measurement = measurments[i];
    }
    printf("Highest latency: %dns\n", highest_measurement * 10);
}

/**
 * The ping and pong function are used to stress the core interconnect while we measure
 * the communication latency.
 * The ping and pong function just send constantly a dummy variable back and forth and
 * use up all otherwise unused communication channels.
 */
void ping(chanend chan_in[], chanend chan_out[], chanend sync_with_ping, unsigned in_channels, unsigned out_channels) {
    int dummy = 0;
    sync_with_ping <: dummy;

    while(1) {
        for(unsigned i = 0; i < out_channels; ++i) chan_out[i] <: dummy;
        for(unsigned i = 0; i < in_channels; ++i) chan_in[i] :> dummy;
    }
}

void pong(chanend chan_in[], chanend chan_out[], unsigned in_channels, unsigned out_channels) {
    int dummy = 0;
    while(1) {
        for(unsigned i = 0; i < in_channels; ++i) chan_in[i] :> dummy;
        ++dummy;
        for(unsigned i = 0; i < out_channels; ++i) chan_out[i] <: dummy;
        if (dummy == 10000000) printf("Dummy: %d\n", dummy);
    }
}

int main() {
    chan ping_to_pong_1[PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION];
    chan ping_to_pong_2[PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION];
    chan ping_to_pong_3[PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION];
    chan pong_to_ping_1[PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION];
    chan pong_to_ping_2[PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION];
    //We use one channel less than what the hardware offers as we get
    //an unexpected run time error otherwise.
    chan pong_to_ping_3[PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION - 1];
    chan p_to_c;
    //These channels are used to synchronize the producer and ping threads.
    //The producer should only start measurements once the ping pong threads
    //are running and stress the hardware.
    chan sync_with_ping[3];

    par {
        ping(pong_to_ping_1, ping_to_pong_1, sync_with_ping[0], PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION, PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION);
        pong(ping_to_pong_1, pong_to_ping_1, PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION, PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION);
        ping(pong_to_ping_2, ping_to_pong_2, sync_with_ping[1], PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION, PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION);
        pong(ping_to_pong_2, pong_to_ping_2, PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION, PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION);
        ping(pong_to_ping_3, ping_to_pong_3, sync_with_ping[2], PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION - 1, PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION);
        pong(ping_to_pong_3, pong_to_ping_3, PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION, PING_PONG_CHANNELS_PER_PAIR_PER_DIRECTION - 1);

        producer(p_to_c, sync_with_ping);
        consumer(p_to_c);
    }

    return 0;
}
