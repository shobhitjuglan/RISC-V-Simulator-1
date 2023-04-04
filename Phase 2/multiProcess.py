import multiprocessing as mp
import time
from multiprocessing import Manager
import sys
import os
import argparse



register = [0] * 32


MEM = [0] * 4000
data_mem = [0] * 100000000

preparation_status = {
    # 1 - Ready
    # 0 - Not Ready
    'pc': 1,
    'instruction_word': 1,
    'rs2':1,
}

stage1 = {
    'pc': 0,
}

# dictionary for the fetch-decode stage
stage2 = {
    'instruction_word': 0,
    'pc':0,
}

# dictionary for the decode-execute stage
stage3 = {
    'operand1':0,
    'operand2':0,
    'inst_type':'R',
    'immFinal':0,
    'pc':0,
    'rs2':0,
    'rd':0,
}

# dictionary for the execute-memory stage
stage4 = {
    'inst_type':'R',
    'ALUResult':0,
    'rs2':0,
    'immFinal': 0,
    'rd': 0,

}

# dictionary for the memory-writeback stage
stage5 = {
    'inst_type':'R',
    'ReadData':0,
    'rd': 0,
    'immFinal': 0,
    'ALUResult':0,
}

stage6={
    'ALUResult':0,
}

# creating 4 dictionaries for each stage
# dictionary for the fetch stage

registerCheck = [1 for i in range(32)]
# print("registerCheck= ")
# print(registerCheck)    
# functions to be made----> fetch, decode, execute, memory, writeback


'''

Ready Bit
1 -> Ready
0 -> Not Ready

'''

def reset_proc():
    pass

def load_program_memory(file, MEM):
    '''
        Load program Memory
    '''
    f = open(file, 'r')

    for line in f.readlines():
        address, instruction = line.split()

        address = int(address,16)
        instruction = int(instruction,16)

        write_word(address, instruction, MEM)

    f.close()



