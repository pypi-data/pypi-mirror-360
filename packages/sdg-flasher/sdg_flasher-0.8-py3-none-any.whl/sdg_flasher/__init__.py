"""
Универсальный загрузчик ПО в микроконтроллеры:
avr8, 1887ve4u, avr16, 1986ve1t, 1986ve91t, stm32f4

Можно использовать из командной строки:
python -m sdg_flasher -p COM1 -c 500000_O_2 -d ve1t -a 85 -o w -f "ololo.hex"

Пример использования:
-------------
```python
from sdg_io import SdgIO
from sdg_flasher import Flasher

io = SdgIO('COM1', '115200_O_2')
Flasher(io, file='ololo.hex', device='ve1t, opt='wv', addr=b'\x01', rebootcmd='b'\x03').do()
```
"""

__version__ = '0.8'

import time
import sys
from struct import pack, unpack
from pathlib import Path
from intelhex import IntelHex
from sdg_dev import DevMaster, DevException
from sdg_utils import align, dump_bytes, bits2nums

stm32f4 = {
    'mtu': 1024,
    'sync': (b'\x71', b'stm4'),
    'flash': (  # Номер сектора начиная | Адрес | Размер в байтах
               # (0, 0x08000000, 16*1024), нулевой сектор занят бутлоадером
               (1, 0x08004000, 16 * 1024),
               (2, 0x08008000, 16 * 1024),
               (3, 0x0800C000, 16 * 1024),
               (4, 0x08010000, 64 * 1024),
               (5, 0x08020000, 128 * 1024),
               (6, 0x08040000, 128 * 1024),
               (7, 0x08060000, 128 * 1024),
               (8, 0x08080000, 128 * 1024),
               (9, 0x080A0000, 128 * 1024),
               (10, 0x080C0000, 128 * 1024),
               (11, 0x080E0000, 128 * 1024)),
    'cathex': True,  # Для stm32f4 hex файл содердит и бутлоадер и основную прошивку, бутлоадер
    # записан в 0-й сектор. Шить надо с 1го сектора (0x08004000) -> начало hex файла надо срезать.
}

stm32f1 = {  # 15 секторов - бутлоадер
    'mtu': 1024,
    'flash': [(i, 0x08000000 + i * 1024, 1024) for i in range(16, 128, 1)]
}

ve91t = {  # 0 сектор занят бутлоадером
    'mtu': 1024,
    'flash': [(i, 0x08000000 + i * 0x1000, 0x1000) for i in range(1, 32, 1)],
    'sync': (b'\x71', b've91t'),
}

ve1t = {  # ve1t - бутлоадер является частью программы
    'mtu': 1024,
    'flash': [(i, i * 0x1000, 0x1000) for i in range(32)],
    'sync': (b'\x71', b've1t'),
}

