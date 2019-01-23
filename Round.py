#! /usr/bin/python3
import subprocess
from copy import copy
from migen import *
from migen.fhdl import verilog
from migen.fhdl.verilog import convert

from common import *
from SubBytes import SubBytes
from ShiftRows import ShiftRows
from MixColumns import MixColumns
from AddRoundKey import AddRoundKey

'''
=================================================================================================================================
@module name: Round
@description: 
              
@author: KOS
@contact: khobatha.setetemela@gmail.com
@date: November 2018
@interface:

@parameters:
-DATA_W


@inputs:
-clk: the clock signal
-reset: the module reset signal
-valid_data_in
-data_in
-valid_key_in
-round_key


@outputs:
-valid_out
-data_out
=====================================================================================================================================
'''
class Round(Module): # MixColumn submodule
        def __init__(self,DATA_W):
                self.NO_DBYTES=int(DATA_W/8)
                
                self.valid_data_in=Signal(name="ROUND_valid_data_in")# input text data valid flag signal
                self.data_in=[Signal(8,name="ROUND_data_in{}".format(s)) for s in range(self.NO_DBYTES)]# input text data signal array
                
                self.valid_key_in=Signal(name="ROUND_valid_key_in")# input key data valid flag signal
                self.round_key=[Signal(8,name="ROUND_round_key{}".format(s)) for s in range(self.NO_DBYTES)]# input key data signal array
                
                self.valid_data_out=Signal(name="ROUND_valid_data_out")# output text data valid flag signal
                self.data_out=[Signal(8,name="ROUND_data_out{}".format(s)) for s in range(self.NO_DBYTES)] # output text data signal array

                self.io = set()
                self.io = self.io.union(self.data_in)
                self.io = self.io.union(self.round_key)
                self.io = self.io.union(self.data_out)
                
                ###
                
                self.data_sub2shift=[Signal(8) for s in range(self.NO_DBYTES)]
                self.data_shift2mix=[Signal(8) for s in range(self.NO_DBYTES)]
                self.data_mix2key=[Signal(8) for s in range(self.NO_DBYTES)]
                
                self.valid_sub2shift=Signal()
                self.valid_shift2mix=Signal()
                self.valid_mix2key=Signal()
                
                self.submodules.M_SUB = SubBytes(DATA_W)
                self.submodules.M_SR= ShiftRows(DATA_W)
                self.submodules.M_MIX= MixColumns(DATA_W)
                self.submodules.M_ARK= AddRoundKey(DATA_W,DATA_W)
                
                
                #-------------------------------------
                # SubBytes Module
                #-------------------------------------
                
                
                for b in range(self.NO_DBYTES):
                    self.sync+=If(self.valid_data_in==1,
                                  self.M_SUB.data_in[b].eq(self.data_in[b]))
                
                self.sync+=self.M_SUB.valid_in.eq(self.valid_data_in)
                
                for b in range(self.NO_DBYTES):
                    self.sync+=If(self.M_SUB.valid_out==1,
                                  self.data_sub2shift[b].eq(self.M_SUB.data_out[b]))
                
                self.sync+=self.valid_sub2shift.eq(self.M_SUB.valid_out)
                
                #-------------------------------------
                # ShiftRows Module
                #-------------------------------------
                for b in range(self.NO_DBYTES):
                    self.sync+=If(self.valid_sub2shift==1,
                                  self.M_SR.data_in[b].eq(self.data_sub2shift[b]))
                    
                self.sync+=self.M_SR.valid_in.eq(self.valid_sub2shift)
                
                for b in range(self.NO_DBYTES):
                    self.sync+=If(self.M_SR.valid_out==1,
                                  self.data_shift2mix[b].eq(self.M_SR.data_out[b]))
                    
                self.sync+=self.valid_shift2mix.eq(self.M_SR.valid_out)
                
                #-------------------------------------
                # MixColumns Module
                #-------------------------------------
                
                for b in range(self.NO_DBYTES):
                    self.sync+=If(self.valid_shift2mix==1,
                                  self.M_MIX.data_in[b].eq(self.data_shift2mix[b]))
                
                self.sync+=self.M_MIX.valid_in.eq(self.valid_shift2mix)
                
                for b in range(self.NO_DBYTES):
                     self.sync+=If(self.M_MIX.valid_out==1,
                                   self.data_out[b].eq(self.M_MIX.data_out[b]))
                            
                self.sync+=self.valid_data_out.eq(self.M_MIX.valid_out)
                           
                
                #-------------------------------------
                # AddRoundKey
                #-------------------------------------
                '''
                for b in range(self.NO_DBYTES):
                    self.sync+=If(self.valid_mix2key==1,
                                  self.M_ARK.text_in[b].eq(self.data_mix2key[b]))
                    
                    
                self.sync+=self.M_ARK.valid_text_in.eq(self.valid_mix2key)
                
                for b in range(self.NO_DBYTES):
                    self.sync+=If(self.M_ARK.valid_data_out==1,
                                  self.data_out[b].eq(self.M_ARK.data_out[b]))
                            
                self.sync+=self.valid_data_out.eq(self.M_ARK.valid_data_out),
                '''