def fetch(pipe1, out1):
    '''
        Fetch Instruction
    '''
    # destructure variables
    pc, fetch_ready, MEM, decode_ready = pipe1



    if (fetch_ready):
        print("FETCH")
        print("PC: ", pc)
    
        # global instruction_word
        instruction_word = read_word(pc, MEM)
        print("instruction_word in fetch after read_Word=",hex(instruction_word))
        print("instruction word in binary=",bin(instruction_word))

        if (instruction_word == 0xfffffffb):
            out1[0] = 0
            out1[1] = 0
            out1[2] = 0
            out1[3] = 0
            out1[4] = 0
            out1[5] = 0
            out1[6] = 0
            out1[7] = 0
            out1[8] = 0
            out1[9] = 0
            return 
        
        opcode_mask = 0b1111111
        opcode = instruction_word & opcode_mask

        # find first  source register
        rs1 = instruction_word
        rs1 = rs1 >> 15
        rs1_mask = 0b11111
        rs1 = rs1 & rs1_mask
        # print("rs1: ", rs1)

        # find second source register
        rs2 = instruction_word
        rs2 = rs2 >> 20
        rs2_mask = 0b11111
        rs2 = rs2 & rs2_mask

        # find destination register
        rd = instruction_word
        rd = rd >> 7
        rd_mask = 0b11111
        rd = rd & rd_mask
        # print("rd: ", rd)

        # find func3
        func3 = instruction_word
        func3 = func3 >> 12
        func3_mask = 0b111
        func3 = func3 & func3_mask

        # find func7
        func7 = instruction_word
        func7 = func7 >> 25
        func7_mask = 0b1111111
        func7 = func7 & func7_mask

        # generate Immediate --> space left intentionally

        imm = instruction_word
        imm = imm >> 20
        imm_mask = 0b111111111111
        imm = imm & imm_mask

        immS=instruction_word
        immS1=immS>>7
        immS2=immS>>25
        immS_mask1=0b11111
        immS_mask2=0b1111111
        immS=(immS1 & immS_mask1)+((immS2 & immS_mask2)<<5)

        # IMM B Generation
        immB=instruction_word
        immB1=instruction_word>>7
        # print("instruction word=",bin(instruction_word),"and instruction word<<5=",bin(instruction_word<<5),"and instruction_word>>5=",bin(instruction_word>>5))
        immB_mask1=0b1#for 11th
        immB2=instruction_word>>7
        immB_mask2=0b11110
        immB3=instruction_word>>25
        immB_mask3=0b111111
        immB4=instruction_word>>31
        immB_mask4=0b1#for 12th

        immB=((immB1 & immB_mask1)<<11) + ((immB2 & immB_mask2)) + ((immB3 & immB_mask3)<<5) +((immB4& immB_mask4)<<12)
        # print("immB=",immB,"and immB in binary=",bin(immB))


        immU=instruction_word>>12
        immU_mask=0b11111111111111111111
        immU=((immU&immU_mask)<<12)
        # print(hex(immU))

        immJ = instruction_word
        immJ1=instruction_word>>12
        immJ_mask1=0b11111111
        immJ2=instruction_word>>20
        immJ_mask2=0b1
        immJ3=instruction_word>>21
        immJ_mask3=0b1111111111
        immJ4=instruction_word>>31
        immJ_mask4=0b1
        immJ = ((immJ1 & immJ_mask1) << 12) + \
            ((immJ2 & immJ_mask2) << 11) + \
            ((immJ3 & immJ_mask3) << 1)+((immJ4 & immJ_mask4) << 20)
        

        print("opcode here=",bin(opcode))
        inst_type = getInstructionType(opcode)
        print("Instruction type is: ",inst_type)

        immFinal = getFinalImmediate(inst_type, imm, immS ,immB, immU, immJ) 
        print("Final immediate is: ",immFinal, " in hex: ", hex(immFinal))

        decode_ready = 1

        out1[0] = pc
        out1[1] = opcode
        out1[2] = rs1
        out1[3] = rs2
        out1[4] = rd
        out1[5] = func3
        out1[6] = func7
        out1[7] = immFinal
        out1[8] = inst_type
        out1[9] = decode_ready
        # pc, opcode, rs1, rs2, rd, func3, func7, immFinal, instructionType, decode_ready
        # out1 = list([rs1, rs2, rd, immFinal, func3, func7, inst_type, opcode])
        # print("Decode ready: ", out1[9])
        return 

        sys.exit(0)
        # get instruction type
        instructionType = getInstructionType(opcode)

        if(instructionType=='S' or instructionType=='B'):
            # do nothing
            None
        else:
            # set ready bit
            ready[rd]=0

        # also return immFinal
        return [rs1, rs2, rd, func3, func7, ready, instructionType]

        
    

    # counter[0] += 1
def decode(pipe2, out2):

    # destructure arguments
    pc, opcode, rs1, rs2, rd, func3, func7, immFinal, instructionType, decode_ready = pipe2
    
    print("Ready: ")

    if (decode_ready):
        print("DECODE")
        ALUop = getALUop(instructionType, func3, func7)  
        operand1, operand2 = op2selectMUX(instructionType, rs1, rs2, immFinal)
        BranchTargetSelect = BranchTargetSelectMUX(instructionType, immFinal) #this is left
        MemOp = getMemOp(instructionType, opcode)
        RFWrite, ResultSelect = ResultSelectMUX(opcode, instructionType)
        isBranch = isBranchInstruction(opcode, instructionType, func3, operand1, operand2)
        
        # printing operation details
        printOperationDetails(instructionType, immFinal, operand1, operand2, rd, ALUop) # this is not required
        
        execute_ready = 1

        out2[0] = pc
        out2[1] = ALUop
        out2[2] = BranchTargetSelect
        out2[3] = ResultSelect
        out2[4] = immFinal
        out2[5] = operand1
        out2[6] = operand2
        out2[7] = rd
        out2[8] = MemOp
        out2[9] = isBranch
        out2[10] = RFWrite
        out2[11] = execute_ready

        # out2 = list(ALUop, ready, immFinal, operand1, operand2, rd, BranchTargetSelect, MemOp, ResultSelect, isBranch, ready, pc)
        return
    else:
        out2[0] = 0
        out2[1] = 0
        out2[2] = 0
        out2[3] = 0
        out2[4] = 0
        out2[5] = 0
        out2[6] = 0
        out2[7] = 0
        out2[8] = 0
        out2[9] = 0
        out2[10] = 0
        out2[11] = 0

        return

    
