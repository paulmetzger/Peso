/*
 * utils.h
 *
 *  Created on: 11 May 2018
 *      Author: picard
 */


#ifndef UTILS_H_
#define UTILS_H_
#define peso_timer_init() \
    timer time; \
    unsigned int timeout = 0; \
    time :> timeout; \

#define peso_sleep(time_in_ns) \
    timeout += time_in_ns / 10; \
    select { \
        case time when timerafter(timeout) :> void: \
            break; \
    }

#define peso_period(time_in_ns) \
    select { \
        case time when timerafter(timeout) :> void: \
            timeout += time_in_ns / 10; \
            break; \
    }

#endif /* UTILS_H_ */
