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

/* Global Variables */
extern ADC_HandleTypeDef hadc1;
extern TR_HandleTypeDef htr;

uint8_t MAX_NUM_VALUES = 128;

void TR_Init(TR_HandleTypeDef *tr){
	tr->state = TR_SETUP;
	tr->done = false;
	tr->stable_values = calloc(MAX_NUM_VALUES, sizeof(uint16_t));
	tr->curr_values = calloc(MAX_NUM_VALUES, sizeof(uint16_t));
	tr->n_read = 0;
}

int TR_NextState(TR_HandleTypeDef *tr){
	switch(tr->state) {
	case TR_SETUP: ;
		// Set 'col' to be read
		uint8_t col = tr->pos/16;
		if(col >= 4){
			tr->state = TR_COMPLETED;
		}else{
			// Set 'col' pin LOW and others HIGH, so that there is non-zero
			// potential difference between the reference voltage and 'col' pin
			// and current flows through it.
			for(int i = 0; i< 4; ++i){
				if(i == col){
					// Column to be read has to be grounded
					HAL_GPIO_WritePin(GPIOB, 3+i, GPIO_PIN_RESET);
				}else{
					// All other columns are set to HIGH
					HAL_GPIO_WritePin(GPIOB, 3+i, GPIO_PIN_SET);
				}
			}
			tr->state = TR_BUSY;
		}
		break;
	case TR_IDLE:
		// State machine waits in this state until the 'curr_values' has been
		// converted into a spike and the 'done' signal has been reset.
		if(!tr->done){
			// Update 'pos' so that next cell is read
			tr->pos += 1;
			if(tr->pos % 16 == 0){
				tr->state = TR_SETUP;
			}else{
				tr->state = TR_BUSY;
			}
		}
		break;
	case TR_BUSY: ;
		debug_2[0]=2;
		CDC_Transmit_FS(debug_2, 1);
		uint8_t row = tr->pos % 16;

		ADC_ChannelConfTypeDef sConfig;
		sConfig.Rank = ADC_REGULAR_RANK_1;
		sConfig.SamplingTime = ADC_SAMPLETIME_1CYCLE_5;

		if(row < 8){
			// Select channel
			sConfig.Channel = row;
		}else{
			// Enable the multiplexor
			HAL_GPIO_WritePin(GPIOB, 15, GPIO_PIN_SET);
			// Select rows
			HAL_GPIO_WritePin(GPIOB, 14, (row - 8)/2 );
			HAL_GPIO_WritePin(GPIOB, 13, (row - 8)%2 );
			// Select channel
			sConfig.Channel = (row + 8)/2;
		}
		// Configure ADC handle with the channel to be scanned
		if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK){
			_Error_Handler(__FILE__, __LINE__);
		}
		// Sensor is being run in discontinuous mode and so needs to
		// be restarted every time since it stops after 1 reading.
		HAL_ADC_Start(&hadc1);
		// Read sensor value
		if(HAL_ADC_PollForConversion(&hadc1, 1000) == HAL_OK){
			tr->valueRead = HAL_ADC_GetValue(&hadc1);
			tr->done = true;
			tr->state = TR_IDLE;
		}
		break;
	case TR_COMPLETED:
		debug_2[0]=3;
		CDC_Transmit_FS(debug_2, 1);
		// All 64 values have been successfully read
		tr->state = TR_SETUP;
		tr->pos = 0;
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
