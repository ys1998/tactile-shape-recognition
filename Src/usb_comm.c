/*
 * usb_comm.c
 *
 *  Created on: May 17, 2018
 *      Author: Yash
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "usb_comm.h"
#include "usbd_cdc_if.h"
#include "usbd_cdc.h"
#include "spike_conv.h"

/* Global Variables */

extern SpikeConv_HandleTypeDef hsc;
extern USBComm_HandleTypeDef huc;
extern MAX_NUM_VALUES;

uint8_t *debug_1;

void USBComm_Init(USBComm_HandleTypeDef *uc){
	debug_1 = calloc(1, sizeof(uint8_t));
	debug_1[0]=9;
	CDC_Transmit_FS(debug_1, 1);
	uc->state = UC_RESET;
	uc->sendBuffer = calloc(MAX_NUM_VALUES, sizeof(uint16_t));
	uc->recvBuffer = NULL;
}

int USBComm_NextState(USBComm_HandleTypeDef *uc){
	switch(uc->state) {
	case UC_COLLECT:
		debug_1[0]=6;
		CDC_Transmit_FS(debug_1, 1);
		// State machine collects the data to be sent in this state.
		if(hsc.spikeGenerated){
			// Copy spike values to buffer for sending
			memcpy(uc->sendBuffer, hsc.values, MAX_NUM_VALUES);
			hsc.spikeGenerated = false;
			uc->state = UC_SEND;
		}
		break;
	case UC_SEND:
		debug_1[0]=7;
		CDC_Transmit_FS(debug_1, 1);
		// Send data via the USB port
		CDC_Transmit_FS(uc->sendBuffer, MAX_NUM_VALUES);
		uc->state = UC_RESET;
		break;
	case UC_RESET:
		debug_1[0]=8;
		CDC_Transmit_FS(debug_1, 1);
		memset(uc->sendBuffer, 0, 2 * MAX_NUM_VALUES);
		// memset(uc->recvBuffer, 0, 3);
		uc->state = UC_COLLECT;
		break;
	default:
		// this state should never be reached
		return -1;
	}
	return 0;
}


void USBComm_Deinit(USBComm_HandleTypeDef *uc){
	debug_1[0]=12;
	CDC_Transmit_FS(debug_1, 1);
	free(uc->sendBuffer);
	free(uc->recvBuffer);
}


