import json

current_data = json.load(open("split1.json", "r"))  
data = json.load(open("split2.json", "r"))  
current_is = [d["i"] for d in current_data]
new_is = [d["i"] for d in data]

#Create dictionary of i values mapping to elements of the list data
data_dict = {}
for i in range(len(data)):
    data_dict[data[i]["i"]] = data[i]

for i in new_is:
    if i not in current_is:
        current_data.append(data_dict[i])

print(data[-1])

j = json.dumps(current_data, indent=4)
with open("loggerify.json", "w") as f:
    f.write(j)