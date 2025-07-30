import sys
sys.path.append("../src")

import redflagbpm

bpm=redflagbpm.BPMService()

def holaMundo(msg):
    print(msg)
    bpm.reply("Hola Mundo!")

#bpm.register_handler("TEST/helloWorld.py",holaMundo)

if __name__ == '__main__':
    bpm.register_handler("holaMundo",holaMundo)
    bpm.start()

