#!/usr/bin/env python3
#import jmspy
import jmspy



with jmspy.Jmspy("tcp://localhost:61616") as mq:
    pass
    mq.send_file("myQueue", "message1.txt")
    mq.receive_file("myQueue", save_dir=".")
