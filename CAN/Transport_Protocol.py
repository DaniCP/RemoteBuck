'''
Created on 8 de jul. de 2016

@author: daniel.cano
@note: SAE J1939-21
'''
import sys, os
from bitstring import BitString, BitArray


class Transport_Protocol():
    def __init__(self, diagMng):
        self.CM = TP_Connection_Management(self)
        self.DT = TP_Data_Transfer(self)
        self.diag = diagMng

    def receive_data(self, src_add='0xEB', dest_add='0xFC'):
        canId = hex(self.diag._id_composer(_pgn=self.CM.PGN, dest_add=dest_add, src_add=src_add))
        print 'waiting to receive data from: ', canId
        rx = BitString(self.diag._wait_for_id(_id=canId))

        if self.CM._decode_rts(rx)[0] == self.CM.CONTROL_RTS:
            control_by, msg_size, num_pkts, pgn = self.CM._decode_rts(rx)
            self.CM.send_cts(pgn)   # tx CM.CTS
            total_msg = self.DT.wait_msg(src_add, dest_add, num_pkts)   # rx DT
#             print 'received DataTransfer msg: ', total_msg
            self.CM.send_EOAck(msg_size, num_pkts, pgn)     # tx CM.ACK

        return total_msg

    def receive_data_and_dont_send_ack(self, src_add='0xEB', dest_add='0xFC'):
        canId = hex(self.diag._id_composer(_pgn=self.CM.PGN, dest_add=dest_add, src_add=src_add))
        print 'waiting to receive data from: ', canId
        rx = BitString(self.diag._wait_for_id(_id=canId))

        if self.CM._decode_rts(rx)[0] == self.CM.CONTROL_RTS:
            control_by, msg_size, num_pkts, pgn = self.CM._decode_rts(rx)
            self.CM.send_cts(pgn)   # tx CM.CTS
            total_msg = self.DT.wait_msg(src_add, dest_add, num_pkts)   # rx DT
#             print 'received DataTransfer msg: ', total_msg
#             self.CM.send_EOAck(msg_size, num_pkts, pgn)     # tx CM.ACK
        return total_msg

    def decode_CM(self, msg):
        return self.CM.decode_tp_msg(msg)

    def wait_for_DT_msg(self, src_add='', dest_add='', num_pkts=0):
        self.DT.wait_msg(src_add, dest_add, num_pkts)


class TP_Connection_Management():
    CONTROL_RTS = 16
    CONTROL_CTS = 17
    CONTROL_END = 19
    CONTROL_ABORT = 255
    CONTROL_BAM = 32
    PGN = '0xEC'

    def __init__(self, tp):
        self.tp = tp

    def send_rts(self):
        pass

    def send_cts(self, pgn):
        by1 = self.CONTROL_CTS
        by2 = 255   # no limit
        by3 = 1     # next packet
        by4 = 255   # reserved
        by5 = 255   # reserved
        by6 = pgn[-8:].uint
        by7 = pgn[8:-8].uint
        by8 = pgn[:8].uint
        msg = (by1, by2, by3, by4, by5, by6, by7, by8)
        canId = self.tp.diag._id_composer(_pgn=self.PGN, dest_add='0xEB', src_add='0xFC')
        self.tp.diag.can_h.send_msg(msg, canId)

    def send_EOAck(self, size, num_pack, pgn):
        by1 = self.CONTROL_END
        by2 = size[-8:].uint
        by3 = size[:-8].uint
        by4 = num_pack.uint
        by5 = 255
        by6 = pgn[-8:].uint
        by7 = pgn[8:-8].uint
        by8 = pgn[:8].uint
        msg = (by1, by2, by3, by4, by5, by6, by7, by8)
        canId = self.tp.diag._id_composer(_pgn=self.PGN, dest_add='0xEB', src_add='0XFC')
        self.tp.diag.can_h.send_msg(msg, canId)

    def send_Abort(self):
        pass

    def send_BAM(self):
        pass

    def decode_tp_msg(self, msg):
        control_by = msg[:8].uint
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
        control_by = msg[:8].uint
        msg_size = msg[16:24] + msg[8:16]
        pckts = msg[24:32]
        pgn = msg[-8:] + msg[-16:-8] + msg[-24:-16]
        return control_by, msg_size, pckts, pgn

    def _decode_cts(self, msg):
        pass

    def _decode_end_ack(self, msg):
        pass

    def _decode_abort(self, msg):
        pass

    def _decode_bam(self, msg):
        pass


class TP_Data_Transfer():
    PGN = '0xEB'

    def __init__(self, tp):
        self.tp = tp

    def wait_msg(self, src_add='', dest_add='', num_pkts=2):
        total_msg = ''
        canId = hex(self.tp.diag._id_composer(_pgn=self.PGN, dest_add=dest_add, src_add=src_add))
        for i in range(0, num_pkts.uint):
            total_msg += (BitString(self.tp.diag._wait_for_id(_id=canId)))[8:]
        return total_msg
