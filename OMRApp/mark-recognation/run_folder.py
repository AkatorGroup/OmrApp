from getResults import saveResults
import json
import os
import argparse

if __name__ == "__main__":
    # argparser
    parser = argparse.ArgumentParser()
    # folder path --documents
    parser.add_argument("--documents", type=str, default="documents")
    # output file --output
    parser.add_argument("--output", type=str, default="output.json")
    # number of question --number (default 60)
    parser.add_argument("--number", type=int, default=60)
    args = parser.parse_args()
    number_of_questions = args.number
    
    save = saveResults(number_of_questions)
    results = save.inputFolder(args.documents)
    # save the results
    save.saveResults(results, args.output)