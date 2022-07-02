import json
in_files = ["docs/all_results_original.json", "2018.json", "2019.json", "2021.json", "2022.json"]
out_file = "docs/all_results.json"

data = []
for file in in_files:
    print(f"Loading {file}")
    with open(file) as fp:
        data.extend(json.load(fp))

with open(out_file, "w") as fp:
    json.dump(data, fp, indent=2)
