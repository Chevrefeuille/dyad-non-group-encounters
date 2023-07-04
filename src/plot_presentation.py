import matplotlib.pyplot as plt
import csv

def read_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            return row

non_disturbed_data = read_csv("../data/csv/will/result_non_disturbed.csv")
all_data = read_csv("../data/csv/will/result_all.csv")
disturbed_data = read_csv("../data/csv/will/result_disturbed.csv")
other_data = read_csv("../data/csv/will/result_other.csv")
list_of_social_binding = ["0", "1", "2", "3", "alone"]


fig,ax = plt.subplots(1, 1, figsize=(10, 10))
ax.set_title("Mean max deviation in function of the situation for all social bindings")
ax.set_xlabel("Social binding")
ax.set_ylabel("Mean max deviation")
ax.set_xticks([0,1,2,3,4])
ax.set_xticklabels(list_of_social_binding)
ax.plot(all_data, label="All")
ax.plot(non_disturbed_data, label="Non disturbed")
ax.plot(disturbed_data, label="Disturbed")
ax.legend()
plt.show()
