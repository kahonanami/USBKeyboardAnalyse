import sys, argparse, os

#Dictionary
Keys = {'00':'', "04":"a", "05":"b", "06":"c", "07":"d", "08":"e", "09":"f", "0a":"g", "0b":"h", "0c":"i", "0d":"j", "0e":"k", "0f":"l", "10":"m", "11":"n", "12":"o", "13":"p", "14":"q", "15":"r", "16":"s", "17":"t", "18":"u", "19":"v", "1a":"w", "1b":"x", "1c":"y", "1d":"z","1e":"1", "1f":"2", "20":"3", "21":"4", "22":"5", "23":"6","24":"7","25":"8","26":"9","27":"0","28":"<RET>","29":"<ESC>","2a":"<DEL>", "2b":"<ENTER>","2c":"<SPACE>","2d":"-","2e":"=","2f":"[","30":"]","31":"\\","32":"<NON>","33":";","34":"'","35":"<GA>","36":",","37":".","38":"/","39":"<CAP>","3a":"<F1>","3b":"<F2>", "3c":"<F3>","3d":"<F4>","3e":"<F5>","3f":"<F6>","40":"<F7>","41":"<F8>","42":"<F9>","43":"<F10>","44":"<F11>","45":"<F12>","59":"1","5a":"2","5b":"3","5c":"4","5d":"5","5e":"6","5f":"7","60":"8","61":"9","62":"0","63":"."}

shiftKeys = {"00":'', "04":"A", "05":"B", "06":"C", "07":"D", "08":"E", "09":"F", "0a":"G", "0b":"H", "0c":"I", "0d":"J", "0e":"K", "0f":"L", "10":"M", "11":"N", "12":"O", "13":"P", "14":"Q", "15":"R", "16":"S", "17":"T", "18":"U", "19":"V", "1a":"W", "1b":"X", "1c":"Y", "1d":"Z","1e":"!", "1f":"@", "20":"#", "21":"$", "22":"%", "23":"^","24":"&","25":"*","26":"(","27":")","28":"<RET>","29":"<ESC>","2a":"<DEL>", "2b":"<ENTER>","2c":"<SPACE>","2d":"_","2e":"+","2f":"{","30":"}","31":"|","32":"<NON>","33":"\"","34":":","35":"<GA>","36":"<","37":">","38":"?","39":"<CAP>","3a":"<F1>","3b":"<F2>", "3c":"<F3>","3d":"<F4>","3e":"<F5>","3f":"<F6>","40":"<F7>","41":"<F8>","42":"<F9>","43":"<F10>","44":"<F11>","45":"<F12>","59":"<END>","5a":"<Down Arrow>","5b":"<PageDn>","5c":"<Left Arrow>","5d":"","5e":"","5f":"<Home>","60":"<Up Arrow>","61":"<PageUp>","62":"<Insert>","63":"<Delete>"}

Modifier_keys_dictoinary=["Ctrl + ","Shift + ","Alt + ","GUI + ","Ctrl + ","Shift + ","Alt + ","GUI + "]

#DATA
transformdata=[]

#Run the tshark to extract data
def run_tshark(out_file,file,filter,field):
    if filter is not None:
        command = f"tshark -r {file} -Y {filter} -T fields -e {field} > {out_file}"
    else:
        command = f"tshark -r {file} -T fields -e {field} > {out_file}"
    try:
        os.system(command)
        print(f"\nData extracted in {out_file}. ")
    except:
        print("\nFailed to extract data.")

#Format the extracted data
def formatdata(out_file):
    formatfile = open(f"format_{out_file}","w")

    with open(f"{out_file}","r") as file:
        for i in file:
            if len(i.strip("\n")) == 16:
                Bytes = [i[j:j+2] for j in range(0, len(i.strip("\n")), 2)]
                data = ":".join(Bytes)
                formatfile.writelines(data+"\n")
    
    formatfile.close()
    print(f"Data formated in format_{out_file}")


