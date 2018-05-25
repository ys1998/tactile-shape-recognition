/*
 * spike_conv.c
 *
 *  Created on: May 17, 2018
 *      Author: Yash
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "stm32f1xx_hal.h"
#include "tactile_read.h"
#include "spike_conv.h"
#include "usbd_cdc_if.h"
#include "usbd_cdc.h"

/* Global Variables */
extern ADC_HandleTypeDef hadc1;
extern TR_HandleTypeDef htr;
extern SpikeConv_HandleTypeDef hsc;
extern MAX_NUM_VALUES;

void SpikeConv_Init(SpikeConv_HandleTypeDef *sc){
	sc->state = SC_IDLE;
	sc->spikeGenerated = false;
	sc->values = calloc(MAX_NUM_VALUES, sizeof(uint16_t));
}

int SpikeConv_NextState(SpikeConv_HandleTypeDef *sc){
	switch(sc->state) {
	case SC_IDLE:
		// State machine remains idle until the previous generated spike
		// is successfully transmitted, and the Tactile Reader has read
		// the next sensor data.
		if(!sc->spikeGenerated && !htr.cache_read){
			memcpy(sc->values, htr.stable_values, 2 * MAX_NUM_VALUES);
			// Change the flag of TactileReader's State Machine
			htr.cache_read = true;
			sc->state = SC_BUSY;
		}
		break;
	case SC_BUSY:
		/*
		 * Spike encoding algorithm.
		 * Currently, simply returns the same analog input.
		*/

		sc->spikeGenerated = true;
		sc->state = SC_IDLE;
		break;
	default:
		// this state should never be reached
		return -1;
	}
	return 0;
}

void SpikeConv_Deinit(SpikeConv_HandleTypeDef *sc){
	// free the memory allocated to buffers
	free(sc->values);
}
