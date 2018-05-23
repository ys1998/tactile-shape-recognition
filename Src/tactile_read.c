/*
 * State machine for handling data reading events of tactile sensors.
 *
 *  Created on: May 17, 2018
 *      Author: Yash
 */

/*
 * Includes for header files.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "stm32f1xx_hal.h"
#include "tactile_read.h"
#include "usbd_cdc_if.h"
#include "usbd_cdc.h"

/* Global Variables */
extern ADC_HandleTypeDef hadc1;
extern TR_HandleTypeDef htr;
extern MAX_NUM_VALUES;

void TR_Init(TR_HandleTypeDef *tr){
	tr->state = TR_SETUP;
	tr->cache_read = true;
	tr->stable_values = calloc(MAX_NUM_VALUES, sizeof(uint16_t));
	tr->curr_values = calloc(MAX_NUM_VALUES, sizeof(uint16_t));
	tr->n_read = 0;
}

int TR_NextState(TR_HandleTypeDef *tr){
	switch(tr->state) {
	case TR_SETUP: ;
		tr->state = TR_BUSY;
		break;
	case TR_IDLE:
		// State machine waits in this state if the 'stable_values' haven't been
		// converted into spikes and the 'curr_values' buffer is full.
		if(tr->cache_read == true){
			// copy 'curr_values' to 'stable_values'
			memcpy(tr->stable_values, tr->curr_values, 2 * MAX_NUM_VALUES);
			tr->cache_read = false;
			tr->state = TR_COMPLETED;
		}
		break;
	case TR_BUSY: ;
		if(tr->n_read == MAX_NUM_VALUES){
			/* When values from all sensors have been read */
			if(tr->cache_read == true){
				// stable values can be safely updated
				memcpy(tr->stable_values, tr->curr_values, 2 * MAX_NUM_VALUES);
				tr->cache_read = false;
				tr->state = TR_COMPLETED;
			}else{
				// last read values haven't been used; remain idle until they are
				tr->state = TR_IDLE;
			}
		}else{
			/* Reading process is still ongoing */
			ADC_ChannelConfTypeDef sConfig;

			/* Configure 4 channels for polling */
			sConfig.SamplingTime = ADC_SAMPLETIME_7CYCLES_5;
			sConfig.Rank = 1;
			sConfig.Channel = ADC_CHANNEL_0;
			if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK){
				_Error_Handler(__FILE__, __LINE__);
			}
			if(HAL_ADC_PollForConversion(&hadc1, 1000) == HAL_OK){
				tr->curr_values[0] = HAL_ADC_GetValue(&hadc1);
			}
			// Update the number of values read
			tr->n_read += 1;
			// Transit to the SETUP state when column needs to be changed
			if(tr->n_read % 16 == 0 && tr->n_read < MAX_NUM_VALUES){
				tr->state = TR_SETUP;
			}
		}
		break;
	case TR_COMPLETED:
		// All 64 values have been successfully read
		tr->state = TR_SETUP;
		tr->n_read = 0;
		break;
	default:
		// this state should never be reached
		return -1;
	}
	return 0;
}

void TR_Deinit(TR_HandleTypeDef *htr){
	// free the memory allocated to buffers
	free(htr->curr_values);
	free(htr->stable_values);
}
