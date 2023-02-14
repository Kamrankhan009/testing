homo = ""

testing = "abc"
testing2 = "xyz"
data = "mno"
data2 = "smo"

xy = ""

homo += testing + ","

homo += testing2 + ","

homo += data + ","

homo += data2 + ","

if xy:
    homo += xy + ","
else:
    print("wrong")



print(homo)

print(homo.split(','))