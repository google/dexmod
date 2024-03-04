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

import struct
from ctypes import cast
from ctypes import POINTER, c_char_p, c_uint32

class methodInfo:
  def __init__(self, methodIdx, offset, name, bytecode):
    self.methodIdx = methodIdx
    self.offset = offset
    self.name = name
    self.bytecode = bytecode

class methods:
  """
  " Maps a method_idx to the method's name, offset and bytecode
  """
  def __init__(self, dex):
    self.dex = dex

  def getMethodObjects(self):
    """
    " Returns objects for all the methods in the DEX file
    " Each object contains the method's method_idx, file offset, name and bytecode
    """
    idxOffsetsMapping = self.getIdxOffsetsMapping()
    bytecodeOffsetsMapping = self.getBytecodeOffsetsMapping()
    strings = self.getStringsData()
    namesIdxMapping = self.getNamesIdxMapping(strings)
    methodInfoObjects = self.getMethodInformation(idxOffsetsMapping, bytecodeOffsetsMapping, namesIdxMapping)
    return methodInfoObjects

  def getIdxOffsetsMapping(self):
    """
    " Gets the direct and virtual methods for each class in the DEX
    """
    idxOffsetsMapping = {}

    classData = self.dex.contents().class_data
    classDataSize = self.dex.contents().meta.class_data_size
    for i in range(classDataSize):
      idxOffsetsMapping.update(self.getClassMethods(classData[i].contents))

    return idxOffsetsMapping

  def getClassMethods(self, classDataItem):
    """
    " Gets the offset to idx mapping for the direct and 
    " virtual methods of a class using getClassMethodsHelper
    """
    idxOffsetsMapping = {}

    idxOffsetsMapping.update(self.getClassMethodsHelper(classDataItem.direct_methods, classDataItem.direct_methods_size.__int__()))
    idxOffsetsMapping.update(self.getClassMethodsHelper(classDataItem.virtual_methods, classDataItem.virtual_methods_size.__int__()))

    return idxOffsetsMapping


  def getClassMethodsHelper(self, methods, methodsSize):
    """
    " Maps the file offsets of a class direct and virtual methods to their method_idx
    """
    idxOffsetsMapping = {}
    methodIdsStart = self.calculateMethodIdsStart()

    for i in range(methodsSize):
      methodContent = methods[i].contents
      if i == 0:
        methodIdx = methodContent.method_idx_diff.__int__()
      else:
        methodIdx += methodContent.method_idx_diff.__int__()
      codeOffset = methodContent.code_off.__int__()
      if codeOffset != 0:      
        idxOffsetsMapping[codeOffset] = methodIdsStart + methodIdx*8

    return idxOffsetsMapping

  def calculateMethodIdsStart(self):
    """
    " Calculates the start of the method_ids section in the DEX file
    """
    header = self.dex.header()
    methodIdsStart = header.header_size + header.string_ids_size*4 + header.type_ids_size*4 + header.proto_ids_size*12 + header.field_ids_size*8
    return methodIdsStart

  def getBytecodeOffsetsMapping(self):
    """
    " Maps a method's file offset to its bytecode
    """
    bcOffsetsMapping = {}

    codeList = self.dex.code_list()
    codeListSize = self.dex.meta().code_list_size
    for i in range(codeListSize):
      codeItem = codeList[i]
      codeOffset = codeItem.meta.offset
      bytecode = self.getBytecode(codeItem)
      bcOffsetsMapping[codeOffset] = bytecode

    return bcOffsetsMapping

  def getBytecode(self, codeItem):
    """
    " Reads a method's bytecode based on its insns_size
    """
    bytecode = b""
    insns = codeItem.insns
    insnsSize = codeItem.insns_size
    for k in range(insnsSize):
      bytecode += struct.pack("H", insns[k])
    return bytecode

  def getNamesIdxMapping(self, strings):
    """
    " Maps a method's name to its method_idx
    """
    namesIdxMapping = {}

    methodIds = self.dex.method_ids()
    methodIdsSize = self.dex.header().method_ids_size
    methodIdsStart = self.calculateMethodIdsStart()
    stringIdsStart = self.dex.header().string_ids_off

    for i in range(methodIdsSize):
      namesIdxMapping[methodIds[i].meta.offset] = strings[methodIds[i].name_idx]

    return namesIdxMapping

  def getStringsData(self):
    """
    " Gets the DEX file strings
    """
    strings = []

    stringDataList = self.dex.string_data_list()
    stringDataSize = self.dex.header().string_ids_size

    for i in range(stringDataSize):
      stringData = str(cast(stringDataList[i].data, c_char_p).value)
      strings.append(stringData[2:-1])

    return strings

  def getMethodInformation(self, idxOffsetsMapping, bytecodeOffsetsMapping, namesIdxMapping):
    """
    " Uses the mappings from previous methods to create a
    " method object that has the following information:
    " method idx, file offset, name and bytecode
    """
    methodInfoObjects = []
    methodIdsStart = self.calculateMethodIdsStart()
    for methodOffset in idxOffsetsMapping:
      methodIdx = idxOffsetsMapping[methodOffset]
      methodBytecode = bytecodeOffsetsMapping[methodOffset]
      methodName = namesIdxMapping[methodIdx]
      methodIdx = int((methodIdx - methodIdsStart) / 8)
      methodInfoObjects.append(methodInfo(methodIdx, methodOffset, methodName, methodBytecode))
    return methodInfoObjects
