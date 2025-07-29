import argparse
from sdg_io import SdgIO
from sdg_utils import log_init, DEBUG
from . import Flasher

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ArgumentParser')
    parser.add_argument('--file', '-f',
                        action='store',
                        type=str, default="",
                        help=u"Файл прошивки в формате bin или hex")
    parser.add_argument('--port', '-p',
                        action='store',
                        type=str, default='COM1',
                        help=u"Порт. Например COM1")
    parser.add_argument('--port_cfg', '-c',
                        action='store',
                        type=str, default='500000_O_2',
                        help=u"115200_O_2 скорость_четность_стопбиты")
    parser.add_argument('--device', '-d',
                        action='store',
                        type=str, default='ve1t',
                        help=u"device stm32f1,stm32f4,ve91t,ve1t,avr16,avr8,ve4u,avrEE,rt1050")
    parser.add_argument('--opt', '-o',
                        action='store',
                        type=str, default='wv',
                        help="r/w/v for read/write/verification (default = wv)")
    parser.add_argument('--loglevel', '-l',
                        action='store',
                        type=int, default='2',
                        help=u"1-debug 2-info 3-warn 4-err")
    parser.add_argument('--addr', '-a',
                        action='store',
                        type=int, default='0',
                        help=u"адрес устройства 1-255 (default = 0 без адреса)")
    parser.add_argument('--reboot', '-r',
                        action='store',
                        type=int, default='-1',
                        help=u"код команды сброса 0-255 (default = -1 без команды)")
    options = vars(parser.parse_args())
    log = log_init(name='flasher', level=DEBUG)
    log.setLevel(log.getEffectiveLevel() * options['loglevel'])
    try:
        io = SdgIO(options['port'], options['port_cfg'])
    except IOError as e:
        log.error(f"Порт недоступен! {e}")
        input(">")
    else:
        addr = None if options['addr'] == 0 else bytes([options['addr'] & 0xff])
        rebootcmd = None if options['reboot'] == -1 else bytes([options['reboot'] & 0xff])
        Flasher(io,
                options['file'],
                options['device'],
                options['opt'],
                addr, rebootcmd, log).do()
