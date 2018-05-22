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
#include "spike_conv.h"

/* Global Variables */
extern SpikeConv_HandleTypeDef hsc;
extern USBComm_HandleTypeDef huc;
uint8_t *debug_1;

void USBComm_Init(USBComm_HandleTypeDef *uc){
	debug_1 = calloc(1, sizeof(uint8_t));
	debug_1[0]=9;
	CDC_Transmit_FS(debug_1, 1);
	uc->state = UC_RESET;
	uc->sendBuffer = calloc(3, sizeof(uint8_t));
	uc->recvBuffer = NULL;
}

Errno USBComm_NextState(USBComm_HandleTypeDef *uc){
	switch(uc->state) {
	case UC_COLLECT:
		debug_1[0]=6;
		CDC_Transmit_FS(debug_1, 1);
		// State machine collects the data to be sent in this state.
		if(hsc.spikeGenerated){
			// Copy spike position to buffer
			uc->sendBuffer[0] = hsc.pos;
			// Copy spike value to buffer
			memcpy(&uc->sendBuffer[1], &hsc.value, 2 * sizeof(uint8_t));
			hsc.spikeGenerated = false;
			uc->state = UC_SEND;
		}
		break;
	case UC_SEND:
		debug_1[0]=7;
		CDC_Transmit_FS(debug_1, 1);
		// Send data via the USB port
		CDC_Transmit_FS(uc->sendBuffer, 3);
		uc->state = UC_RESET;
		break;
	case UC_RESET:
		debug_1[0]=8;
		CDC_Transmit_FS(debug_1, 1);
		memset(uc->sendBuffer, 0, 3 * sizeof(uint8_t));
		// memset(uc->recvBuffer, 0, 3);
		uc->state = UC_COLLECT;
		break;
	default:
		// this state should never be reached
		return UNKNOWN_STATE;
	}
	return ALL_WELL;
}


void USBComm_Deinit(USBComm_HandleTypeDef *uc){
	debug_1[0]=12;
	CDC_Transmit_FS(debug_1, 1);
	free(uc->sendBuffer);
	free(uc->recvBuffer);
}


