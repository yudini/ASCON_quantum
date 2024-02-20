import math
from projectq import MainEngine
from projectq.ops import H, CNOT, Measure, Toffoli, X, All, T, Tdag, S, Swap
from projectq.backends import CircuitDrawer, ResourceCounter, CommandPrinter, ClassicalSimulator
from projectq.meta import Loop, Compute, Uncompute, Control , Dagger
import random

def print_state(eng, b, len): # if b is 128-bit -> len is 32

    All(Measure) | b
    print('0x', end='')
    print_hex(eng, b, len)
    print('\n')

# def print_state(eng, b, n):   # binary
#     All(Measure) | b
#     print('Result : ', end='')
#     for i in range(n):
#         print(int(b[n - 1 - i]), end='')
#     print('\n')

def print_hex(eng, qubits, len):

    for i in reversed(range(len)):
        temp = 0
        temp = temp + int(qubits[4 * i + 3]) * 8
        temp = temp + int(qubits[4 * i + 2]) * 4
        temp = temp + int(qubits[4 * i + 1]) * 2
        temp = temp + int(qubits[4 * i])

        temp = hex(temp)
        y = temp.replace("0x", "")
        print(y, end='')

def AND_gate(eng, a, b, c, ancilla):
    H | c
    CNOT | (b, ancilla)
    CNOT | (c, a)
    CNOT | (c, b)
    CNOT | (a, ancilla)

    Tdag | a
    Tdag | b
    T | c
    T | ancilla

    CNOT | (a, ancilla)
    CNOT | (c, b)
    CNOT | (c, a)
    CNOT | (b, ancilla)

    H | c
    S | c

def AND_gate_dag(eng, a, b, c):
    H | b
    CNOT | (a, b)
    X | c

    with Dagger(eng):
        Measure | c
    H | b
    H | c
def Message_XOR(eng, constant, qubit, len):
    for i in range(len): #length
        if(constant & 1 == 1 ):
            X | qubit[i]
        constant = constant >> 1

def S_constant_XOR(eng,constant,x2):
    for i in range(64):
        if(constant & 1 ==1):
            X | x2[i]
        constant = constant>>1


def add_constant(eng,x2,i):
    Constant= [0xf0, 0xe1, 0xd2, 0xc3, 0xb4, 0xa5, 0x96, 0x87, 0x78, 0x69, 0x5a, 0x4b]
    S_constant_XOR(eng,Constant[i],x2)

