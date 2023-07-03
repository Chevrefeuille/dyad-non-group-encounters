import matplotlib.pyplot as plt


non_disturbed_data = [118.23960102887247,113.3526767214382, 151.56786165177346,132.48819806326802, 154.04223676971273]
all_data = [156.43670630933292, 154.0004832357587, 145.95828330300708,135.47683607411992 , 159.68050414905602]
disturbed_data = [200.6641705056591, 201.24375404582526, 181.9996156475991, 142.6281574472449, 234.97674153363997]
list_of_social_binding = ["0", "1", "2", "3", "alone"]


fig,ax = plt.subplots(1, 1, figsize=(10, 10))
ax.set_title("Mean max deviation in function of the situation for all social bindings")
ax.set_xlabel("Social binding")
ax.set_ylabel("Mean max deviation")
ax.set_xticks([0,1,2,3,4])
ax.set_xticklabels(list_of_social_binding)
ax.plot(all_data, label="All")
# ax.plot(non_disturbed_data, label="Non disturbed")
ax.plot(disturbed_data, label="Disturbed")
ax.legend()
plt.show()
