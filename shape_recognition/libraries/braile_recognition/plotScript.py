import numpy as np
import matplotlib.pyplot as plt
c = 0
r = 3
s = np.loadtxt('./NewData_BRC/BRC_B5.txt')
taxel = []
for k in range(c,len(s),4):
    taxel.append(s[k,r])
print len(taxel)
plt.figure()
plt.plot(taxel)
plt.show()