def execute(pipe3, out3):

    # destructure arguments
    pc, ALUop, BranchTargetResult, ResultSelect, immFinal, operand1, operand2, rd, MemOp, isBranch, RFWrite, execute_ready = pipe3
    print("Pipe3: ", pipe3)
    '''
    ALUop operation
    0 - perform none (skip)
    1 - add
    2 - subtract
    3 - and
    4 - or
    5 - shift left
    6 - shift right
    7 - xor
    8 - set less than
    '''

    # ready variable is used to check if the instruction is to be executed or not

    if (execute_ready):
        print("EXECUTE")
        ALUResult = 0
        
        if (ALUop == 1):
            ALUResult = operand1 + operand2
        elif (ALUop == 2):
            ALUResult = operand1 - operand2
        elif (ALUop == 3):
            ALUResult = operand1 & operand2
        elif (ALUop == 4):
            ALUResult = operand1 | operand2
        elif (ALUop == 5):
            ALUResult = operand1 << operand2
        elif (ALUop == 6):
            ALUResult = operand1 >> operand2
        elif (ALUop == 7):
            ALUResult = operand1 ^ operand2
        elif (ALUop == 8):
            ALUResult = 1 if (operand1 < operand2) else 0

        # print("ALUResult: ", ALUResult)
        # print("BranchTargetResult=",BranchTargetResult)
        BranchTargetAddress=BranchTargetResult+(pc*4)

        memory_ready = 1

        out3[0] = pc
        out3[1] = MemOp
        out3[2] = ALUResult
        out3[3] = operand2
        out3[4] = RFWrite
        out3[5] = ResultSelect
        out3[6] = rd
        out3[7] = immFinal
        out3[8] = isBranch
        out3[9] = BranchTargetAddress
        out3[11] = memory_ready

        # [BranchTargetAddress, ALUResult, pc, MemOp, isBranch, MemOp, ALUResult, pc, ResultSelect, rd, immFinal, isBranch, BranchTargetResult, ready]
        return 
    else:
        out3[0] = 0
        out3[1] = 0
        out3[2] = 0
        out3[3] = 0
        out3[4] = 0
        out3[5] = 0
        out3[6] = 0
        out3[7] = 0
        out3[8] = 0
        out3[9] = 0
        out3[10] = 0
        out3[11] = 0

        return


    
def Memory(pipe4, out4):

    # destructure arguments
    pc, MemOp, ALUResult, operand2, RFWrite, ResultSelect, rd, immFinal, isBranch, BranchTargetAddress, data_mem, mem_ready = pipe4

    '''
    MemOp operation
    0 - Do nothing (skip)
    1 - Write in memory --> Store
    2 - Read from memory --> Load
    '''
    if (mem_ready):
        ReadData = 0

        print()
        print("MEMORY")

        if (MemOp == 0):
            print("There is no Memory Operation")
            ReadData = ALUResult
        elif (MemOp == 1): 
            # Store

            # unsigned int *data_p;
            # data_p = (unsigned int*)(DataMEM + ALUResult);
            data_mem[ALUResult] = operand2
            ReadData = data_mem[ALUResult]
            # int rs2Value = BintoDec(rs2,5);
            # *data_p = X[rs2Value];
            # ReadData = X[rs2Value];
            print("There is a Store Operation to be done from memory")
        elif (MemOp == 2):
            # Load
            # int *data_p;
            # data_p = (int*)(DataMEM + ALUResult);
            # ReadData = *data_p;
            ReadData = data_mem[ALUResult]
            print("There is a Read Operation to be done from memory")

        MemOp = 0

        write_ready = 1

        out4[0] = pc
        out4[1] = RFWrite
        out4[2] = ResultSelect
        out4[3] = rd
        out4[4] = immFinal
        out4[5] = ReadData
        out4[6] = ALUResult
        out4[7] = isBranch
        out4[8] = BranchTargetAddress
        out4[9] = write_ready

        return
    else:
        out4[0] = 0
        out4[1] = 0
        out4[2] = 0
        out4[3] = 0
        out4[4] = 0
        out4[5] = 0
        out4[6] = 0
        out4[7] = 0
        out4[8] = 0
        out4[9] = 0
        return
        return [RFWrite, pc, ResultSelect, rd, immFinal, ReadData, ALUResult, isBranch, BranchTargetAddress, ready]
    
