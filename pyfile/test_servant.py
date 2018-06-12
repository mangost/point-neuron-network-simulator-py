#! python
#! -*- coding:UTF8 -*-

# test_servant.py
# A demo for using class Servant on the remote servant machines

from servant import Servant

PORT = 12345        # the same as what the lab_neu has opened
HOST = "127.0.0.1"  # the hostname of the machine running lab_neu
ADDR = (HOST,PORT)

sm = Servant(ADDR)  # initialize the servant machine
# At this point,  make sure lab_gen has started 'lab_gen.start()'
sm.start()          # Start working

