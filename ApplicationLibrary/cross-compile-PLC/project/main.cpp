//-----------------------------------------------------------------------------
// Copyright 2018 Thiago Alves
// This file is part of the OpenPLC Software Stack.
//
// OpenPLC is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// OpenPLC is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with OpenPLC.  If not, see <http://www.gnu.org/licenses/>.
//------
//
// This is the main file for the OpenPLC. It contains the initialization
// procedures for the hardware, network and the main loop
// Thiago Alves, Jun 2018
//-----------------------------------------------------------------------------

#include <stdio.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <signal.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/mman.h>

#include "iec_types.h"
#include "ladder.h"


IEC_BOOL __DEBUG;

unsigned long __tick = 0;
pthread_mutex_t bufferLock; //mutex for the internal buffers
pthread_mutex_t logLock; //mutex for the internal log
uint8_t run_openplc = 1; //Variable to control OpenPLC Runtime execution
unsigned char log_buffer[1000000]; //A very large buffer to store all logs
int log_index = 0;
int log_counter = 0;

// Helper function - Makes the running thread sleep for the ammount of time
// in milliseconds
void sleep_until(struct timespec *ts, long long delay)
{
    ts->tv_sec  += delay / (1000*1000*1000);
    ts->tv_nsec += delay % (1000*1000*1000);
    if(ts->tv_nsec >= 1000*1000*1000)
    {
        ts->tv_nsec -= 1000*1000*1000;
        ts->tv_sec++;
    }
    clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, ts,  NULL);
}


// Disable all outputs
void disableOutputs()
{
    //Disable digital outputs
    for (int i = 0; i < BUFFER_SIZE; i++)
        for (int j = 0; j < 8; j++)
            if (bool_output[i][j] != NULL) *bool_output[i][j] = 0;
    //Disable byte outputs
    for (int i = 0; i < BUFFER_SIZE; i++)
        if (byte_output[i] != NULL) *byte_output[i] = 0;
    
    //Disable analog outputs
    for (int i = 0; i < BUFFER_SIZE; i++)
        if (int_output[i] != NULL) *int_output[i] = 0;
}


// Helper function - Logs messages and print them on the console
void log(unsigned char *logmsg)
{
    pthread_mutex_lock(&logLock); //lock mutex
    printf("%s", logmsg);
    for (int i = 0; logmsg[i] != '\0'; i++)
    {
        log_buffer[log_index] = logmsg[i];
        log_index++;
        log_buffer[log_index] = '\0';
    }
    
    log_counter++;
    if (log_counter >= 1000)
    {
        /*Store current log on a file*/
        log_counter = 0;
        log_index = 0;
    }
    pthread_mutex_unlock(&logLock); //unlock mutex
}



int main(int argc,char **argv)
{
    unsigned char log_msg[1000];
    sprintf((char *)log_msg, "OpenPLC Runtime starting...\n");
    log(log_msg);

    // PLC INITIALIZATION
    tzset();
    config_init__();
    glueVars();

    // MUTEX INITIALIZATION
    if (pthread_mutex_init(&bufferLock, NULL) != 0)
    {
        printf("Mutex init failed\n");
        exit(1);
    }

    // HARDWARE INITIALIZATION

    initializeHardware();
    updateBuffersIn();
    updateBuffersOut();


#ifdef __linux__
    // REAL-TIME INITIALIZATION

    // Set our thread to real time priority
    struct sched_param sp;
    sp.sched_priority = 30;
    printf("Setting main thread priority to RT\n");
    if(pthread_setschedparam(pthread_self(), SCHED_FIFO, &sp))
    {
        printf("WARNING: Failed to set main thread to real-time priority\n");
    }

    // Lock memory to ensure no swapping is done.
    printf("Locking main thread memory\n");
    if(mlockall(MCL_FUTURE|MCL_CURRENT))
    {
        printf("WARNING: Failed to lock memory\n");
    }
#endif
    struct timespec timer_start;

	// MAIN LOOP
	while(run_openplc)
	{
		glueVars();
        
		updateBuffersIn();
		pthread_mutex_lock(&bufferLock); 

		config_run__(__tick++); 
		pthread_mutex_unlock(&bufferLock); 

		updateBuffersOut();
		updateTime();

		sleep_until(&timer_start, common_ticktime__);
	}

	// SHUTTING DOWN OPENPLC RUNTIME
    disableOutputs();
	finalizeHardware();
    printf("Shutting down OpenPLC Runtime...\n");
    exit(0);
}
