import numpy as np
import sys

def make_t ():
    np.set_printoptions(threshold=sys.maxsize)
    DOT_TEST_SIZES = [16, 32, 64, 128, 256, 512, 1024]
    NORM_TEST_SIZES = [16, 32, 64, 128, 256, 512, 1024]
    MATVEC_TEST_SIZES = [(4,4), (4,8), (8, 8), (8, 16), (16,16), (16,32),\
                         (32, 32), (32,64), (64, 64), (64,128), (128,128),\
                         (128,256), (256,256)]
    MATMAT_TEST_SIZES = [(4,4,4), (8,8,8), (16,16,16), (32,32,32),\
                         (64,64,64), (128,128,128), (256,256,256), (512,512,512)]
    # [(4,4,4), (4,4,8), (4,8,8), (8,8,8), (8,8,16),\
    # (8,16,16), (16,16,16), (16,16,32), (16,32,32),\
    # (32,32,32), (32,32,64), (32,64,64), (64,64,64),\
    # (64,64,128), (64,128,64),(128,128)]
    d_min = -1000
    d_max = 1000

    # alg1
    print(len(DOT_TEST_SIZES))
    for s in DOT_TEST_SIZES:
        a = np.random.default_rng().uniform(d_min,d_max,s)
        b = np.random.default_rng().uniform(d_min,d_max,s)
        dot = np.dot(a, b)
        print(s)
        print(' '.join(map(str, a)))
        print(' '.join(map(str, b)))
        print(dot)

    # alg2
    print(len(NORM_TEST_SIZES))
    for s in NORM_TEST_SIZES:
        a = np.random.default_rng().uniform(d_min,d_max,s)
        norm = np.linalg.norm(a, 2)
        print(s)
        print(' '.join(map(str, a)))
        print(norm)

    # alg3
    print(len(MATVEC_TEST_SIZES))
    for s in MATVEC_TEST_SIZES:
        M = np.random.default_rng().uniform(d_min,d_max,s)
        V = np.random.default_rng().uniform(d_min,d_max,s[1])
        dot = np.dot(M, V)
        print(' '.join(map(str,s)))
        for line in M:
            print(' '.join(map(str, line)))
        print(' '.join(map(str, V)))
        print(' '.join(map(str, dot)))

    # alg4
    print(len(MATMAT_TEST_SIZES))
    for s in MATMAT_TEST_SIZES:
        M = np.random.default_rng().uniform(d_min,d_max,s[0:2])
        V = np.random.default_rng().uniform(d_min,d_max,s[1:3])
        dot = np.matmul(M, V)
        print(' '.join(map(str,s)))
        for line in M:
            print(' '.join(map(str, line)))
        for line in V:
            print(' '.join(map(str, line)))
        for line in dot:
            print(' '.join(map(str, line)))

make_t()