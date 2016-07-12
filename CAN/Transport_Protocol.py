'''
Created on 8 de jul. de 2016

@author: daniel.cano
@note: SAE J1939-21
'''
import sys, os
from bitstring import BitString, BitArray


class Transport_Protocol():
    CONTROL_RTS = 16
    CONTROL_CTS = 17
    CONTROL_END = 19
    CONTROL_ABORT = 255
    CONTROL_BAM = 32
    PGN = '0xEC'

    def __init__(self):
        pass

    def decode_tp_msg(self, msg):
        control_by = msg[0]
        if control_by == self.CONTROL_RTS:
            return self._decode_rts(msg)
        elif control_by == self.CONTROL_CTS:
            return self._decode_cts(msg)
        elif control_by == self.CONTROL_END:
            return self._decode_end_ack(msg)
        elif control_by == self.CONTROL_ABORT:
            return self._decode_abort(msg)
        elif control_by == self.CONTROL_BAM:
            return self._decode_bam(msg)

    def _decode_rts(self, msg):
        pass

    def _decode__cts(self, msg):
        pass

    def _decode_end_ack(self, msg):
        pass

    def _decode_abort(self, msg):
        pass

    def _decode_bam(self, msg):
        pass