def Substitution_Layer(eng, x0, x1, x2, x3, x4, new_ancilla_x0, new_ancilla_x1, new_ancilla_x2, new_ancilla_x3,
                           new_ancilla_x4, new_x0, new_x1, new_x2, new_x3, new_x4):
    # global count
    # count +=1
    ancilla_x0 = eng.allocate_qureg(64)
    ancilla_x1 = eng.allocate_qureg(64)
    ancilla_x2 = eng.allocate_qureg(64)
    ancilla_x3 = eng.allocate_qureg(64)
    ancilla_x4 = eng.allocate_qureg(64)


    for i in range(64):
        CNOT | (x4[i], x0[i])
        CNOT | (x1[i], x2[i])
        CNOT | (x3[i], x4[i])

    for i in range(64):
        CNOT | (x0[i], new_ancilla_x0[i])
        CNOT | (x1[i], new_ancilla_x1[i])
        CNOT | (x2[i], new_ancilla_x2[i])
        CNOT | (x3[i], new_ancilla_x3[i])
        CNOT | (x4[i], new_ancilla_x4[i])

    #
    # for i in range(64):
    #     AND_gate(eng, new_ancilla_x1[i], x2[i], ancilla_x0[i],new_x0[i])
    # for i in range(64):
    #     AND_gate(eng, new_ancilla_x2[i], x3[i], ancilla_x1[i],new_x1[i])
    # for i in range(64):
    #     AND_gate(eng, new_ancilla_x3[i], x4[i], ancilla_x2[i],new_x2[i])
    # for i in range(64):
    #     AND_gate(eng, new_ancilla_x0[i], x1[i], ancilla_x4[i],new_x3[i])
    # for i in range(64):
    #     AND_gate(eng, new_ancilla_x4[i],x0[i], ancilla_x3[i], new_x4[i])

    for i in range(64):
        AND_gate_dag(eng, new_ancilla_x1[i], x2[i], ancilla_x0[i])
    for i in range(64):
        AND_gate_dag(eng, new_ancilla_x2[i], x3[i], ancilla_x1[i])
    for i in range(64):
        AND_gate_dag(eng, new_ancilla_x3[i], x4[i], ancilla_x2[i])
    for i in range(64):
        AND_gate_dag(eng, new_ancilla_x0[i], x1[i], ancilla_x4[i])
    for i in range(64):
        AND_gate_dag(eng, new_ancilla_x4[i], x0[i], ancilla_x3[i])


    for i in range(64):
        CNOT | (x0[i], ancilla_x0[i])
        CNOT | (x1[i], ancilla_x1[i])
        CNOT | (x2[i], ancilla_x2[i])
        CNOT | (x3[i], ancilla_x3[i])
        CNOT | (x4[i], ancilla_x4[i])
    #Uncompute(eng)

    for i in range(64):
        CNOT | (x0[i], new_ancilla_x0[i])
        CNOT | (x1[i], new_ancilla_x1[i])
        CNOT | (x2[i], new_ancilla_x2[i])
        CNOT | (x3[i], new_ancilla_x3[i])
        CNOT | (x4[i], new_ancilla_x4[i])

    for i in range(64):
        CNOT | (ancilla_x0[i],ancilla_x1[i])
        CNOT | (ancilla_x2[i],ancilla_x3[i])
    for i in range(64):
        CNOT | (ancilla_x4[i],ancilla_x0[i])
        X | ancilla_x2[i]


    return ancilla_x0,ancilla_x1,ancilla_x2,ancilla_x3,ancilla_x4

def LinearDiffusion_Layer(eng,x0,x1,x2,x3,x4,new_x0,new_x1,new_x2,new_x3,new_x4):

    for i in range(64):
        CNOT | (x0[i], new_x0[i])
        CNOT | (x1[i], new_x1[i])
        CNOT | (x2[i], new_x2[i])
        CNOT | (x3[i], new_x3[i])
        CNOT | (x4[i], new_x4[i])

    for i in range(64):
        CNOT | (new_x0[(i+19) % 64], x0[i])
        CNOT | (new_x1[(i + 61) % 64], x1[i])
        CNOT | (new_x2[(i + 1) % 64], x2[i])
        CNOT | (new_x3[(i + 10) % 64], x3[i])
        CNOT | (new_x4[(i + 7) % 64], x4[i])
    #b= a+ a>>3
    #a = a + a>>3
    for i in range(64):
        CNOT | (new_x0[(i+28) % 64], x0[i])
        CNOT | (new_x1[(i + 39) % 64], x1[i])
        CNOT | (new_x2[(i + 6) % 64], x2[i])
        CNOT | (new_x3[(i + 17) % 64], x3[i])
        CNOT | (new_x4[(i + 41) % 64], x4[i])

def Permutation_a(eng,pa,x0,x1,x2,x3,x4, new_ancilla_x0, new_ancilla_x1, new_ancilla_x2, new_ancilla_x3, new_ancilla_x4):
    # S = (MSB) x0  ||  x1  ||  x2  ||  x3  || x4 (LSB)
    #       256:320   192:256 128:192  64:128   0:64

    for i in range(pa):
        new_x0 = eng.allocate_qureg(64)
        new_x1 = eng.allocate_qureg(64)
        new_x2 = eng.allocate_qureg(64)
        new_x3 = eng.allocate_qureg(64)
        new_x4 = eng.allocate_qureg(64)

        add_constant(eng,x2,i)
        x0,x1,x2,x3,x4 = Substitution_Layer(eng, x0, x1, x2, x3, x4, new_ancilla_x0, new_ancilla_x1, new_ancilla_x2, new_ancilla_x3,new_ancilla_x4, new_x0, new_x1, new_x2, new_x3, new_x4)  # correct
        LinearDiffusion_Layer(eng, x0, x1, x2, x3, x4, new_x0, new_x1, new_x2, new_x3, new_x4)
