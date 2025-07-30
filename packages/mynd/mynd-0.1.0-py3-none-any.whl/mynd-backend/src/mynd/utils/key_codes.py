"""Module for ASCII key codes."""

from enum import IntEnum


class KeyCode(IntEnum):
    """Class representing ASCII key codes."""

    NULL = 0  # NUL
    BACKSPACE = 8  # BS
    HORIZONTAL_TAB = 9  # HT

    ESC = 27  # ESC
    SPACE = 32  #
    EXCLAMATION = 33  # !
    QUOTE = 34  # "
    NUMBER = 35  # #
    DOLLAR = 36  # $
    PERCENT = 37  # %
    AMPERSAND = 38  # &
    APOSTROPHE = 39  # '
    LEFT_PARANTHESIS = 40  # (
    RIGHT_PARANTHESIS = 41  # )
    ASTERISK = 42  # *
    PLUS = 43  # +
    COMMA = 44  # ,
    HYPHEN = 45  # -
    PERIOD = 46  # .
    SLASH = 47  # /
    D0 = 48  # 0
    D1 = 49  # 1
    D2 = 50  # 2
    D3 = 51  # 3
    D4 = 52  # 4
    D5 = 53  # 5
    D6 = 54  # 6
    D7 = 55  # 7
    D8 = 56  # 8
    D9 = 57  # 9
    COLON = 58  # :
    SEMICOLON = 59  # ;
    LESS_THAN = 60  # <
    EQUAL = 61  # =
    GREATER_THAN = 62  # >
    QUESTION_MARK = 63  # ?
    AT = 64  # @

    UPPERCASE_A = 65
    UPPERCASE_B = 66
    UPPERCASE_C = 67
    UPPERCASE_D = 68
    UPPERCASE_E = 69
    UPPERCASE_F = 70
    UPPERCASE_G = 71
    UPPERCASE_H = 72
    UPPERCASE_I = 73
    UPPERCASE_J = 74
    UPPERCASE_K = 75
    UPPERCASE_L = 76
    UPPERCASE_M = 77
    UPPERCASE_N = 78
    UPPERCASE_O = 79
    UPPERCASE_P = 80
    UPPERCASE_Q = 81
    UPPERCASE_R = 82
    UPPERCASE_S = 83
    UPPERCASE_T = 84
    UPPERCASE_U = 85
    UPPERCASE_V = 86
    UPPERCASE_W = 87
    UPPERCASE_X = 88
    UPPERCASE_Y = 89
    UPPERCASE_Z = 90

    LEFT_BRACKET = 91  # [
    BACKSLASH = 92  # \
    RIGHT_BRACKET = 93  # ]
    HAT = 94  # ^
    UNDERSCORE = 95  # _
    GRAVE_ACCENT = 96  # `

    LEFT_BRACE = 123  # {
    VERTICAL_BAR = 124  # |
    RIGHT_BRACE = 125  # }
    TILDE = 126  # ~
    DEL = 127  # DEL

    LOWERCASE_A = 97
    LOWERCASE_B = 98
    LOWERCASE_C = 99
    LOWERCASE_D = 100
    LOWERCASE_E = 101
    LOWERCASE_F = 102
    LOWERCASE_G = 103
    LOWERCASE_H = 104
    LOWERCASE_I = 105
    LOWERCASE_J = 106
    LOWERCASE_K = 107
    LOWERCASE_L = 108
    LOWERCASE_M = 109
    LOWERCASE_N = 110
    LOWERCASE_O = 111
    LOWERCASE_P = 112
    LOWERCASE_Q = 113
    LOWERCASE_R = 114
    LOWERCASE_S = 115
    LOWERCASE_T = 116
    LOWERCASE_U = 117
    LOWERCASE_V = 118
    LOWERCASE_W = 119
    LOWERCASE_X = 120
    LOWERCASE_Y = 121
    LOWERCASE_Z = 122
