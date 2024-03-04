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

import sys

from editStrings import *
from editBytecode import *
from getMethodObjects import *
from searchBytecode import *

from third_party.dexterity.dx.dex import *

class dexmod:

  def __init__(self):
    if len(sys.argv) == 2:
      oldDexPath = sys.argv[1]
    else:
      print("ERROR: Script expects one argument.")
      return
    dex = Dex(bytes(oldDexPath, "utf-8"))
    methodObjects = methods(dex).getMethodObjects()
    editBytecode(dex, methodObjects, oldDexPath).patchDex()

dexmod()
