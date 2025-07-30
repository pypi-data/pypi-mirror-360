from typing import List, Union

QUICK_TIMEOUT_S = 0.2
MID_TIMEOUT_S = 0.5
LONG_TIMEOUT_S = 1

class MacroController:
    a: str = 'A'
    b: str = 'B'
    x: str = 'X'
    y: str = 'Y'
    r: str = 'R'
    zr: str = 'ZR'
    l: str = 'L'
    zl: str = 'ZL'
    minus: str = 'MINUS'
    plus: str = 'PLUS'
    ls: str = 'L_STICK_PRESS'
    rs: str = 'R_STICK_PRESS'
    home: str = 'HOME'
    capture: str = 'CAPTURE'
    down: str = 'DPAD_DOWN'
    up: str = 'DPAD_UP'
    left: str = 'DPAD_LEFT'
    right: str = 'DPAD_RIGHT'
    empty: str = ''

    def controller_to_macro(self, macro_input: str) -> Union[str, None]:
        macro_dict = {
            'A': 'L',
            'B': 'K',
            'X': 'I',
            'Y': 'J',
            'R': '8',
            'ZR': '9',
            'ZL': '1',
            'L': '2',
            '-': '7',
            '+': '6',
            'L_STICK_PRESS': 'T',
            'R_STICK_PRESS': 'Y',
            'HOME': '[',
            'CAPTURE': ']',
            'DPAD_DOWN': 'B',
            'DPAD_UP': 'G',
            'DPAD_LEFT': 'V',
            'DPAD_RIGHT': 'N',
            'LEFT_STICK_UP': 'W',
            'LEFT_STICK_DOWN': 'S',
            'LEFT_STICK_LEFT': 'A',
            'LEFT_STICK_RIGHT': 'D',
            'RIGHT_STICK_UP': 'ArrowDown',
            'RIGHT_STICK_DOWN': 'ArrowUp',
            'RIGHT_STICK_LEFT': 'ArrowLeft',
            'RIGHT_STICK_RIGHT': 'ArrowRight'
        }
        return macro_dict.get(macro_input)

class Keyboard:
    """
    The Nintendo Switch default
    keyboard layout in Splatoon 3
    looks like this:

    [1,2,3,4,5,6,7,8,9,0,@]
    [q,w,e,r,t,y,u,i,o,p,=]
    [a,s,d,f,g,h,j,k,l,&,;]
    [z,x,c,v,b,n,m,*,#,!,?]

    There is some keys that aren't
    available:

    [@,i,o,=,&,;,z,*,#,!,?]

    Considering that, creating macros for
    NXBT will have some considerations

    First determine the row key, and then determine
    the row column
    """

    row1: List[str] = ["1","2","3","4","5","6","7","8","9","0","@"]
    row2: List[str] = ["q","w","e","r","t","y","u","i","o","p","="]
    row3: List[str] = ["a","s","d","f","g","h","j","k","l","&",";"]
    row4: List[str] = ["z","x","c","v","b","n","m","*","#","!","?"]
    non_typeable_keys: List[str] = ["@","i","o","=","&",";","z","*","#","!","?"]
    macro_controller: MacroController

    def __init__(self):
        self.macro_controller = MacroController()

    @property
    def rows(self) -> List[List[str]]:
        return [
            self.row1,
            self.row2,
            self.row3,
            self.row4
        ]

    def parse_key(self, key_input: str) -> Union[List[str], None]:
        controller = self.macro_controller
        key_macros = []
        row = None
        row_list = None
        col = None
        for i, check_row in enumerate(self.rows):
            if key_input in check_row:
                row = i
                row_list = check_row
                col = row_list.index(key_input)

        if not row and not col:
            return None

        # Moving into the key
        for _ in range(row):
            key_macros.append(controller.down)
        for _ in range(col):
            key_macros.append(controller.right)
        # Adding key
        key_macros.append(controller.a)
        # Going Back
        for _ in range(col):
            key_macros.append(controller.left)
        for _ in range(row):
            key_macros.append(controller.up)
        return key_macros

    def parse_code(self, replay_code: str) -> Union[List[List[str]], None]:
        macro_col = []
        _replay_code = replay_code.replace('-', '').lower()
        for k in _replay_code:
            macro_col.append(self.parse_key(k))
        return macro_col


def translate_code_to_macros(code: str) -> List[List[str]]:
    kb = Keyboard()
    macro_col = [
        [kb.macro_controller.controller_to_macro(c) for c in col] for col in kb.parse_code(code)
    ]
    return macro_col