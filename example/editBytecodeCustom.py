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
    self.newDexPath = "copy_" + oldDexPath
    self.patchDex()
    return

  def patchDex(self):
    """
    " Patches the DEX file by looking for obuscated methods,
    " decoding the obfuscated strings they contain, adding
    " them to the DEX file and overwriting the methods
    """
    obfMethods, refMethods = self.searchDex()
    decodedStrings = self.decodeStrings(obfMethods)
    stringIds, sizeShift = editStrings(self.dex, self.newDexPath).addStrings(decodedStrings)
    for method in obfMethods:
      method.offset += sizeShift
    for method in refMethods:
      method.offset += sizeShift
    self.overwriteMethods(refMethods, decodedStrings, stringIds)
    return

  def findMethods(self, bytecodePattern):
    """
    " Returns method objects that contain a given bytecode pattern
    """
    foundMethods = searchBytecode().lookupPattern(self.methodObjects, bytecodePattern)
    return foundMethods

  def searchDex(self):
    """
    " Searches the DEX file using bytecode patterns
    " Returns obfuscated methods and methods referring them
    """
    refMethods = []
    refPattern = b"\x71\x00%b\x00\x00\x0c\x00\x11\x00"
    obfPattern = b"\xdf\x04\x04\x01\xb0\x4b\xb4\x11\xb0\x1b\x97\x01\x0b\x08\x8d\x11\x4f\x01\x05\x07"

    # Find obfuscated methods
    obfMethods = self.findMethods(obfPattern)
    # Find parent methods calling the obfuscated methods
    for method in obfMethods:
      methodIdx = struct.pack("H", method.methodIdx)
      obfReference = refPattern % methodIdx
      refMethod = self.findMethods(obfReference)
      refMethods += refMethod

    return obfMethods, refMethods

  def decodeStrings(self, obfMethods):
    """
    " Find encoded strings and XOR key in obfuscated methods
    " Decode using helper method xorString
    """
    decodedStrings = []

    arrayPattern = rb"\x03\x01\x00.+$"
    for method in obfMethods:
      encodedStringKey = re.findall(arrayPattern, method.bytecode, re.DOTALL)[0]
      decodedStrings.append(self.xorString(encodedStringKey))

    return decodedStrings
  
  def xorString(self, encodedStringKey):
    """
    " Extract encoded string and XOR key
    " Return the decoded string
    """
    decodedString = b""

    stringKey = encodedStringKey.split(b"\x03\x01\x00")

    xorKey = list(stringKey[2][1:].replace(b"\x00",b""))
    encodedString = list(stringKey[1][1:].replace(b"\x00",b""))

    lenKey = len(xorKey)
    lenString = len(encodedString)

    for i in range(lenString):
      decodedString += (encodedString[i] ^ xorKey[i % lenKey]).to_bytes()

    return decodedString

  def overwriteMethods(self, refMethods, decodedStrings, stringIds):
    """
    " Patch methods to return decoded strings
    " Update DEX checksum and signature
    """
    patchedPreface = b"\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00"
    patchedBytecode = b"\x1a\x00%b\x11\x00"

    f = open(self.newDexPath, "rb+")
    refLen = len(refMethods)
    for i in range(refLen):
      callingMethod = refMethods[i]
      decodedStringId = struct.pack("H", stringIds.get(decodedStrings[i]))
      returnStringBytecode = patchedBytecode % decodedStringId
      f.seek(callingMethod.offset)
      f.write(patchedPreface + returnStringBytecode)

    f.close()
    update_signature(self.newDexPath)
    update_checksum(self.newDexPath)