def Write(pipe5, out5):

    # destructure arguments
    # print(args)
    pc, RFWrite, ResultSelect, rd, immFinal, ReadData, ALUResult, isBranch, BranchTargetAddress, write_ready, register = pipe5

    '''
        ResultSelect
        5 - None
        0 - PC+4
        1 - ImmU_lui
        2 - ImmU_auipc
        3 - LoadData - essentially same as ReadData
        4 - ALUResult
    '''

    if (write_ready):
        print("WRITEBACK ")

        print("RESULTSELECT",ResultSelect)

        if (RFWrite):
            if (ResultSelect == 0):
                register[rd] =4 * (pc + 1)
                print("Write Back  ", 4*(pc+1), "to R", rd)
            elif (ResultSelect == 1):
                register[rd] = immFinal
                print("Write Back to ", immFinal, "to R", rd)
            elif (ResultSelect == 2):
                register[rd] = pc*4 + immFinal
                print("Write Back to ", immFinal, "to R", rd)
            elif (ResultSelect == 3):
                register[rd] = ReadData
                print("Write Back  ", ReadData, "to R", rd)
            elif (ResultSelect == 4):
                register[rd] = ALUResult
                print("Write Back to ", ALUResult, "to R", rd)
        else:
            print("There is no Write Back")

        '''
            IsBranch=0 => ALUResult
            =1         => BranchTargetAddress
            =2         => pc+4(default)
        '''

        print("Isbranch is ",isBranch)
        if (isBranch == 0):
            print("ALUResult=",ALUResult)
            pc = ALUResult
            pc//=4
        elif (isBranch == 1):
            print("BranchTargetAddress=",BranchTargetAddress)
            pc = BranchTargetAddress
            pc//=4
        else:
            pc += 1

        out5[0] = pc
        out5[1] = register

        return
    else:
        out5[0] = 0
        out5[1] = 0
        return
    
        # return pc, ready


def op2selectMUX(inst_type, rs1, rs2, imm_final):
    '''
        Op2SelectMUX
    '''
    # global operand1, operand2
    operand1 = register[rs1]
    if (inst_type == 'S' or inst_type == 'I'):
        operand2 = imm_final
    else:
        operand2 = register[rs2]
    
    return operand1, operand2

    
    
