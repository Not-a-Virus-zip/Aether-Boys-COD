import json
import pprint
with open("food_data.json", "r", encoding="utf-8") as file:
    data = json.load(file)
    

# get the fdcId from here
foundation_foods = data["FoundationFoods"]
# print(pprint.pformat(list(foundation_foods[0])))
# print(str(foundation_foods)[:1000])

def process(descr: str):
    terms = descr.split(", ")
    terms.reverse()
    return " ".join(terms)

stuff = []
things_that_arent_dicts = []
for thing in foundation_foods:
    if not isinstance(thing, dict):
        things_that_arent_dicts.append(thing)
    else:
        stuff.append(thing["description"].strip())

stuff.sort()
stuff = list(map(lambda f: (process(f), f), stuff))

formatted_stuff = [thing.lower() for thing, _ in stuff]
# print("\n".join(f"{processed} <- {raw}" for (processed, raw) in stuff))
print("\n".join(formatted_stuff))

with open("ingredients_list.txt", "w") as file:
    file.write("\n".join(formatted_stuff))

# print([thing for thing in stuff if thing.find("  ")!= -1])
# print(sum(1 for thing in stuff if thing.startswith("Cheese")))
# print(things_that_arent_dicts)
# print(f"{len(foundation_foods) = }")
# print(f"{list(foundation_foods[0])=}")