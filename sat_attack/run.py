import argparse
import time

import sat_attack

import csv

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Perform a SAT attack on a locked circuit.")
    parser.add_argument("locked_ckt", help="The locked benchmark file")
    parser.add_argument("oracle", help="The unlocked benchmark file")
    parser.add_argument("-t", "--timeout", type=int, help="The maximum runtime of the SAT attack in seconds.")
    parser.add_argument("-d", "--detailed", action="store_true", help="Outputs detailed timing information for each iteration of the SAT attack.")

    args = parser.parse_args()

#     already_done = set()
#     with open("sat.csv", "r") as f:
#         reader = csv.reader(f)
#         for row in reader:
#             already_done.add(row[0])

    # if args.locked_ckt in already_done:
    #     print("ALREADY DONE")
    # else:
    attack = sat_attack.SatAttack(args.locked_ckt, args.oracle)

    start = time.time()
    attack.run(args.timeout, args.detailed)
    end = time.time()

    print("Elapsed time: %.3fs\n" % (end - start))