def run_riscvsim():
    
    with Manager() as manager:

        process_list = []

        # for i in range(10):
        #     p =  mp.Process(target= fetch(counter))
        #     p.start()
        #     process_list.append(p)
        # p1 =  mp.Process(target= fetch, args=[counter])pc, ready, MEM

        fetch_ready = 1
        decode_ready = 0
        execute_ready = 0
        mem_ready = 0
        write_ready = 0

        pc = 0
        opcode = 0
        rs1 = 0
        rs2 = 0
        rd = 0
        func3 = 0
        func7 = 0
        immFinal = 0
        instructionType = 0
        ALUop = 0
        BranchTargetResult = 0
        ResultSelect = 0
        operand1 = 0
        operand2 = 0
        MemOp = 0
        isBranch = 0
        RFWrite = 0
        ALUResult = 0
        BranchTargetAddress = 0
        ReadData = 0


        pipe1 = manager.list([pc, fetch_ready, MEM, decode_ready])
        out1 = manager.list([0]*10) #Stage 1 out

        pipe2 = manager.list([pc, opcode, rs1, rs2, rd, func3, func7, immFinal, instructionType, decode_ready])
        out2 = manager.list([0]*12)

        pipe3 = manager.list([pc, ALUop, BranchTargetResult, ResultSelect, immFinal, operand1, operand2, rd, MemOp, isBranch, RFWrite, execute_ready])
        out3 = manager.list([0]*12)

        pipe4 = manager.list([pc, MemOp, ALUResult, operand2, RFWrite, ResultSelect, rd, immFinal, isBranch, BranchTargetAddress, data_mem, mem_ready])
        out4 = manager.list([0]*11)

        pipe5 = manager.list([pc, RFWrite, ResultSelect, rd, immFinal, ReadData, ALUResult, isBranch, BranchTargetAddress, write_ready, register])
        out5 = manager.list([0]*2)

        for i in range(5):
            print("Pipe 3: ", pipe3)
            p1 =  mp.Process(target= fetch, args=(pipe1, out1))
            p2 =  mp.Process(target= decode, args=(pipe2, out2))
            p3 =  mp.Process(target= execute, args=(pipe3, out3))
            p4 =  mp.Process(target= Memory, args=(pipe4, out4))
            p5 =  mp.Process(target= Write, args=(pipe5, out5))
            
            p1.start()
            p2.start()
            p3.start()
            p4.start()
            p5.start()

            process_list.append(p1)
            process_list.append(p2)
            process_list.append(p3)
            process_list.append(p4)
            process_list.append(p5)

            for process in process_list:
                process.join()
            print("Out 1: ", out1)
            print("Out 2: ", out2)
            print("Out 3: ", out3)
            print("Out 4: ", out4)
            print("Out 5: ", out5)
            print("-------------------------------------------------------")

            pipe2 = out1
            pipe3 = out2
            pipe4 = out3
            pipe5 = out4

            # out3[10] = data_mem #Data memory
            out4[10] = register
            if (out1[9] != 0):
                pass
            #     pipe1[0] += 1   #move to next instruction
        print("Register: ", register)

# fetch helper functions


def write_word(address, instruction, MEM):
    '''
        Write Word
    '''
    index = address/4
    MEM[int(index)] = instruction

def read_word(address, MEM):
    '''
        Read Word
    '''
    # print("address=",address,"MEM[address]=",MEM[address])
    
    return MEM[(address)]


# decode helper functions
def getFinalImmediate(inst_type, imm,immS, immB, immU, immJ):
    immFinal = 0
    if inst_type == 'I':
        immFinal = imm
        if ((immFinal >> 11) == 1):
            immFinal = immFinal-4096
    if inst_type == 'S':
        immFinal= immS
        if((immFinal>>11)==1):
            immFinal=immFinal-4096
    if inst_type == 'B':
        immFinal = immB
        if ((immFinal >> 12) == 1):
            immFinal = immFinal-8192
    if inst_type == 'U':
        immFinal= immU
    if inst_type == 'J':
        immFinal = immJ
        if ((immFinal >> 20) == 1):
            immFinal = immFinal-2097152
    return immFinal

def getInstructionType(opcode):
    '''Get Type of Instruction from opcode'''
    inst_type = ''
    print("opcode in getinstructiontype=",bin(opcode))
    if (opcode == 0b0110011):
        inst_type = 'R'
    elif (opcode == 0b0010011 or opcode == 0b0000011 or opcode == 0b1100111):
        inst_type = 'I'
    elif (opcode == 0b0100011):
        inst_type = 'S'
    elif (opcode == 0b1100011):
        inst_type = 'B'
    elif (opcode == 0b0110111):
        inst_type = 'U'
    elif (opcode == 0b1101111):
        inst_type = 'J'
    else:
        print("Not valid instruction type Detected")
        sys.exit(1)
    
    return inst_type


def BranchTargetSelectMUX(inst_type, imm_final):
    '''
        Branch Target Select MUX
    '''

    BranchTargetResult = imm_final

    return BranchTargetResult

def getMemOp(instType, opcode):
    '''
        Get Mem Op
    '''
    if (instType == 'S'):
        MemOp = 1
    elif (opcode == 0b0000011):
        MemOp = 2
    else:
        MemOp = 0

    return MemOp

