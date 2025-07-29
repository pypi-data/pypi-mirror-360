import os, json
from ..templates.cmdTemplate import \
    mainFile, logPrintTemplate, \
    commandsFileStr, commandsJsonDict, \
    cmdSwitchbordFileStr, cmdOptSwitchbordFileStr, \
    argParseTemplate, optSwitchesTemplate, \
    newCmdStr, modCmdStr, rmCmdStr, \
    newCmdTemplateStr, argDefTemplateStr

def writeCLIPackage(fields: dict):
    print()
    field_name = "name"
    programName = fields[field_name]
    # -- package dir files
    ## write __init__.py to package dir from str
    packDir = os.path.join(os.path.abspath("."), 'src', programName)
    #print('packDir:', str(packDir))
    chkDir(packDir)
    fileName = os.path.join(packDir,"main.py")
    with open(fileName,"w") as wf:
        wf.write(mainFile)

    # -- defs dir files
    ## write logPrint.py def for def dir from template
    dirName = os.path.join(packDir,"defs")
    fileName = os.path.join(dirName,"logIt.py")
    fileStr = logPrintTemplate.substitute(name=programName)
    chkDir(dirName)
    with open(fileName,"w") as wf:
        wf.write(fileStr)

    # -- classes dir files
    #write argPars.py to class directory from template
    field_name = "description"
    description = fields[field_name]
    dirName = os.path.join(packDir,"classes")
    fileName = os.path.join(dirName,"argParse.py")
    fileStr = argParseTemplate.substitute(description=description)
    chkDir(dirName)
    with open(fileName,"w") as wf:
        wf.write(fileStr)
    ## write optSwitches.py to clsass dir from template
    fileName = os.path.join(dirName,"optSwitches.py")
    fileStr = optSwitchesTemplate.substitute(name=programName)
    with open(fileName,"w") as wf:
        wf.write(fileStr)

    # -- commands dir files
    ## write commands.py Commands class file
    dirName = os.path.join(packDir,"commands")
    fileName = os.path.join(dirName,"commands.py")
    chkDir(dirName)
    with open(fileName,"w") as wf:
        wf.write(commandsFileStr)
    # write commands.json to commands dir from dict
    fileName = os.path.join(dirName,"commands.json")
    with open(fileName,"w") as wf:
        cmdJson = json.dumps(commandsJsonDict,indent=2)
        wf.write(cmdJson)
    ## write cmdSwitchbord.py to def dir from str
    fileName = os.path.join(dirName,"cmdSwitchbord.py")
    with open(fileName,"w") as wf:
        wf.write(cmdSwitchbordFileStr)
    ## write cmdOptSwitchbord.py to def dir from str
    fileName = os.path.join(dirName,"cmdOptSwitchbord.py")
    with open(fileName,"w") as wf:
        wf.write(cmdOptSwitchbordFileStr)
    ## write newCmd.py to commands dir from str
    fileName = os.path.join(dirName,"newCmd.py")
    with open(fileName,"w") as wf:
        wf.write(newCmdStr)
    ## write rmCmd.py to commands dir from str
    fileName = os.path.join(dirName,"modCmd.py")
    with open(fileName,"w") as wf:
        wf.write(modCmdStr)
    ## write rmCmd.py to commands dir from str
    fileName = os.path.join(dirName,"rmCmd.py")
    with open(fileName,"w") as wf:
        wf.write(rmCmdStr)

    # -- commands\templates dir files
    ## write newCmd.py template file
    dirName = os.path.join(dirName, "templates")
    fileName = os.path.join(dirName,"newCmd.py")
    chkDir(dirName)

    fileStr = "from string import Template\n"
    fileStr += "from textwrap import dedent\n\n"
    fileStr += f'cmdDefTemplate = Template(dedent("""{newCmdTemplateStr}\n"""))\n\n'
    fileStr += f'argDefTemplate = Template(dedent("""{argDefTemplateStr}\n"""))'
    with open(fileName,"w") as wf:
        wf.write(fileStr)

def chkDir(dirName: str):
    if not os.path.isdir(dirName):
        os.makedirs(dirName, exist_ok=True)


