from sys import argv

f = argv[1]

text = open(f,'r')
nf = open('progress','w')
for line in text.readlines():
    nf.write(line.replace('def',''))
    
nf.close()
text.close

