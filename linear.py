import math

from projectq import MainEngine
from projectq.ops import H, CNOT, Measure, Toffoli, X, All, T, Tdag, S, Swap
from projectq.backends import CircuitDrawer, ResourceCounter, ClassicalSimulator
from projectq.meta import Loop, Compute, Uncompute, Control, Dagger
import random
def Round_constant_XOR(eng, k, rc, bit):
    for i in range(bit):
        if (rc >> i & 1):
            X | k[i]
    # print_state(eng,k,bit)
def LinearDiffusion_Layer(eng,x0,x1,x2,x3,x4):
    new_x0 = eng.allocate_qureg(64)
    new_x1 = eng.allocate_qureg(64)
    new_x2 = eng.allocate_qureg(64)
    new_x3 = eng.allocate_qureg(64)
    new_x4 = eng.allocate_qureg(64)

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

def main(eng):
    pa = 12
    pb = 6
    A_len = 64
    pt_len = 64

    # S => IV || K || nonce   320 bits
    IV = eng.allocate_qureg(64)  # fixed
    K = eng.allocate_qureg(128)
    Nonce = eng.allocate_qureg(128)  # the fixed nonce
    key = eng.allocate_qureg(128)
    # A = eng.allocate_qureg(32)
    # pt = eng.allocate_qureg(32)
    ct = eng.allocate_qureg(32)
    #
    # new_ancilla_x0 = eng.allocate_qureg(64)
    # new_ancilla_x1 = eng.allocate_qureg(64)
    # new_ancilla_x2 = eng.allocate_qureg(64)
    # new_ancilla_x3 = eng.allocate_qureg(64)
    # new_ancilla_x4 = eng.allocate_qureg(64)

    if (resource_check != 1):
        Round_constant_XOR(eng, IV, 0x80400c0600000000, 64)
        Round_constant_XOR(eng, K, 0x000102030405060708090a0b0c0d0e0f, 128)
        Round_constant_XOR(eng, key, 0x000102030405060708090a0b0c0d0e0f, 128)
        Round_constant_XOR(eng, Nonce, 0x000102030405060708090a0b0c0d0e0f, 128)
        # Round_constant_XOR(eng, A, 0x00010203, 32)
        # Round_constant_XOR(eng, pt, 0x00010203, 32)

    def main(eng):
        pa = 12
        pb = 6
        A_len = 64
        pt_len = 64

        # S => IV || K || nonce   320 bits
        IV = eng.allocate_qureg(64)  # fixed
        K = eng.allocate_qureg(128)
        Nonce = eng.allocate_qureg(128)  # the fixed nonce
        key = eng.allocate_qureg(128)
        A = eng.allocate_qureg(32)
        pt = eng.allocate_qureg(32)
        ct = eng.allocate_qureg(32)

        new_ancilla_x0 = eng.allocate_qureg(64)
        new_ancilla_x1 = eng.allocate_qureg(64)
        new_ancilla_x2 = eng.allocate_qureg(64)
        new_ancilla_x3 = eng.allocate_qureg(64)
        new_ancilla_x4 = eng.allocate_qureg(64)

        if (resource_check != 1):
            Round_constant_XOR(eng, IV, 0x80400c0600000000, 64)
            Round_constant_XOR(eng, K, 0x000102030405060708090a0b0c0d0e0f, 128)
            Round_constant_XOR(eng, key, 0x000102030405060708090a0b0c0d0e0f, 128)
            Round_constant_XOR(eng, Nonce, 0x000102030405060708090a0b0c0d0e0f, 128)
            Round_constant_XOR(eng, A, 0x00010203, 32)
            Round_constant_XOR(eng, pt, 0x00010203, 32)

        S = []
        for i in range(128):
            S.append(Nonce[i])
        for i in range(128):
            S.append(K[i])
        for i in range(64):
            S.append(IV[i])

        LinearDiffusion_Layer(eng, S[256:320], S[192:256], S[128:192], S[64:128], S[0:64])

    S = []
    for i in range(128):
        S.append(Nonce[i])
    for i in range(128):
        S.append(K[i])
    for i in range(64):
        S.append(IV[i])

    LinearDiffusion_Layer(eng, S[256:320],S[192:256],S[128:192],S[64:128],S[0:64])



print('Estimate cost…')
Resource = ResourceCounter()
eng = MainEngine(Resource)
resource_check = 1
AND_check = 0
main(eng)
print(Resource)
# print(count)
print('\n')
eng.flush()