from enum import Enum, auto


class OPCODE(Enum):
    # Register commands
    PUSH_SP = auto()
    PUSH_BP = auto()
    PUSH_SL = auto()
    PUSH_PC = auto()
    SET_SP = auto()
    SET_BP = auto()
    SET_SL = auto()
    SET_PC = auto()

    # Control operators
    NOP = auto()
    PUSH = auto()
    DUP = auto()
    DROP = auto()
    SWAP = auto()
    OVER = auto()
    SLOAD = auto()
    SSTORE = auto()
    LOAD = auto()
    STORE = auto()
    CALL = auto()
    RET = auto()
    CALL_RET = auto()
    JMP = auto()
    JNZ = auto()
    JZ = auto()
    EXIT = auto()

    # Quantum operators
    PLAY = auto()
    CAPTURE = auto()
    CAPTURE_IQ = auto()
    CAPTURE_TRACE = auto()
    SET_TIME = auto()
    SET_PHASE = auto()
    SET_PHASE_EXT = auto()
    SET_BIAS = auto()
    ADD_TIME = auto()
    ADD_PHASE = auto()
    ADD_PHASE_EXT = auto()
    ADD_BIAS = auto()

    # Hardware control operators
    SET = auto()

    # Arithmetic operators
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    NEG = auto()
    EQ = auto()
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    BOR = auto()
    BAND = auto()
    BNOT = auto()
    XOR = auto()
    SHL = auto()
    SHR = auto()

    # Math operators
    ABS = auto()
    SQRT = auto()
    EXP = auto()
    SIN = auto()
    COS = auto()
    TAN = auto()
    ASIN = auto()
    ACOS = auto()
    ATAN = auto()
    ATAN2 = auto()
    LOG = auto()
    POW = auto()
    MIN = auto()
    MAX = auto()

    def __repr__(self):
        return self.name
