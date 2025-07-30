import sys

sys.path.append("../src")

import redflagbpm

bpm = redflagbpm.BPMService()

if __name__ == '__main__':
    x = bpm.exec("holaMundo", "vertx", {})
    print(x)
