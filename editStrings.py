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

from third_party.dexterity.dx.hash import update_checksum
from third_party.dexterity.dx.hash import update_signature

class editStrings:

  def __init__(self, dex, newDexPath):
    self.dex = dex
    self.newDexPath = newDexPath

  def addStrings(self, stringsToAdd):
    """
    " Add new strings to a DEX file
    " Return strings and their new offset, or existing offset if they are already present in the DEX
    " Monitors changes in the DEX file size to adjust offsets in subsequent sections accordingly
    """
    if type(stringsToAdd) != list:
      print("ERROR: method expects a list of strings")
      return

    sizeShift = 0
    stringsToAdd = list(set(stringsToAdd))
    stringsToAdd.sort()

    newStrings = {}
    existingStrings = {}

    allStrings = {}

    for string in stringsToAdd:
      strOffset = self.dex.add_string(string)
      if strOffset > 0:
        newStrings[string] = strOffset
        #4 added bytes for string_id item
        #2 added bytes for string length and terminating character in string_data item
        sizeShift += len(string) + 6
      else:
        existingStrings[string] = strOffset*-1

    allStrings.update(newStrings)
    allStrings.update(existingStrings)

    self.saveDex()

    return allStrings, sizeShift

  def saveDex(self):
    """
    " Save a new DEX file with the added strings
    " Update the method offsets to reflect the changes in the string sections
    """
    self.dex.save(bytes(self.newDexPath, "utf-8"))
    update_signature(self.newDexPath)
    update_checksum(self.newDexPath)
    return

