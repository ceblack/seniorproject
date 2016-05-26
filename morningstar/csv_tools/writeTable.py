#!/usr/bin/env python3
import sys
import csv

def write_table(tablelist,filepath):
    with open(filepath, 'w', newline='') as csvfile:
        tablewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for item in tablelist:
            tablewriter.writerow(item)

if __name__ == "__main__":
    print("nothing here")
