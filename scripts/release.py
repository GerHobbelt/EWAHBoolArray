#!/usr/bin/env python3
########################################################################
# Generates a new release.
########################################################################
import sys
import re
import subprocess
import io
import os
import fileinput
if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, requires Python 3.x or better\n")
    sys.exit(1)

def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)

def extractnumbers(s):
    return tuple(map(int,re.findall(r"(\d+)\.(\d+)\.(\d+)",str(s))[0]))

def toversionstring(major, minor, rev):
    return str(major)+"."+str(minor)+"."+str(rev)

def topaddedversionstring(major, minor, rev):
    return str(major)+str(minor).zfill(3)+str(rev).zfill(3)
print("Calling git rev-parse --abbrev-ref HEAD")
pipe = subprocess.Popen(["git", "rev-parse", "--abbrev-ref", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
branchresult = pipe.communicate()[0].decode().strip()

if(branchresult != "master"):
    print(colored(255, 0, 0, "We recommend that you release on master, you are on '"+branchresult+"'"))

ret = subprocess.call(["git", "remote", "update"])

if(ret != 0):
    sys.exit(ret)
print("Calling git log HEAD.. --oneline")
pipe = subprocess.Popen(["git", "log", "HEAD..", "--oneline"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
uptodateresult = pipe.communicate()[0].decode().strip()

if(len(uptodateresult) != 0):
    print(uptodateresult)
    sys.exit(-1)

pipe = subprocess.Popen(["git", "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
maindir = pipe.communicate()[0].decode().strip()
scriptlocation = os.path.dirname(os.path.abspath(__file__))

print("repository: "+maindir)

pipe = subprocess.Popen(["git", "describe", "--abbrev=0", "--tags"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
versionresult = pipe.communicate()[0].decode().strip()

print("last version: "+versionresult )
try:
  currentv = extractnumbers(versionresult)
except:
  currentv = [0,0,0]
if(len(sys.argv) != 2):
    nextv = (currentv[0],currentv[1], currentv[2]+1)
    print ("please specify version number, e.g. "+toversionstring(*nextv))
    sys.exit(-1)
try:
    newversion = extractnumbers(sys.argv[1])
    print(newversion)
except:
    print("can't parse version number "+sys.argv[1])
    sys.exit(-1)

print("checking that new version is valid")
if(newversion[0] !=  currentv[0]):
    assert newversion[0] ==  currentv[0] + 1
    assert newversion[1] == 0
    assert newversion[2] == 0
elif (newversion[1] !=  currentv[1]):
    assert newversion[1] ==  currentv[1] + 1
    assert newversion[2] == 0
else :
    assert newversion[2] ==  currentv[2] + 1

atleastminor= (currentv[0] != newversion[0]) or (currentv[1] != newversion[1])


newmajorversionstring = str(newversion[0])
mewminorversionstring = str(newversion[1])
newrevversionstring = str(newversion[2])
newversionstring = str(newversion[0]) + "." + str(newversion[1]) + "." + str(newversion[2])
cmakefile = maindir + os.sep + "CMakeLists.txt"

for line in fileinput.input(cmakefile, inplace=True, backup='.bak'):
    line = re.sub(r'  VERSION \d+\.\d+\.\d+','  VERSION '+newmajorversionstring+'.'+mewminorversionstring+'.'+newrevversionstring, line.rstrip())
    print(line)

print("modified "+cmakefile+", a backup was made")


doxyfile = maindir + os.sep + "Doxyfile"
for line in fileinput.input(doxyfile, inplace=True, backup='.bak'):
    line = re.sub(r'PROJECT_NUMBER         = "\d+\.\d+\.\d+','PROJECT_NUMBER         = "'+newversionstring, line.rstrip())
    print(line)
print("modified "+doxyfile+", a backup was made")

print("running doxygen")
cp = subprocess.run(["doxygen"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=maindir)  # doesn't capture output

if(cp.returncode != 0):
    print("Failed to run doxygen")


readmefile = maindir + os.sep + "README.md"

print("Please run the tests before issuing a release. \n")
print("to issue release, enter \n git commit -a && git push  &&  git tag -a v"+toversionstring(*newversion)+" -m \"version "+toversionstring(*newversion)+"\" &&  git push --tags \n")



