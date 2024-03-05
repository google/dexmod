# dexmod

dexmod is a tool written in python to exemplify patching Dalvik bytecode in a DEX (Dalvik Executable) file, and assist in the static analysis of Android applications.

Malicious applications can have obfuscation schemes that are repeatedly used throughout the code (for example, for the purpose of encoding strings). There are numerous existing approaches to overcome this, bytecode patching is another proposed solution since in certain cases it is easier to identify such schemes through bytecode. While the source code may use randomized variable names or dead code to hinder analysis, the underlying obfuscation logic in the bytecode will remain the same, making it easier to identify and patch.

dexmod allows researchers to
* Find methods in the application based on bytecode patterns
* Add new strings to the application
* Patch methods with custom bytecode

## Download and Usage

Download the dexmod code, and modify the `editBytecode.py` skeleton code to include custom bytecode patching logic based on analyzed samples.

Run the following command, where `DEX_FILE_NAME` is the name of the DEX file to be patched
```
python dexmod.py [DEX_FILE_NAME]
```

The tool will generate a patched DEX file with the name `copy_[DEX_FILE_NAME]`.

## Example

To use or expand this tool, it is best to first view a working example where dexmod was used to patch a malicious application's code:
* Download the DEX file matching the hashes under `example/sample` (Please note this is a malicious sample, download it in a safe analysis environment)
* Rename the file to `classes.dex`
* Copy the contents of `example/editBytecodeCustom.py` into `editBytecode.py`
* Run the command `python dexmod.py classes.dex`
* A patched `copy_classes.dex` will be generated

## Further Information

We recommend reviewing the Mandiant [Delving into Dalvik: A Look into DEX Files](https://www.mandiant.com/resources/blog/dalvik-look-into-dex-files) blog for more detailed information about the DEX file format, method structure in bytecode, and usage of this tool.

## Disclaimer

This is not an officially supported Google product.
