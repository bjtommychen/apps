import os
import sys

func_in="FUNCTION_IN;"
func_exit="FUNCTION_EXIT;"
marker="MARKHERE;"

# func_in=""
# func_exit=""
# marker=""


def found_array(outlines):
    idx = len(outlines)
    bFoundArray = False
    bFoundKuoHao = False
    for index in range(idx-1, idx-3, -1):
        if outlines[index].find("typedef") != -1 or outlines[index].find("[") != -1 or outlines[index].find("]") != -1:
            bFoundArray = True
            break
        if outlines[index].find(")") != -1:
            bFoundKuoHao = True
    if bFoundKuoHao == False:
        return True
    return bFoundArray

def found_string_prev5lines(outlines, str):
    idx = len(outlines)
    bFoundArray = False
    for index in range(idx-1, idx-5, -1):
        if outlines[index].find(str) != -1:
            bFoundArray = True
            break
    return bFoundArray            

def process_lines(lines):
    outlines = []
    function_header = False 
    function_tail = False
    in_function = False
    
    for line in lines:
        stripline = line.strip()
        cmds = stripline.split()
        if line[0] == "{" :
            outlines.append(line)
            function_header = False
            function_tail = False
            in_function = False
            if found_array(outlines) == False:            
                function_header = True
                in_function = True
        elif line[0] == '}':
            if len(cmds) == 1 and len(cmds[0]) == 1 and in_function == True:
                num = 0
                idx = len(outlines)
                #back 5 lines to search for 'return'
                bFoundReturn = False
                for index in range(idx-1, idx-5, -1):
                    if outlines[index].find("return") != -1 and found_string_prev5lines(outlines, "else") == False:
                        outlines.insert( index, func_exit+'\n')
                        bFoundReturn = True
                        break
                if bFoundReturn == False and len(func_exit) > 0:
                    outlines.append(func_exit+'\n')
            outlines.append(line)
            function_tail = False
            function_header = False
            in_function = False
        elif line.find("}") != -1 and in_function == True:
            idx = line.find("}")
#             print line[idx]
            if len(cmds) > 1 or cmds[0] != "}":
                outlines.append(line)
#             elif found_array(outlines) or found_string_prev5lines(outlines, "switch") or found_string_prev5lines(outlines, "_asm") or found_string_prev5lines(outlines, "union"):
#                 outlines.append(line)
            else:
#                 outlines.append(line[0:idx] + marker + line[idx:] )
                outlines.append(marker+'\n')
                outlines.append(line)
        else:
            if len(cmds) > 1: 
                if (cmds[0].find("if(") != -1 or cmds[0].find("for(") != -1 or cmds[0].find("while(") != -1) and function_header:
                    function_header = False
                    outlines.append(func_in+'\n')
            if line.find("return") != -1:
                function_tail = True
            outlines.append(line)
    return outlines

if __name__ == '__main__':
    print 'start! read cmds from cmdlog.txt....\n'
#     print len(sys.argv)
    if len(sys.argv) < 2:
        exit(0)    
#     print sys.argv[1]
    if os.path.isfile(sys.argv[1]):
        f = open(sys.argv[1],"r")
        cmdlines = f.readlines()
        f.close()
#         print cmdlines
        writelines = process_lines(cmdlines)
#         f = open("temp.c", "w")
        f = open(sys.argv[1],"w")
        f.writelines(writelines)
        f.close()
    print 'done'        