def ResultSelectMUX(opcode, inst_type):
    '''
    ResultSelect
    5 - None
    0 - PC+4
    1 - ImmU_lui
    2 - ImmU_auipc
    3 - LoadData - essentially same as ReadData
    4 - ALUResult
    '''

    RFWrite = 0
    ResultSelect = None

    if (opcode == 0b0110111):
        ResultSelect = 1
        RFWrite = 1
    elif (opcode == 0b0010111):
        ResultSelect = 2
        RFWrite = 1
    elif (opcode == 0b1101111 or opcode == 0b1100111):
        ResultSelect = 0
        RFWrite = 1
    elif (opcode == 0b0000011):
        ResultSelect = 3
        RFWrite = 1
    elif (opcode == 0b0100011 or inst_type == 'B'):
        RFWrite = 0
    else:
        ResultSelect = 4
        RFWrite = 1

    return RFWrite, ResultSelect

def isBranchInstruction(opcode, inst_type, func3, operand1, operand2):
    '''
        Check weather the condition is a branch instruction

        IsBranch=0 => ALUResult
        =1         => BranchTargetAddress
        =2         => pc+4(default)
    '''

    if (opcode == 0b1100111):
        isBranch = 0
    elif (inst_type == 'B'):
        isBranch = 2
        if (func3 == 0x0 and operand1 == operand2):
            isBranch = 1
        elif (func3 == 0x1 and operand1 != operand2):
            isBranch = 1
        elif (func3 == 0x4 and operand1 < operand2):
            isBranch = 1
        elif (func3 == 0x5 and operand1 >= operand2):
            isBranch = 1
    elif (inst_type == 'J'):
        isBranch = 1
    else:
        isBranch = 2

    return isBranch


def getALUop(inst_type, func3, func7):
    '''
    ALUop operation
    0 - perform none (skip)
    1 - add
    2 - subtract
    3 - and
    4 - or
    5 - shift left
    6 - shift right
    7 - xor
    8 - set less than
    '''
    ALUop = 0

    if (inst_type == 'R'):
        if (func3 == 0x0):
            if (func7 == 0x0):
                ALUop = 1
            elif (func7 == 0x20):
                ALUop = 2

        elif (func3 == 0x4):
            ALUop = 7
        elif (func3 == 0x6):
            ALUop = 4
        elif (func3 == 0x7):
            ALUop = 3
        elif (func3 == 0x1):
            ALUop = 5
        elif (func3 == 0x5):
            ALUop = 6
    elif (inst_type == 'I'):
        if (func3 == 0x0):
            ALUop = 1
        elif (func3 == 0x7):
            ALUop = 3
    if inst_type == 'I':
        if ((func3 == 0x0) or (func3 == 0x2) or (func3 == 0x1)):
            ALUop = 1
        elif func3 == 0x6:
            ALUop = 4
        elif func3 == 0x7:
            ALUop = 3
    if inst_type == 'S':
        ALUop = 1
    if inst_type == 'B':
        ALUop = 2
    if inst_type == 'U' or inst_type == 'J':
        ALUop = 1
    
    return ALUop


def printOperationDetails(inst_type, immFinal, operand1, operand2, rd, ALUop):
    '''
        Print Operation Details
    '''

    if (inst_type == 'R'):
        if (ALUop == 1):
            print("Instruction Type is ADD")
        elif (ALUop == 3):
            print("Instruction Type is AND")

        print("Operands are: ", operand1, operand2)
        print("Write Register is: ", rd)
    elif (inst_type == 'I'):
        if (ALUop == 1):
            print("Instruction Type is ADDI")
        elif (ALUop == 3):
            print("Instruction Type is ANDI")

        print("Operand is: ", operand1)
        print("Immediate is: ", immFinal)
        print("Write Register is: ", rd)



def init():
    parser = argparse.ArgumentParser(
                    prog='RISC V Simulator',
                    description='This program Simulates the RISC V Architecture computer',
                    epilog='Text at the bottom of help')
    
    parser.add_argument('--file', help='filename')

    args = parser.parse_args()

    if args.file:
        # print(args.file)

        reset_proc()
        load_program_memory(args.file, MEM)
        run_riscvsim()


    else:
        print("Incorrect number of arguments. Please invoke the simulator \n\t./myRISCVSim <input mem file>")
        sys.exit(0)


if __name__=='__main__':
    init()