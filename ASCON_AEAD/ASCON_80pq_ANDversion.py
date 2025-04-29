import math

from projectq import MainEngine
from projectq.ops import H, CNOT, Measure, Toffoli, X, All, T, Tdag, S, Swap
from projectq.backends import CircuitDrawer, ResourceCounter, ClassicalSimulator
from projectq.meta import Loop, Compute, Uncompute, Control, Dagger
import random

# key,nonce,tag,:128, datablock: 64, pa:12, pb:6

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

def Toffoli_gate(eng, a, b, c):

    #Toffoli | (a, b, c)

    if (resource_check):
        if (AND_check):
            ancilla = eng.allocate_qubit()
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

        else:
            Tdag | a
            Tdag | b
            H | c
            CNOT | (c, a)
            T | a
            CNOT | (b, c)
            CNOT | (b, a)
            T | c
            Tdag | a
            CNOT | (b, c)
            CNOT | (c, a)
            T | a
            Tdag | c
            CNOT | (b, a)
            H | c
    else:
        Toffoli | (a, b, c)

def Round_constant_XOR(eng, k, rc, bit):
    for i in range(bit):
        if (rc >> i & 1):
            X | k[i]
    # print_state(eng,k,bit)

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
        x0, x1, x2, x3, x4 = Substitution_Layer(eng, x0, x1, x2, x3, x4, new_ancilla_x0, new_ancilla_x1, new_ancilla_x2,
                                                new_ancilla_x3, new_ancilla_x4, new_x0, new_x1, new_x2, new_x3,
                                                new_x4)  # correct
        LinearDiffusion_Layer(eng, x0, x1, x2, x3, x4, new_x0, new_x1, new_x2, new_x3, new_x4)

def Permutation_b(eng,pb,x0,x1,x2,x3,x4, new_ancilla_x0, new_ancilla_x1, new_ancilla_x2, new_ancilla_x3, new_ancilla_x4):
    for i in range(pb):

        new_x0 = eng.allocate_qureg(64)
        new_x1 = eng.allocate_qureg(64)
        new_x2 = eng.allocate_qureg(64)
        new_x3 = eng.allocate_qureg(64)
        new_x4 = eng.allocate_qureg(64)

        add_constant(eng,x2,i+4)
        x0, x1, x2, x3, x4 = Substitution_Layer(eng, x0, x1, x2, x3, x4, new_ancilla_x0, new_ancilla_x1, new_ancilla_x2,
                                                new_ancilla_x3, new_ancilla_x4, new_x0, new_x1, new_x2, new_x3,
                                                new_x4)  # correct
        LinearDiffusion_Layer(eng, x0, x1, x2, x3, x4, new_x0, new_x1, new_x2, new_x3, new_x4)



def Initialization(eng,pa,x0,x1,x2,x3,x4,key, new_ancilla_x0, new_ancilla_x1, new_ancilla_x2, new_ancilla_x3, new_ancilla_x4):
    Permutation_a(eng,pa,x0,x1,x2,x3,x4, new_ancilla_x0, new_ancilla_x1, new_ancilla_x2, new_ancilla_x3, new_ancilla_x4)

    for i in range(32):
        CNOT | (key[i+128] , x2[i]) #k0

    for i in range(64):
        CNOT | (key[i+64] , x3[i]) # k1
        CNOT | (key[i], x4[i])  # k2

    # if (resource_check != 1):
    #     print_state(eng, x0, 16)
    #     print_state(eng, x1, 16)
    #     print_state(eng, x2, 16)
    #     print_state(eng, x3, 16)
    #     print_state(eng, x4, 16)


def Associated(eng,pb,A,A_len,x0,x1,x2,x3,x4, new_ancilla_x0, new_ancilla_x1, new_ancilla_x2, new_ancilla_x3, new_ancilla_x4):
    for i in range(32):
        CNOT | (A[i],x0[32+i])

    X | x0[31]

    Permutation_b(eng,pb,x0,x1,x2,x3,x4, new_ancilla_x0, new_ancilla_x1, new_ancilla_x2, new_ancilla_x3, new_ancilla_x4)

    X | x4[0]

def Plain(eng,pb,pt,pt_len,ct,x0,x1,x2,x3,x4):
    for i in range(32):
        CNOT | (pt[i],x0[32+i])
        CNOT | (x0[32+i], ct[i])

    X | x0[31]

    if (resource_check != 1):
        print_state(eng, x0, 16)
        print_state(eng, x1, 16)
        print_state(eng, x2, 16)
        print_state(eng, x3, 16)
        print_state(eng, x4, 16)

