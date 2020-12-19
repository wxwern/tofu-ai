#!/usr/bin/env python3

from engine import Responder
from positivity import Sentience
from bulkprocessing import *
from sys import argv
import time

if __name__ == "__main__":
    if len(argv) == 1:
        print('No arguments provided.')

    elif 'emulate' == argv[1] and len(argv) >= 3:
        messages = process_message_history(argv[2])
        for message in messages:
            time.sleep(0.25)
            if message[1] == 'BOT tofu':
                time.sleep(1)
                print('* ', end='')
            else:
                print('- ', end='')
            print(message[1], end=':\n')
            print(message[2])
            print()
            x = Responder.generate_response(message[2])
            if x is not None:
                time.sleep(1)
                print('* BOT tofu2 (emulated autoreply):\n' + x)
                print()
    elif argv[1] == 'reply' and len(argv) >= 3:
        reply = Responder.generate_response(argv[2])
        if reply is not None:
            print(reply)
    elif argv[1] == 'chat':
        try:
            while True:
                if len(argv) > 2:
                    s = argv[2]
                else:
                    s = input()
                reply = Responder.generate_response(s)
                if reply is not None:
                    print(reply)
                else:
                    print()
                if len(argv) > 2:
                    break
        except KeyboardInterrupt:
            pass
    elif argv[1] == 'jsonio':
        try:
            while True:
                if len(argv) > 2:
                    s = argv[2]
                else:
                    s = input()
                reply = Responder.get_info(s)
                if reply is not None:
                    print(reply)
                else:
                    print()
                if len(argv) > 2:
                    break
        except KeyboardInterrupt:
            pass

    else:
        print("Invalid arguments.")