def check_Round(dut,data,key):
        for i in range(16):# loop to load testbench inputs onto input ports of our AESCipher core
                yield dut.data_in[i].eq(data[i])# load the ith byte of the plain text
                yield dut.round_key[i].eq(key[i])
        yield dut.valid_data_in.eq(1)
        yield dut.valid_key_in.eq(1)
        
        for i in range(64):
                yield                


                
# Generate RTL for the parent module and the submodules, run through
# icarus for a syntax check
def test_instance_module():
        '''
        sub4 = SubBytes()
        convert(sub4, sub4.io, name="SubBytes").write("SubBytes.v")
        par = AES()
        convert(par, par.io, name="AES").write("AES.v")
        
        par1 = AES_Enc()
        convert(par1, par1.io, name="AES_Enc").write("AES_Enc.v")
        par2 = AES_Dec()
        convert(par2, par2.io, name="AES_Dec").write("AES_Dec.v")
        sub1 = AddRoundKey()
        convert(sub1, sub1.io, name="AddRoundKey").write("AddRoundKey.v")
       
        sub2 = ShiftRows()
        convert(sub2, sub2.io, name="ShiftRows").write("ShiftRows.v")
        
        sub3 = ShiftRowInv()
        convert(sub3, sub3.io, name="ShiftRowInv").write("ShiftRowInv.v")
        sub5 = SubBytesInv()
        convert(sub5, sub5.io, name="SubBytesInv").write("SubBytesInv.v")
        sub6 = SubBytesInv()
        convert(sub6, sub6.io, name="MixColumn").write("MixColumn.v")
        
        sub7 = MixColumns()
        convert(sub7, sub7.io, name="MixColumns").write("MixColumns.v")
        '''
        DATA_W=128
        KEY_L=128
        WORD_L=32
        NO_ROUNDS=10
        #dut=KeyExpansion(DATA_W,KEY_L,WORD_L,NO_ROUNDS)# instantiate AES module here
        #sub7 = KeyExpansion(DATA_W,KEY_L,WORD_L,NO_ROUNDS)
        #convert(sub7, sub7.io, name="KeyExpansion").write("KeyExpansion.v")
        sub7 = AddRoundKey(DATA_W,KEY_L)
        convert(sub7, sub7.io, name="AddRoundKey").write("AddRoundKey.v")
                              
def testbench(dut):
        ptext=[Signal(8) for x in range(16)]# input plain text test signal
        key=[Signal(8) for x in range(16)]# input cipher key test signal
        dummylen=0

        # prompt user for values
        msg ="1234567890123456"#input("Please enter message to encrypt: ")
        key_in ="1234567890123456" #input("Please 16 bytes enter key: ")

        msglen = len(msg) #length of message
        print("[OK] msg length =",msglen)

        #padd the message with dummy bytes to have a message multiples of 16 bytes long
        if msglen % 16 != 0:
                dummylen = 16 - (msglen % 16)
        msg = msg + ("." * dummylen)
        
        print("[OK] new padded message =",msg)

        #new length of msg
        newLen = len(msg)

        # convert inputs to matrices of corresponding ASCII values
        pt = textconverter(msg.encode('utf-8'))
        key_m = keyconverter(key_in.encode('utf-8'))
    
        newLen=16
        count=0x00
        for i in range(newLen):# loop to initialise ptext
                ptext[i]=count+1#pt[i]

        for i in range(16):# loop to initialise key
                key[i]=count+1#key_m[i]

        # allow 256 + 1 clock cycles to tick so that our mem memory is initialised with the 256 words
        #for i in range(256): 
        #       yield

        #yield from check_case(dut,ptext,key)# pass initialised testbench signals to check_case to exercise the dut
        #yield from check_ShiftRows(dut,ptext)# pass initialised testbench signals to check_case to exercise the dut
        #yield from check_MixColumns(dut,ptext)# pass initialised testbench signals to check_case to exercise the dut
        #rcw=0x6c000000
        
        #yield from check_KeyExpansion(dut,ptext)# pass initialised testbench signals to check_case to exercise the dut
        yield from check_Round(dut,ptext,key)# pass initialised testbench signals to check_case to exercise the dut
        #yield from check_SubBytes(dut,ptext)# pass initialised testbench signals to check_case to exercise the dut
        #print("sm_original: {} \nsm_shifted: {}".format((yield dut.sm),(yield dut.sm_shifted)))
        #print("sm_in: {} \nsm_mixed: {}".format((yield dut.sm),(yield dut.sm_out)))
        #print("ptext: {} \nkey: {} \ncipher: {} \nrecovered: {}".format((yield dut.ptext),(yield dut.key),(yield dut.ctext),(yield dut.recovered)))
 
 
 
if __name__ == "__main__":
    #test_instance_module()
    DATA_W=128
    KEY_W=128
    #WORD_L=32
    #NO_ROUNDS=10
    dut=Round(DATA_W)# instantiate AES module here
    run_simulation(dut, testbench(dut),vcd_name="migenAES_Round.vcd")# simulate the module with the logic described in testbench

                           