def Finalization(eng,pa,x0,x1,x2,x3,x4,key, new_ancilla_x0, new_ancilla_x1, new_ancilla_x2, new_ancilla_x3, new_ancilla_x4):

    for i in range(32):
        CNOT | (key[i+128] , x1[i+32])
        CNOT | (key[i + 96], x1[i])
        CNOT | (key[i + 64], x2[i + 32])
        CNOT | (key[i + 32], x2[i])
        CNOT | (key[i ], x3[i+32])

    if (resource_check != 1):
        print_state(eng, x0, 16)
        print_state(eng, x1, 16)
        print_state(eng, x2, 16)
        print_state(eng, x3, 16)
        print_state(eng, x4, 16)


    Permutation_a(eng, pa, x0, x1, x2, x3, x4, new_ancilla_x0, new_ancilla_x1, new_ancilla_x2, new_ancilla_x3, new_ancilla_x4)

    for i in range(64):
        CNOT | (key[i + 64], x3[i])
        CNOT | (key[i], x4[i])



def main(eng):
    pa = 12
    pb = 6
    A_len = 64
    pt_len = 64

    # S => IV || K || nonce   320 bits
    IV = eng.allocate_qureg(32)    # fixed
    K = eng.allocate_qureg(160)
    Nonce = eng.allocate_qureg(128)   # the fixed nonce
    key = eng.allocate_qureg(160)
    A = eng.allocate_qureg(32)
    pt = eng.allocate_qureg(32)
    ct = eng.allocate_qureg(32)

    new_ancilla_x0 = eng.allocate_qureg(64)
    new_ancilla_x1 = eng.allocate_qureg(64)
    new_ancilla_x2 = eng.allocate_qureg(64)
    new_ancilla_x3 = eng.allocate_qureg(64)
    new_ancilla_x4 = eng.allocate_qureg(64)

    # Key = 000102030405060708090A0B0C0D0E0F10111213
    # Nonce = 000102030405060708090A0B0C0D0E0F
    # PT = 00010203
    # AD = 00010203
    # CT = 8987022AF6E736CB84B8E988085B09B9F6B08E6B

    if(resource_check!=1):
        Round_constant_XOR(eng,IV,0xa0400c06,32)
        Round_constant_XOR(eng,K,0x000102030405060708090A0B0C0D0E0F10111213,160)
        Round_constant_XOR(eng,key,0x000102030405060708090A0B0C0D0E0F10111213,160)
        Round_constant_XOR(eng,Nonce, 0x000102030405060708090a0b0c0d0e0f,128)
        Round_constant_XOR(eng,A,0x00010203,32)
        Round_constant_XOR(eng,pt,0x00010203,32)

    S =[]
    for i in range(128):
        S.append(Nonce[i])
    for i in range(160):
        S.append(K[i])
    for i in range(32):
        S.append(IV[i])

    for i in range(64):
        X | new_ancilla_x0[i]
        X | new_ancilla_x1[i]
        X | new_ancilla_x2[i]
        X | new_ancilla_x3[i]
        X | new_ancilla_x4[i]

    Initialization(eng,pa,S[256:320],S[192:256],S[128:192],S[64:128],S[0:64],key, new_ancilla_x0, new_ancilla_x1, new_ancilla_x2, new_ancilla_x3, new_ancilla_x4)   # end
    Associated(eng,pb,A,A_len,S[256:320],S[192:256],S[128:192],S[64:128],S[0:64], new_ancilla_x0, new_ancilla_x1, new_ancilla_x2, new_ancilla_x3, new_ancilla_x4)

    # if(A_len):
    # Associated(eng,pb,A,A_len,S[256:320],S[192:256],S[128:192],S[64:128],S[0:64])

    Plain(eng,pb,pt,pt_len,ct,S[256:320],S[192:256],S[128:192],S[64:128],S[0:64])


    Finalization(eng,pa,S[256:320],S[192:256],S[128:192],S[64:128],S[0:64],key, new_ancilla_x0, new_ancilla_x1, new_ancilla_x2, new_ancilla_x3, new_ancilla_x4)

    c = []
    for i in range(64):
        c.append(S[i])

    for i in range(64):
        c.append(S[i+64])

    for i in range(32):
        c.append(ct[i])

    if(resource_check != 1):
        print_state(eng, c, 40)

global resource_check
global AND_check
global count
count =0
# print('Generate Ciphertext…')
# Simulate = ClassicalSimulator()
# eng = MainEngine(Simulate)
# resource_check = 0
# main(eng)

print('Estimate cost…')
Resource = ResourceCounter()
eng = MainEngine(Resource)
resource_check = 1
AND_check = 0
main(eng)
print(Resource)
print(count)
print('\n')
eng.flush()