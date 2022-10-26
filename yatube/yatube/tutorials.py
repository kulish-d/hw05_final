n = int(input())
m = None
q = -4
k = -2
for i in range(2*n+1):
    for j in range(2*n+1):
        if i == j:
            print(0)
        print(j+q)
        q-=1
    print(i+k)

