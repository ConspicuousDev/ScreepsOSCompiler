import os
import re
import shutil
import sys

import easygui


def compileDirectory(inputDir, outputDir):
    fileMap = {}
    inputWalk = os.walk(inputDir)
    print("Generating file mappings...")
    for path, dirs, files in inputWalk:
        if path.split("\\")[-1].startswith("."):
            continue
        for file in files:
            pathDiff = path.replace(inputDir, "").replace("\\", "_")
            if len(pathDiff) > 0 and pathDiff[0] == "_":
                pathDiff = pathDiff[1:]
            mappedFile = f"{pathDiff}{'-' if len(pathDiff) > 0 else ''}{file}"
            if not os.path.exists(outputDir):
                os.mkdir(outputDir)
            shutil.copy(f"{path}\\{file}", f"{outputDir}\\{mappedFile}", )
            fileMap[mappedFile] = {
                "from": inputDir + "\\" + pathDiff.replace("_", "\\") + ("\\" if len(pathDiff) > 0 else "") + file,
                "to": outputDir + "\\" + mappedFile
            }
    print("File mappings generated.")
    print("Applying file mappings to compiled sources...")
    outputWalk = os.walk(outputDir)
    for path, dirs, files in outputWalk:
        for file in files:
            print(f"FILE: {file}")
            if not file.endswith(".js"):
                continue
            read = open(path + "\\" + file, "r")
            contents = read.read()
            read.close()
            for match in re.findall(r"require\(\"(.*)\"\)|from \"(.*)\"", contents):
                os.chdir(os.path.dirname(fileMap[file]["from"]))
                replaced = False
                if "/" in match:
                    replaced = True
                    match = match.replace("/", "\\")
                relative = os.path.realpath(match)
                if "." not in relative:
                    relative += ".js"
                filtered = list(filter(lambda fileName: fileMap[fileName]["from"] == relative, list(fileMap)))
                if len(filtered) == 0:
                    raise Exception(
                        f"COMPILATION ERROR: Refereced file '{relative}' not found on original files ('{fileMap[file]['from']}').")
                contents = contents.replace(match.replace("\\", "/") if replaced else match, "./" + list(filtered)[0])
                print(f"  MAPPING: {match} → .\\{list(filtered)[0]}")
            write = open(path + "\\" + file, "w")
            write.write(contents)
            write.close()
    print("File mappings applied.")
    print("SUCCESS! Compilation finished.")


def main():
    if len(sys.argv) < 2:
        inputDir = easygui.diropenbox("Select INPUT directory")
    else:
        inputDir = sys.argv[1].replace("/", "\\")
    if len(sys.argv) < 3:
        outputDir = easygui.diropenbox("Select OUTPUT directory")
    else:
        outputDir = sys.argv[2].replace("/", "\\")
    compileDirectory(inputDir, outputDir)


if __name__ == '__main__':
    main()
