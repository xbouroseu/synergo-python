x = int(input("Give x: "))
y = int(input("Give y: "))
z = int(input("Give z: "))
w = x + y + z
i = 0
while w > 0:
	w = w - i*i
	i += 1
w = w*w
print("W: ", w)