AVR8PAGESIZE = 64
AVR8BOOTPAGES = 1024 // AVR8PAGESIZE  # бутлоадер занимает 1кб в конце флешки
avr8 = {
    'flash': [(i, i * AVR8PAGESIZE, AVR8PAGESIZE) for i in range(8192 // AVR8PAGESIZE - AVR8BOOTPAGES)],
    'eeprom': (0, 0, 512)
}

ve4u = {
    'flash': [(i, i * AVR8PAGESIZE, AVR8PAGESIZE) for i in range(8192 // AVR8PAGESIZE - AVR8BOOTPAGES)],
    'skip_erase': True,
    'eeprom': (0, 0, 512)
}

AVR16PAGESIZE = 128
AVR16BOOTPAGES = 2048 // AVR16PAGESIZE  # бутлоадер занимает 2кб в конце флешки
avr16 = {
    'flash': [(i, i * AVR16PAGESIZE, AVR16PAGESIZE) for i in range(16384 // AVR16PAGESIZE - AVR16BOOTPAGES)],
    'eeprom': (0, 0, 512)
}

""" 1887ВЕ7Т: 64к по 256 байт (rww) + 64к по 64 байта (nrww); -загрузчик 4кб в конце (nrww) """
ve7 = {  # ve7
    'flash': [(n//256, n, 256) for n in range(0, 64*1024, 256)] +
             [(n//64 - 768, n, 64) for n in range(64*1024, 128*1024 - 4*1024, 64)],
    'skip_erase': True,
    'sync': (b'\x71', b'\x0B\x0E\x07'),
    'eeprom': [(n//256, n | 0x10000000, 256) for n in range(0, 8*1024, 256)],
}

avr128 = {  # mega128
    'flash': [(n//256, n, 256) for n in range(0, 128*1024 - 4*1024, 256)],
    'sync': (b'\x71', b'\x01\x02\x08'),
    'eeprom': [(n//256, n | 0x10000000, 256) for n in range(0, 8*1024, 256)],
}

rt1050 = {
    'mtu': 256,
    'flash': [(i, i * 0x1000, 0x1000) for i in range(1024)]
}

vk035 = {
    'mtu': 1024,
    'flash': [(i, i * 1024, 1024) for i in range(64)],
    'sync': (b'\x71', b'\x00\x03\x05'),
}

vk035ram = {
    'mtu': 1024,
    'flash': [(0, 0x20000800, 14 * 1024), ],
    'skip_erase': True,
    'sync': (b'\x71', b'\x00\x03\x06'),
}


class Flasher(DevMaster):
    """ Универсальный загрузчик ПО в микроконтроллеры:
    avr8, 1887ve4u, avr16, 1986ve1t, 1986ve91t, stm32f4 """
    def __init__(self,
                 io,
                 filename,
                 device='ve91t',
                 opt='r',
                 addr: bytes = None,
                 reboot: bytes = None,
                 log=None,
                 mtu: int = None,
                 notsync: bool = None,
                 ):
        """ Универсальный загрузчик ПО в микроконтроллеры
        :param io: интерфейс ввода/вывода, должен иметь методы read(timeout)/write,
            для приема/передачи сообщений. В случае ошибок генерировать IOError.
        :param filename: Файл прошивки в формате bin или hex
        :param device: avr8, ve4u, avr16, ve1t, ve91t, stm32f4
        :param opt: r/w/v/f/e for read/write/verification/fullerase/eeprom
        :param addr: Адрес устройсатва, например b'\x01', или None - без адреса.
        :param reboot: Команда сброса, например b'\x03' или None -без команды, с перебросом питания
        :param log: объект Logger, если не задать будет получен автоматом.
        :param mtu: переопределяет MTU, для поддержки старых устройств.
        :param notsync: без команды синхронизации, для поддержки старых устройств.
        """
        super().__init__(io, addr=addr, log=log)
        try:
            self.device = dict(stm32f4=stm32f4,
                               stm32f1=stm32f1,
                               ve91t=ve91t,
                               ve1t=ve1t,
                               avr8=avr8,
                               ve4u=ve4u,
                               avr16=avr16,
                               ve7=ve7,
                               avr128=avr128,
                               rt1050=rt1050,
                               vk035=vk035,
                               vk035ram=vk035ram,
                               )[device]
        except KeyError:
            self.log.error("device uncknown")
            sys.exit()
        self.opt = opt
        self.filename = filename
        self.rebootcmd = reboot
        self.wrbin = None
        self.timer = time.time()
        self.notsync = notsync
        if mtu:
            self.device['mtu'] = mtu


    def do(self):
        if 'flash' in self.device:
            for n, addr, size in self.device['flash']:
                self.log.debug(f"flash {n=}, {addr=:08x}, {size=}")
        if 'eeprom' in self.device:
            for n, addr, size in self.device['eeprom']:
                self.log.debug(f"eeprom {n=}, {addr=:08x}, {size=}")

        while True:
            if self.do_flash():
                self.log.info(u"Complite")
                try:
                    self.send_exit()
                except DevException:
                    pass
                return True
            else:
                self.log.info(u"Fail! repit? 'N' - no; AnyKey - yes")
                x = input(">")
                print("")
                if x == 'n' or x == 'N':
                    return False

    def file_open(self, filename):
        try:
            if Path(filename).suffix == '.bin':
                fd = open(filename, 'rb')
                data = fd.read()
                self.log.info(f"open bin file. len={len(data)}")
                fd.close()

            elif Path(filename).suffix == '.hex':
                ih = IntelHex(filename)
                device_start_addr = self.device['flash'][0][1]
                if 'cathex' in self.device:
                    self.log.info(f"Начало hex файла {ih.minaddr():08x} обрезано до {device_start_addr:08x}")
                    data = ih.tobinstr(start=device_start_addr)
                else:
                    if ih.minaddr() != device_start_addr:
                        self.log.warning(f"Начальный адрес в hex файле {ih.minaddr():08x}"
                                         f" не равен адресу device {device_start_addr:08x}")
                    data = ih.tobinstr()
                self.log.info(f"open hex file. len={len(data)}")

            elif filename:
                self.log.error(f"Некорректное раcширение файла. Нужен *.bin или *.hex")
                return None
            else:
                self.log.error(f"Некорректное имя файла <{filename}>")
                return None
        except FileNotFoundError as e:
            self.log.error(f"Невозможно открыть файл {e}")
            return None
        data = align(data, alignlen=4)
        return data

    def wait_connection(self):
        self.log.info("waiting connection")
        while 1:
            try:
                self.send_reboot()
                time.sleep(.025)  # avr min wdt time 15ms + 10ms start
            except DevException:
                pass
            for _ in range(5):
                try:
                    self.sync()
                except DevException:
                    time.sleep(.1)
                else:
                    self.log.info("Connected!")
                    return

    def sync(self):
        if not self.notsync and 'sync' in self.device:
            ack = self.send(self.device['sync'][0], ackfrmt='raw', timeout=0.1)
            if ack != self.device['sync'][1]:
                self.log.info(f"sync ack err {dump_bytes(ack)} {dump_bytes(self.device['sync'][0])}")
                raise DevException(f"uncknown ack {dump_bytes(ack)}")
        else:
            return self.send_read(self.device['flash'][0][1], 4, timeout=0.1)

    def do_flash(self):
        memory = 'eeprom' if 'e' in self.opt else 'flash'  # хренькакаято
        if 'w' in self.opt and 'r' in self.opt:
            self.log.error(f"error opt {self.opt}")

        if 'r' in self.opt and 'v' in self.opt:
            self.log.error(f"error opt {self.opt}")

        if 'w' in self.opt or 'v' in self.opt:
            self.wrbin = self.file_open(self.filename)
            if not self.wrbin:
                time.sleep(2)
                exit()

        self.wait_connection()
        if 'f' in self.opt:
            self.send_fullerase()

        if self.device == vk035:
            self.send_get_vk035cfg()

        if 'r' in self.opt:
            rdbin = self.read(memory, size=self.get_device_size(memory))
            fd = open(self.filename, 'wb')
            fd.write(rdbin)
            fd.close()
            return True

        if 'w' in self.opt:
            if memory == 'flash' and \
                    not self.device.get('skip_erase') and \
                    not self.erase(size=len(self.wrbin)):
                return False
            if not self.write(memory, data=self.wrbin):
                return False

        if 'v' in self.opt:
            if not self.wrbin:
                self.wrbin = self.file_open(self.filename)
            rdbin = self.read(memory, size=len(self.wrbin))
            rdbin = align(rdbin, alignlen=4)
            fd = open('tmp.bin', 'wb')
            fd.write(rdbin)
            fd.close()
            if self.wrbin == rdbin:
                self.log.info("Verification OK!")
                return True
            else:
                self.log.error("Verification FAIL!")
                return False
        else:
            return True

    def get_device_size(self, memory='flash'):
        size = 0
        for i in self.device[memory]:
            size += i[2]
        return size

    def get_sector_size(self, memory='flash', addr=0):
        """ если MTU не задан, размер пакета будет равен размеру страницы памяти"""
        for n, a, s in self.device[memory]:
            if a + s > addr:
                return s

    def read(self, memory='flash', addr=0, size=0):
        addr = addr or self.device[memory][0][1]
        self.log.info(f"rd {memory} {addr=:08x} {size=}")
        rdbin = b''
        while len(rdbin) < size:
            rdaddr = len(rdbin) + addr
            mtu = self.device['mtu'] if 'mtu' in self.device else self.get_sector_size(memory, rdaddr)
            msglen = mtu if size - len(rdbin) > mtu else size - len(rdbin)
            rdbin += self.send_read(rdaddr, msglen, timeout=2)
        self.log.info(f"rd {memory} ok ({time.time() - self.timer:.2f}sec)")
        return rdbin

    def write(self, memory='flash', addr=0, data=b''):
        addr = addr or self.device[memory][0][1]
        self.log.info(f"wr {memory} {addr=:08x} {len(data)=}")
        wrlen = 0
        while wrlen != len(data):
            wraddr = wrlen + addr
            mtu = self.device['mtu'] if 'mtu' in self.device else self.get_sector_size(memory, wraddr)
            msglen = mtu if len(data) - wrlen > mtu else len(data) - wrlen
            self.send_write(wraddr, data[wrlen:wrlen + msglen], timeout=3)
            wrlen += msglen
        self.log.info(f"wr {memory} ok ({time.time() - self.timer:.2f}sec)")
        return True

    def erase(self, memory='flash', size=0):
        self.log.info(f"erase {memory}")
        clrsize = 0
        for i in self.device['flash']:
            clrsize += i[2]
            self.log.debug(f"erase {i}")
            self.send_erase(i[0])
            if clrsize >= size:
                break
        self.log.info(f"erase {memory} ok ({time.time() - self.timer:.2f}sec)")
        return True

    def send_reboot(self):
        if self.rebootcmd:
            self.send(self.rebootcmd, remix=0, timeout=.1)

    # cmd = addr, 0x77, a0, a1, a2, a3, x, x,   ..data..    (2 or 1 + 6 byte + data)
    # ack = addr, 0xF7, a0, a1, a2, a3, x, x,               (2 or 1 + 6 byte )
    def send_write(self, addr, data, timeout):
        self.log.debug(f"send_write {addr:08x} {len(data)}")
        ackaddr, _ = self.send(b'w' + pack('I', addr) + b'\x00\x00' + data, ackfrmt='IH', timeout=timeout)
        if ackaddr != addr:
            raise DevException(f"Некорректный адрес данных в ответном сообщении {ackaddr} != {addr}")

    # cmd = addr, 0x72, a0, a1, a2, a3, s0, s1              (2 or 1 + 6 byte)
    # ack = addr, 0xF2, a0, a1, a2, a3, s0, s1, ..data..    (2 or 1 + 6 byte + data)
    def send_read(self, addr, size, timeout):
        self.log.debug(f"send_read {addr:08x} {size}")
        ack = self.send(b'r' + pack('IH', addr, size), ackfrmt='raw', timeout=timeout)
        ackaddr, = unpack('I', ack[0:4])
        if ackaddr != addr:
            raise DevException(f"Некорректный адрес данных в ответном сообщении {ackaddr} != {addr}")
        return ack[6:]

    #  cmd = addr + b'e'
    #  ack = addr + b'e'
    def send_exit(self):
        self.send(b'e', ackfrmt='', remix=0, timeout=0.05)

    # cmd = addr, 0x63, n0  |  addr, 0x63, n0, n1
    # ack = addr, 0xE3, n0  |  addr, 0xE3, n0, n1
    def send_erase(self, n):
        if len(self.device['flash']) > 255:  # костыль
            self.send(b'c' + pack('H', n), ackfrmt='H', remix=0, timeout=2)
        else:
            self.send(b'c' + pack('B', n & 0xff), ackfrmt='B', remix=0, timeout=2)

    # cmd = addr + 0x66
    # ack = addr + 0xE6
    def send_fullerase(self):
        self.send(b'f', ackfrmt='', remix=0, timeout=20)

    def send_get_vk035cfg(self):
        flags = {
            0: "JTAGEN",
            1: "DEBUGEN",
            2: "NVRWE",
            3: "FLASHWE",
            4: "BMODEDIS",
            6: "NVRRE",
            7: "FLASHRE",
        }
        ack = self.send(b'\x78', ackfrmt='B', remix=2, timeout=.1) & 0b11011111
        f = set(flags.get(f, '?') for f in bits2nums(ack))
        self.log.info(f"vk035cfg: 0x{ack:02x} {f}")
        return ack

    def send_set_cfg(self, flags):
        pass
