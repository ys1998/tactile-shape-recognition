/*
 * spike_conv.h
 *
 *  Created on: May 18, 2018
 *      Author: Yash
 */

#ifndef INC_SPIKE_CONV_H_
#define INC_SPIKE_CONV_H_

#include <stdbool.h>
#include "abbr.h"
/*
 * State declaration
 */
typedef enum {
	SC_IDLE,
	SC_BUSY,
} SpikeConv_States;

typedef struct {
	// state of the spike-converter
	SpikeConv_States state;
	// boolean storing whether a spike has been generated
	bool spikeGenerated;
	// position of spike
	uint8_t pos;
	// 'value' of spike (currently analog, will be converted to 0-1 later)
	uint16_t value;
} SpikeConv_HandleTypeDef;

/*
 * Associated functions for the spike converter.
 */

// constructor
void SpikeConv_Init(SpikeConv_HandleTypeDef*);
// 'step' function for the state-machine
Errno SpikeConv_NextState(SpikeConv_HandleTypeDef*);

#endif /* INC_SPIKE_CONV_H_ */
