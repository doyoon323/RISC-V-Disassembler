import sys
import os

#disassemble code: PA1 in CA

#input -bin file / first command-line -> file name

#format (R,I,S,U ... ) 또는 명령어를 바로 인식한다. || C에서 ENUM 쓰면 좋을듯 
form = {
    '0110111': 'U',
    '0010111': 'U',
    '1101111': 'UJ',
    '1100111': 'I',
    '1100011': 'SB',
    '0000011': 'I',
    '0100011': 'S',
    '0010011': 'I',
    '0110011': 'R'
}

#lw -> 1 word , lh -> half word 이것도 처리할 것


insts = { #비효율적인것같기도  
    '0110111': {'': 'lui'},
    '0010111': {'': 'auipc'},
    '1101111': {'': 'jal'},
    '1100111': {'000': 'jalr'},
    '1100011': {'000': 'beq', '001': 'bne', '100': 'blt', '101': 'bge', '110': 'bltu', '111': 'bgeu'},
    '0000011': {'000': 'lb', '001': 'lh', '010': 'lw', '100': 'lbu', '101': 'lhu'},
    '0100011': {'000': 'sb', '001': 'sh', '010': 'sw'},
    '0010011': {'000': 'addi', '010': 'slti', '011': 'sltiu', '100': 'xori', '110': 'ori', '111': 'andi',
                '001': 'slli', '101': ['srai','srli']},  
    '0110011': {'000': ['add','sub'], '001': 'sll', 
                '010': 'slt', '011': 'sltu', '100': 'xor', '101': ['srl',  'sra'], '110': 'or', '111': 'and'}
}



def splits_field(code,f):
    
##    if f == 'R':
##        return {'funct7':code[:7] , 'rs2':code[7:12],'rs1':code[12:17],'funct3':code[17:20],'rd':code[20:25]}
##    elif f == "I":
##        return {'imm' : code[:12], 'rs1':code[12:17],'funct3':code[17:20],'rd':code[20:25]}
##    elif f == "S":
##        return {'imm[11:5]' :code[:7] , 'rs2':code[7:12],'rs1':code[12:17],'funct3':code[17:20],'imm[4:0]':code[20:25]}
##    elif f == "SB":
##        return {'imm[12][10:5]':code[:7] , 'rs2':code[7:12],'rs1':code[12:17],'funct3':code[17:20],'imm[4:1][11]':code[20:25]}
##    elif f == "U":
##        return {'imm[20][10:1]':code[:20],"imm[11][19:12]":code[20:25]}
##    elif f == "UJ":
##        return {'imm[31:12]' :code[:20] , 'rd':code[20:25]}
##    else:
##        print("ERROR : 존재하지 않는 format") 
##        

    if f == 'R':
        return [code[:7] , code[7:12],code[12:17], code[17:20],code[20:25]]
    elif f == "I":
        return [code[:12], code[12:17],code[17:20],code[20:25]]
    elif f == "S":
        return [code[:7] , code[7:12],code[12:17],code[17:20],code[20:25]]
    elif f == "SB":
        return [code[:7] , code[7:12],code[12:17],code[17:20],code[20:25]]
    elif f == "U":
        return [code[:20],code[20:25]]
    elif f == "UJ":
        return [code[:20] , code[20:25]]
    else:
        print("ERROR : 존재하지 않는 format") 
        

