"""
Copyright 2024 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import re
import struct
from editStrings import *
from searchBytecode import *

class editBytecode:
  def __init__(self, dex, methodObjects, oldDexPath):
    self.dex = dex
    self.methodObjects = methodObjects
    self.oldDexPath = oldDexPath
    self.newDexPath = "copy_" + self.oldDexPath
    self.patchDex()
    return

  def patchDex(self):
    """
    " Example using helper methods to patch the DEX file
    """
    #methodsToPatch = self.findMethods(b"\xca\xfe\xba\xbe")
    #stringsToAdd = ["helloWorld"]
    #stringIds = self.addStrings(stringsToAdd)
    #fileOffset = methodsToPatch[0].offset
    #newBytecode = b"\xca\xfe%b\xde\xad" % struct.pack("H", stringIds.get(stringsToAdd[0]))
    #self.patchMethod(self.newDexPath, fileOffset, newBytecode)
    return

  def addStrings(self, stringsToAdd):
    """
    " Adds strings and saves a new DEX with the added strings
    " Updates the offsets of the methods according to the changes in the string section size
    " Returns the string IDs which can be referenced and used by methods
    """
    stringIds, sizeShift = editStrings(self.dex, self.newDexPath).addStrings(stringsToAdd)
    for methodObject in self.methodObjects:
      methodObject.offset += sizeShift
    return stringIds

  def findMethods(self, bytecodePattern):
    """
    " Returns method objects that contain a given bytecode pattern
    """
    foundMethods = searchBytecode().lookupPattern(self.methodObjects, bytecodePattern)
    return foundMethods

  def patchMethod(self, dexPath, fileOffset, newBytecode):
    """
    " Patches a method by overwriting existing bytecode in the DEX file with new bytecode
    """
    try:
      f = open(dexPath, "rb+")
    except:
      print("ERROR: File does not exist")
      return
    f.seek(fileOffset)
    f.write(newBytecode)
    f.close()
    update_signature(dexPath)
    update_checksum(dexPath)

  def bytecodeOperation_1(self):
    """
    " Implement your own logic for bytecode extraction or manipulation
    """
    return

  def bytecodeOperation_2(self):
    """
    " Implement your own logic for bytecode extraction or manipulation
    """
    return

  def bytecodeOperation_3(self):
    """
    " Implement your own logic for bytecode extraction or manipulation
    """
    return

