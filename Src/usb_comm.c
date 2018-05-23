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


void USBComm_Init(USBComm_HandleTypeDef *uc){
	uc->state = UC_RESET;
	uc->sendBuffer = calloc(MAX_NUM_VALUES, sizeof(uint16_t));
	uc->recvBuffer = NULL;
}

int USBComm_NextState(USBComm_HandleTypeDef *uc){
	switch(uc->state) {
	case UC_COLLECT:
		// State machine collects the data to be sent in this state.
		if(hsc.spikeGenerated){
			// Copy spike values to buffer for sending
			memcpy(uc->sendBuffer, hsc.values, MAX_NUM_VALUES);
			hsc.spikeGenerated = false;
			uc->state = UC_SEND;
		}
		break;
	case UC_SEND:
		// Send data via the USB port
		CDC_Transmit_FS(uc->sendBuffer, MAX_NUM_VALUES);
		uc->state = UC_RESET;
		break;
	case UC_RESET:
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
	free(uc->sendBuffer);
	free(uc->recvBuffer);
}


