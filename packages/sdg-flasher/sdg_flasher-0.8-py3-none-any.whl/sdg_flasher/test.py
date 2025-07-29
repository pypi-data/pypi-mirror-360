
from sdg_io import SdgIO
from sdg_utils import log_init, DEBUG, INFO, WARNING
from __init__ import Flasher

F210 = 'j:/Project/2B17M1BR/2b17m1br_210/bin/2B17M1BR_12_210_v24_01.bin'
F220 = 'j:/Project/2B17M1BR/2b17m1br_220/bin/2B17M1BR_12_220_v24_01.bin'

if __name__ == '__main__':
    mylog = log_init(level=INFO)
    myio = SdgIO('COM11', '500000_O_2', log=mylog.getChild("io").setLevel(WARNING))

    ve7prog = Flasher(myio, F210, 've7', opt='wv', addr=b'\x01', reboot=b'\x03', log=mylog)
    ve7prog.do()
    ve7prog = Flasher(myio, F220, 've7', opt='wv', addr=b'\x11', reboot=b'\x03', log=mylog)
    ve7prog.do()
    ve7prog = Flasher(myio, F220, 've7', opt='wv', addr=b'\x12', reboot=b'\x03', log=mylog)
    ve7prog.do()
    exit()