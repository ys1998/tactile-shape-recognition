#include "mbed.h"

/*
Created by: Kyle Crockett
For MCP2515duino with 16MHz oscillator.
CNFx register values.
use preprocessor command "_XXkbps" 
"XX" is the baud rate.

10 kbps
CNF1/BRGCON1    b'00110001'     0x31
CNF2/BRGCON2    b'10111000'     0xB8
CNF3/BRGCON3    b'00000101'     0x05

20 kbps
CNF1/BRGCON1    b'00011000'     0x18
CNF2/BRGCON2    b'10111000'     0xB8
CNF3/BRGCON3    b'00000101'     0x05

50 kbps
CNF1/BRGCON1    b'00001001'     0x09
CNF2/BRGCON2    b'10111000'     0xB8
CNF3/BRGCON3    b'00000101'     0x05

100 kbps
CNF1/BRGCON1    b'00000100'     0x04
CNF2/BRGCON2    b'10111000'     0xB8
CNF3/BRGCON3    b'00000101'     0x05

125 kbps
CNF1/BRGCON1    b'00000011'     0x03
CNF2/BRGCON2    b'10111000'     0xB8
CNF3/BRGCON3    b'00000101'     0x05

250 kbps
CNF1/BRGCON1    b'00000001'     0x01
CNF2/BRGCON2    b'10111000'     0xB8
CNF3/BRGCON3    b'00000101'     0x05

500 kbps
CNF1/BRGCON1    b'00000000'     0x00
CNF2/BRGCON2    b'10111000'     0xB8
CNF3/BRGCON3    b'00000101'     0x05

800 kbps
Not yet supported

1000 kbps
Settings added by Patrick Cruce(pcruce_at_igpp.ucla.edu)
CNF1=b'10000000'=0x80 = SJW = 3 Tq. & BRP = 0
CNF2=b'10010000'=0x90 = BLTMode = 1 & SAM = 0 & PS1 = 3 & PR = 1
CNF3=b'00000010'=0x02 = SOF = 0  & WAKFIL = 0 & PS2 = 3

*/
#ifndef MCP2515_h
#define MCP2515_h

#define SCK 13 //spi
#define MISO 12
#define MOSI 11
#define SS 10
#define RESET 2//reset pin

#define RESET_REG 0xc0  
#define READ 0x03 
#define WRITE 0x02 //read and write comands for SPI

#define READ_RX_BUF_0_ID 0x90
#define READ_RX_BUF_0_DATA 0x92
#define READ_RX_BUF_1_ID 0x94
#define READ_RX_BUF_1_DATA 0x96 //SPI commands for reading MCP2515 RX buffers

#define LOAD_TX_BUF_0_ID 0x40
#define LOAD_TX_BUF_0_DATA 0x41
#define LOAD_TX_BUF_1_ID 0x42
#define LOAD_TX_BUF_1_DATA 0x43
#define LOAD_TX_BUF_2_ID 0x44
#define LOAD_TX_BUF_2_DATA 0x45 //SPI commands for loading MCP2515 TX buffers

#define SEND_TX_BUF_0 0x81
#define SEND_TX_BUF_1 0x82
//#define SEND_TX_BUF_2 0x83 //SPI commands for transmitting MCP2515 TX buffers
#define SEND_TX_BUF_2 0x84

#define READ_STATUS 0xA0
#define RX_STATUS 0xB0
#define BIT_MODIFY 0x05 //Other commands


//Registers
#define CNF0 0x2A
#define CNF1 0x29
#define CNF2 0x28
#define TXB0CTRL 0x30 
#define TXB1CTRL 0x40
#define TXB2CTRL 0x50 //TRANSMIT BUFFER CONTROL REGISTER
#define TXB0DLC 0x35 //Data length code registers
#define TXB1DLC 0x45
#define TXB2DLC 0x55
#define MCP2515CTRL 0x0F //Mode control register
#define MCP2515STAT 0x0E //Mode status register

//------------------------------------------------------------------------------
//Added for ram
// Register Bit Masks
// MCP2515STAT
#define MODE_CONFIG     0x80
#define MODE_LISTEN     0x60
#define MODE_LOOPBACK   0x40
#define MODE_SLEEP      0x20
#define MODE_NORMAL     0x00

//MCP2515 bus error counter
#define TEC            0x1C
#define REC            0x1D

//Mask 0
#define RXM0SIDH    0x20 //Mask0 normal ID high
#define RXM0SIDL    0x21 //Mask0 normal ID low
#define RXM0EID8    0x22 //Mask0 extended ID high
#define RXM0EID0    0x23 //Mask0 extended ID low

//Mask 1
#define RXM1SIDH    0x24 //Mask1 normal ID high
#define RXM1SIDL    0x25 //Mask1 normal ID low
#define RXM1EID8    0x26 //Mask1 extended ID high
#define RXM1EID0    0x27 //Mask1 extended ID low

