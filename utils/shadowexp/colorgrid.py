import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from matplotlib import colors
import numpy as np

# figure(num=None,figsize=(10,100))

makespan=98
x_axis_max_len = 105

p1 = [(29, 42, '1'), (60, 81, '7'), (84, 98, '9')]
p2 = [(22, 40, '4')]
p3 = [(0, 11, '0'), (11, 21, '3'), (21, 30, '2'), (30, 45, '5'), (45, 55, '6'), (58, 71, '8')]
  
procs = [p1,p2,p3]
fig, ax = plt.subplots(3)
data = np.zeros((105,3)).transpose()
count=0
xticks = []
# print(data[count])
for proc in procs:
    for tup in proc:
        # data[count][tup[0]]=0.5
        data[count][(tup[0]):tup[1]]=1
        # data[count][tup[1]]=0.5
        text = ax[count].text((tup[1]+tup[0])/2, count, tup[2],  verticalalignment='center',color="w")
        # data[count][tup[1]+1]=0.5
        xticks.append(tup[1])
    count+=1   

print(data)



# Set figure width to 12 and height to 9
# fig_size=(8,6)
# # fig_size[0] = 12
# # fig_size[1] = 9
# plt.rcParams["figure.figsize"] = fig_size
# create discrete colormap
# cmap = colors.ListedColormap(['red', 'blue'])
# bounds = [0,100,100]
# norm = colors.BoundaryNorm(bounds, cmap.N)


ax[0].imshow(np.array([data[0]]), cmap="Blues")
# fig.dpi=1000

# draw gridlines
ax[0].set_yticks(np.arange(0,2)-.5, minor=True)
ax[0].set_xticks(xticks)

ax[0].grid(which='minor', axis='y', linestyle='-', color='w', linewidth=5)
# ax.grid(which='major', axis='x', linestyle='-', color='w', linewidth=1)
ax[0].set_yticks(np.arange(0,1));

ax[0].set_aspect(8)
plt.show()  