def main(eng, M_value, len):

    M = eng.allocate_qureg(len)
    h_len = 384

    if(resource_check !=1):
        Message_XOR(eng, M_value, M, len)

    Hash = eng.allocate_qureg(h_len)
    #Hash = eng.allocate_qureg(256)

    x0 = eng.allocate_qureg(64)
    x1 = eng.allocate_qureg(64)
    x2 = eng.allocate_qureg(64)
    x3 = eng.allocate_qureg(64)
    x4 = eng.allocate_qureg(64)

    new_ancilla_x0 = eng.allocate_qureg(64)
    new_ancilla_x1 = eng.allocate_qureg(64)
    new_ancilla_x2 = eng.allocate_qureg(64)
    new_ancilla_x3 = eng.allocate_qureg(64)
    new_ancilla_x4 = eng.allocate_qureg(64)

    temp = len+1
    if (temp % 64 == 0):
        l = int(temp / 64)
    else:
        l = int(temp / 64) + 1

    pa = 12

    # Initialization
    S = (0xb57e273b814cd416, 0x2b51042562ae2420, 0x66a3a7768ddf2218, 0x5aad0a7a8153650c, 0x4f3e0e32539493b6)

    # S => x0 | x1 | x2 | x3 | x4
    # x0 => S_r , x1 | x2 | x3 | X4 => S_c

    S_constant_XOR(eng, S[0], x0)
    S_constant_XOR(eng, S[1], x1)
    S_constant_XOR(eng, S[2], x2)
    S_constant_XOR(eng, S[3], x3)
    S_constant_XOR(eng, S[4], x4)

    for i in range(64):
        X | new_ancilla_x0[i]
        X | new_ancilla_x1[i]
        X | new_ancilla_x2[i]
        X | new_ancilla_x3[i]
        X | new_ancilla_x4[i]

    # Absorbing

    for number in range(l): # l=7
        if(number != l-1):   # 0,1,2,3,4,5
            for i in range(64):
                CNOT | (M[len - (64*(number+1)) + i], x0[i])

            Permutation_a(eng,pa,x0,x1,x2,x3,x4, new_ancilla_x0, new_ancilla_x1, new_ancilla_x2, new_ancilla_x3, new_ancilla_x4)

        else :   #6
            left_len = len-64*number    #0
            start = 64-left_len         #64
            for i in range(left_len):
                CNOT | (M[i], x0[i+start])

            X | x0[63-left_len]

    Permutation_a(eng, pa, x0, x1, x2, x3, x4, new_ancilla_x0, new_ancilla_x1, new_ancilla_x2, new_ancilla_x3, new_ancilla_x4)

    #Squeezing

    for i in range(int(h_len/64)): #6
        for j in range(64):
            CNOT | (x0[j],Hash[64*(int(h_len/64)-1-i)+j])

        if (i != int(h_len/ 64) - 1): # 0,1,2,3,4
            Permutation_a(eng, pa, x0, x1, x2, x3, x4, new_ancilla_x0, new_ancilla_x1, new_ancilla_x2, new_ancilla_x3, new_ancilla_x4)

    if(resource_check!=1):
        #print_state(eng,Hash,64)
        print_state(eng, Hash, 96)

    # Msg = 000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F
    # MD = 0B8E325B9BBF1BB43E77AA1EED93BEE62B4EA1E4B0C5A696B2F5C5B09C968918

global resource_check
global AND_check
global count
count =0
# print('Generate Ciphertext...')
# Simulate = ClassicalSimulator()
# eng = MainEngine(Simulate)
# resource_check = 0
# main(eng, 0x000102030405060708090a0b0c0d0e0f1011121314151617,192)
#main(eng, 0x000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F202122232425262728292A2B2C2D2E2F,384)

print('Estimate cost...')
Resource = ResourceCounter()
eng = MainEngine(Resource)
resource_check = 1
AND_check = 0
main(eng, 0x000102030405060708090A0B0C0D0E0F101112131415161718191A1B1C1D1E1F202122232425262728292A2B2C2D2E2F,384)
print(Resource)
print('\n')
eng.flush()