#Transform the data
def transform(out_file):
    print("\n-------------------START RUNNING-------------------\n")
    with open(f"format_{out_file}") as file:
        for line in file:
            transformdata.append(line.replace("\n",""))

    ans=[]
    i = 0
    while(i<len(transformdata)):
        byte = transformdata[i].split(':')
        if byte[0] == "00":
            ans.append(Keys[byte[2]])
            i+=1
        #normal
        elif byte[0] in ["20","22","02"]:
            ans.append(shiftKeys[byte[2]])
            i+=1
        #shift
        elif byte[0] in ["04", "44", "40"]:
            character=""
            j=i
            while(j < len(transformdata) and transformdata[j].split(':')[0] in ["04", "44", "40"]):
                character+=Keys[transformdata[j].split(':')[2]]
                j+=1
            #add alt_num
            try:
                character = int(character)
                if character <=126:
                    ans.append(chr(character))#ascii
                else:
                    character="\\u"+str(hex(character))[2:]
                    ans.append(character.encode('utf-8').decode('unicode-escape'))#unicode
            except:
                ans.append('['+"Alt + "+character+']')
            i=j
        #alt
        else:
            Modifier_keys=""
            for j in range(8):               
                if(((int(byte[0], 16) >> j) & 1) and byte[2] != "00"):
                    Modifier_keys+=Modifier_keys_dictoinary[j]
                    ans.append('['+Modifier_keys+Keys[byte[2]]+']')
            i+=1

    #Upper
    p = 0
    for i in range(len(ans)):
        try:
            if ans[i] == "<CAP>":
                p += 1
                ans.pop(i)
                if p == 2:
                    p = 0
            if p != 0:
                ans[i] = ans[i].upper()
        except:
            pass

    #Del
    for i in range(len(ans)):
        try:
            a = ans.index('<DEL>')
            del ans[a]
            if "Alt" not in ans[a-1]:
                del ans[a - 1]
        except:
            pass

    print('output :' + "\n\n" + "".join(ans))
    print("")

    f=input(f"Do you want to delete {out_file}?(y/n) : ")
    if(f=='y'):
        os.remove(f"{out_file}")
    s=input(f"Do you want to delete format_{out_file}?(y/n) : ")
    if(s=='y'):
        os.remove(f"format_{out_file}")
        
banners="""
   __  __     __    __ __           __                         __   
  / / / /____/ /_  / //_/__  __  __/ /_  ____  ____ __________/ /   
 / / / / ___/ __ \/ ,< / _ \/ / / / __ \/ __ \/ __ `/ ___/ __  /    
/ /_/ (__  ) /_/ / /| /  __/ /_/ / /_/ / /_/ / /_/ / /  / /_/ /     
\____/____/_.___/_/ |_\___/\__, /_.___/\____/\__,_/_/   \__,_/      
                          /____/

    ___                __
   /   |  ____  ____ _/ /_  __________
  / /| | / __ \/ __ `/ / / / / ___/ _ \\
 / ___ |/ / / / /_/ / / /_/ (__  )  __/
/_/  |_/_/ /_/\__,_/_/\__, /____/\___/
                     /____/                          
                                                            --by kahonanami
"""

print(banners)

parser = argparse.ArgumentParser(description='None')
parser.add_argument('-f', '--file', help='here is file', required=True)
parser.add_argument('-Y', '--filter',help='here is filter',required=False)
parser.add_argument('-e',"--field",help='here is output format,HID Data is usbhid.data while Leftover Capture Data is usb.capdata. ',required=True)
parser.add_argument('-o',"--out_file",help='here is outfile name, default is extracted.txt',required=False, default='extracted.txt')

args = parser.parse_args()

run_tshark(out_file=args.out_file,file=args.file,filter=args.filter,field=args.field)
formatdata(out_file=args.out_file)
transform(out_file=args.out_file)