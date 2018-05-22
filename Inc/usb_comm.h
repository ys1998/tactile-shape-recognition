/*
 * usb_comm.h
 *
 *  Created on: May 18, 2018
 *      Author: Yash
 */

#ifndef INC_USB_COMM_H_
#define INC_USB_COMM_H_

#include "abbr.h"
/*
 * State declaration
 */
typedef enum {
	UC_COLLECT,
	UC_SEND,
	UC_RESET
} USBComm_States;

typedef struct {
	// state of the USB communicator
	USBComm_States state;
	// Send buffer
	uint8_t *sendBuffer;
	// Receive buffer
	uint8_t *recvBuffer;

} USBComm_HandleTypeDef;

/*
 * Associated functions for the USB communicator
 */

// constructor
void USBComm_Init(USBComm_HandleTypeDef*);
// 'step' function for the state-machine
Errno USBComm_NextState(USBComm_HandleTypeDef*);
// destructor
void USBComm_Deinit(USBComm_HandleTypeDef*);



#endif /* INC_USB_COMM_H_ */
