from getResults import Result
import json
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--document", type=str, default="data/doc1.jpg")
    # output file --output
    parser.add_argument("--output", type=str, default="result.json")
    # number of question --number (default 60)
    parser.add_argument("--number", type=int, default=45)
    
    args = parser.parse_args()

    result = Result(args.document, args.number)
    result = result.result()
    r = list(dict())
    for key,value in result.items():
        r.append({"number":key, "option":value})

    with open(args.output, "w") as f:
        f.write(json.dumps(r, indent=4))

