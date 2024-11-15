s =input()
r=[]
for i in s:
    if i.isdigit():
        r.append(int(i))
print(sum(r))  
