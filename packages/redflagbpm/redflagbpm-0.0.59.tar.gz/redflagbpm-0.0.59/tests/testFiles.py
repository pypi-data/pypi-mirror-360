import sys
sys.path.append("../src")

import redflagbpm
from redflagbpm import ResourceService

bpm=redflagbpm.BPMService()

rs:ResourceService = bpm.resourceService

print(rs.accessPath("tmp/test.txt"))

print(rs.accessFile("tmp/test.txt"))

print(rs.accessTempPath("tmp/test.txt"))

print(rs.accessTempFile("tmp/test.txt"))