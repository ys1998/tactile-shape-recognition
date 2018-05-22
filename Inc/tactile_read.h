/*
 * tactile_read.h
 *
 *  Created on: May 17, 2018
 *      Author: Yash
 */

#ifndef INC_TACTILE_READ_H_
#define INC_TACTILE_READ_H_

#include <stdbool.h>

/*
 * State declaration
 */
typedef enum {
	TR_SETUP,
	TR_IDLE,
	TR_BUSY,
	TR_COMPLETED
} TR_States;

typedef struct {
	// state of the reader
	TR_States state;
	// buffer to store current read values
	uint16_t *curr_values;
	// cache to hold previously held values for processing
	uint16_t *stable_values;
	// number of values read
	uint8_t n_read;
	// boolean denoting whether cache buffer has been filled
	bool done;
} TR_HandleTypeDef;

/*
 * Associated functions for the tactile reader.
 */

// constructor
void TR_Init(TR_HandleTypeDef *htr);
// 'step' function for the state-machine
int TR_NextState(TR_HandleTypeDef *htr);

#endif /* INC_TACTILE_READ_H_ */
