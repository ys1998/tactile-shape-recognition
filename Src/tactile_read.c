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
		// Set 'col' to be read
		uint8_t col = tr->n_read/16;
		// Set 'col' pin LOW and others HIGH, so that there is non-zero
		// potential difference between the reference voltage and 'col' pin
		// and current flows through it.
		for(int i = 0; i < 4; ++i){
			if(i == col){
				// Column to be read has to be grounded
				HAL_GPIO_WritePin(GPIOB, 1<<(3+i), GPIO_PIN_SET);
			}else{
				// All other columns are set to HIGH
				HAL_GPIO_WritePin(GPIOB, 1<<(3+i), GPIO_PIN_RESET);
			}
		}
		tr->state = TR_BUSY;
		break;
	case TR_IDLE:
		// State machine waits in this state if the 'stable_values' haven't been
		// converted into spikes and the 'curr_values' buffer is full.
		if(tr->cache_read == true){
			// copy 'curr_values' to 'stable_values'
			memset(tr->stable_values, 0, 2 * MAX_NUM_VALUES);
			memcpy(tr->stable_values, tr->curr_values, 2 * MAX_NUM_VALUES);
			memset(tr->curr_values, 0, 2 * MAX_NUM_VALUES);
			tr->cache_read = false;
			tr->state = TR_COMPLETED;
		}
		break;
	case TR_BUSY: ;
		if(tr->n_read == MAX_NUM_VALUES){
			/* When values from all sensors have been read */
			if(tr->cache_read == true){
				// stable values can be safely updated
				memset(tr->stable_values, 0, 2 * MAX_NUM_VALUES);
				memcpy(tr->stable_values, tr->curr_values, 2 * MAX_NUM_VALUES);
				memset(tr->curr_values, 0, 2 * MAX_NUM_VALUES);
				tr->cache_read = false;
				tr->state = TR_COMPLETED;
			}else{
				// last read values haven't been used; remain idle until they are
				tr->state = TR_IDLE;
			}
		}else{
			/* Reading process is still ongoing */
			// Find row to be read [0,1,2,3]
			uint8_t row = (tr->n_read % 16)/4;
			ADC_ChannelConfTypeDef sConfig;

			/* Configure 4 channels for polling */
			sConfig.SamplingTime = ADC_SAMPLETIME_41CYCLES_5;
			// Select two normal ADC channels
			for(int i = 0; i < 2; ++i){
				sConfig.Rank = i+1;
				sConfig.Channel = row + 4*i;
				// Configure ADC handle with the channel to be scanned
				if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK){
					_Error_Handler(__FILE__, __LINE__);
				}
			}
			// Enable the multiplexor
			HAL_GPIO_WritePin(GPIOB, GPIO_PIN_15, GPIO_PIN_SET);
			// Select rows
			HAL_GPIO_WritePin(GPIOB, GPIO_PIN_14, (int)(row/2) );
			HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, row%2 );

			// Select ADC8 and ADC9
			for(int i = 8; i <= 9; ++i){
				sConfig.Rank = i-5;
				sConfig.Channel = i;
				// Configure ADC handle with the channel to be scanned
				if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK){
					_Error_Handler(__FILE__, __LINE__);
				}
			}
			// Sensor is being run in discontinuous mode and so needs to
			// be restarted every time since it stops after 1 reading.
//			HAL_ADC_Start(&hadc1);
			// Read 4 sensor values
			for(int i = 0; i < 4; ++i){
				if(HAL_ADC_PollForConversion(&hadc1, 1000) == HAL_OK){
					tr->curr_values[tr->n_read + i] = HAL_ADC_GetValue(&hadc1);
				}
			}
			// Update the number of values read
			tr->n_read += 4;
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