def disassembled(splits,opcode):
    f = form[opcode]
    funct3 = ""
    if f == 'R':
        funct7 = splits[0]
        rs2 = int(splits[1],2)
        rs1 = int(splits[2],2)
        funct3 = splits[3]
        rd = int(splits[4],2)

        if funct3 not in insts[opcode]:
            return -1
        else:
            inst = insts[opcode][funct3]
            
        if type(inst) == list and len(inst) > 1:
            if funct7 == "0000000":
                inst = inst[0]
            else:
                inst = inst[1]
        return f"{inst} x{rd}, x{rs1}, x{rs2}"
    elif f == "I":
        imm = splits[0]
        rs1 = int(splits[1],2)
        funct3 = splits[2]
        rd = int(splits[3],2)
        inst = insts[opcode][funct3]

        if funct3 not in insts[opcode]:
            return -1
        else:
            inst = insts[opcode][funct3]


        if funct3 in ["001","101"]:
            shamt = int(imm[7:],2)
            return f"{inst} x{rd}, x{rs1}, {shamt}"
        else:
            imm = sign_extension(imm)
            if imm[0] == '1':
                imm = -1 * int(imm,2)
            else:
                imm = int(imm,2)
        return f"{inst} x{rs1}, x{rd}, {imm}"
    elif f == "S":
        imm1 = splits[0]
        rs2 = int(splits[1],2)
        rs1 = int(splits[2],2)
        funct3 = splits[3]
        imm2 = splits[4]
        if funct3 not in insts[opcode]:
            return -1
        else:
            inst = insts[opcode][funct3]

        imm = sign_extension(imm1+imm2)
        if imm[0] == 1:
            imm = -1 * int(imm,2)
        else:
            imm = int(imm,2)
        return f"{inst} x{rs2}, {imm}(x{rs1})"
    elif f == "SB":
        imm1 = splits[0]
        rs2 = int(splits[1],2)
        rs1 = int(splits[2],2)
        funct3 = splits[3]
        if funct3 not in insts[opcode]:
            return -1
        else:
            inst = insts[opcode][funct3]
        imm2 = splits[4]
        imm = sign_extension(imm1[0] + imm2[4] + imm1[1:] + imm2[:4] )
        if imm[0] == 1:
            imm = -1 * int(imm,2)
        else:
            imm = int(imm,2)
        return f"{inst} x{rs1}, x{rs2}, {imm}"
    
    elif f == "U":
        imm = sign_extension(splits[0])
        if imm[0] == 1:
            imm = -1 * int(imm,2)
        else:
            imm = int(imm,2)
        rd = int(splits[1],2)
        
        if funct3 not in insts[opcode]:
            return -1
        else:
            inst = insts[opcode][funct3]
            
        return f"{inst} x{rd}, {imm}"
    
    elif f == "UJ":
        imm1 = splits[0]
        imm2 = splits[1]
        imm = sign_extension(imm1[0] + imm2[1:] + imm2[1] + imm1[1:])
        if imm[0] == 1:
            imm = -1 * int(imm,2)
        else:
            imm = int(imm,2)
        rd = int(splits[1],2)
        if funct3 not in insts[opcode]:
            return -1
        else:
            inst = insts[opcode][funct3]
            
        return f"{inst} x{rd}, {imm}"
    


def sign_extension(imm):
    sign = '0' 
    if imm[0] == 1:
        sign = '1'
    for i in range(32-len(imm)):
        imm =  sign + imm
    return imm 



count =0 

if len(sys.argv) != 2:
    print("Usage: ./riscv-sim filename")
    sys.exit(1)

with open(sys.argv[1], "rb") as f:
    binary_data = f.read()

bcodes = [binary_data[i:i+4] for i in range(0, len(binary_data), 4)]

for inst in bcodes:
    hcode = inst[::-1].hex()
    bcode = bin(int(hcode,16))[2:].zfill(32)

    opcode = bcode[25:32]
    
    if opcode not in form: #debug 
        print("unknown instruction")
        continue

    #2 opcode 읽고 format 결정 & format에 따라 필드 나누기 
    split_code = splits_field(bcode,form[opcode])
    #print(f"bin : {bcode}, op & form : {opcode}, {form[opcode]}")

    #3 disassembled string 받기 
    disassembled_code = disassembled(split_code,opcode)

    if disassembled_code == -1:
        print("unknown instruction")
    else:
        print(f"inst {count}: {hcode} {disassembled_code}")
        count+=1
        
f.close() 