#define MCP2515INTE        0x2B //Interept permission
#define MCP2515INTF        0x2C //Interept flag
#define EFLG        0x2D //Error flag

#define MASK_SID_ALL_HIT   0x0000 //Mask all
#define MASK_SID_CPL_MATCH 0x07FF //Disable mask


#define MCP2515_RTS         0x80
#define MCP2515_READ_BUFFER 0x90
#define MCP2515_LOAD_BUFFER 0X40

//..............................................................................
//test
// MCP2515INTF
#define RX0IF           0x01
#define RX1IF           0x02
#define TX0IF           0x04
#define TX1IF           0x08
#define TX2IF           0x10
#define ERRIF           0x20
#define WAKIF           0x40
#define MERRF           0x80

// Configuration Registers
#define BFPCTRL         0x0C
#define TXRTSCTRL       0x0D

// TX Buffer 0
#define TXB0CTRL        0x30
#define TXB0SIDH        0x31
#define TXB0SIDL        0x32
#define TXB0EID8        0x33
#define TXB0EID0        0x34
#define TXB0DLC         0x35

// TX Buffer 1
#define TXB1CTRL        0x40
#define TXB1SIDH        0x41
#define TXB1SIDL        0x42
#define TXB1EID8        0x43
#define TXB1EID0        0x44
#define TXB1DLC         0x45

// TX Buffer 2
#define TXB2CTRL        0x50
#define TXB2SIDH        0x51
#define TXB2SIDL        0x52
#define TXB2EID8        0x53
#define TXB2EID0        0x54
#define TXB2DLC         0x55

// RX Buffer 0
#define RXB0CTRL        0x60
#define RXB0SIDH        0x61
#define RXB0SIDL        0x62
#define RXB0EID8        0x63
#define RXB0EID0        0x64
#define RXB0DLC         0x65

// RX Buffer 1
#define RXB1CTRL        0x70
#define RXB1SIDH        0x71
#define RXB1SIDL        0x72
#define RXB1EID8        0x73
#define RXB1EID0        0x74
#define RXB1DLC         0x75

// Buffer Bit Masks
#define RXB0            0x00
#define RXB1            0x02
#define TXB0            0x01
#define TXB1            0x02
#define TXB2            0x04
#define TXB_ALL                  TXB0 | TXB1 | TXB2

#define RXB_RX_STDEXT   0x00
#define RXB_RX_MASK     0x60
#define RXB_BUKT_MASK   (1<<2)

typedef unsigned char byte;

enum MCP2515Mode {CONFIGURATION,NORMAL,SLEEP,LISTEN,LOOPBACK};

class MCP2515
{
public:
    MCP2515(SPI& spi, PinName cs);
    //void begin();//sets up MCP2515
    void baudConfig(int bitRate);//sets up baud

    //Method added to enable testing in loopback mode.(pcruce_at_igpp.ucla.edu)
    void setMode(MCP2515Mode mode) ;//put MCP2515 controller in one of five modes

    void send_0();//request to transmit buffer X
    void send_1();
    void send_2();

    char readID_0();//read ID/DATA of recieve buffer X
    char readID_1();

    char readDATA_0();
    char readDATA_1();

    //extending MCP2515 data read to full frames(pcruce_at_igpp.ucla.edu)
    //data_out should be array of 8-bytes or frame length.
    void readDATA_ff_0(byte* length_out,byte *data_out,unsigned short *id_out);
    void readDATA_ff_1(byte* length_out,byte *data_out,unsigned short *id_out);

    //Adding MCP2515 to read status register(pcruce_at_igpp.ucla.edu)
    //MCP2515 be used to determine whether a frame was received.
    //(readStatus() & 0x80) == 0x80 means frame in buffer 0
    //(readStatus() & 0x40) == 0x40 means frame in buffer 1
    byte readStatus();

    void load_0(byte identifier, byte data);//load transmit buffer X
    void load_1(byte identifier, byte data);
    void load_2(byte identifier, byte data);

    //extending MCP2515 write to full frame(pcruce_at_igpp.ucla.edu)
    //Identifier should be a value between 0 and 2^11-1, longer identifiers will be truncated(ie does not support extended frames)
    void load_ff_0(byte length,unsigned short identifier,byte *data);
    void load_ff_1(byte length,unsigned short identifier,byte *data);
    void load_ff_2(byte length,unsigned short identifier,byte *data);
    
    //--------------------------------------------------------------------------
    //Added for ram
    void writeRegister(byte address, byte data);
    void readRegister(byte address, byte *data_out);
    void reset();
    byte readRXStatus();
    void bitModify(byte address, byte mask, byte data);
    void setMask(unsigned short identifier);
    void setMask_0(unsigned short identifier);
    void setMask_1(unsigned short identifier);
private:
    DigitalOut cs;
    SPI &spi;  
};

#endif
