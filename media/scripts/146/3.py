a1="abcdefghijklmnopqrstuvwxyz"
b1="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
k=int(input())%26
m=input()
a2=a1[k:]+a1[:k]
b2=b1[k:]+b1[:k]
s=""
for i in range(len(m)):
    if m[i] in a1:
        s+=a2[a1.find(m[i])]
    elif m[i] in b1:
        s+=b2[b1.find(m[i])]
    else:
        s+=m[i]
print(s)
