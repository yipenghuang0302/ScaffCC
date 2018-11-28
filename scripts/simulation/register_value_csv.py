#!/usr/bin/env python
import sys, re, cmath, csv, os, glob

regex = re.compile("([a-zA-Z]+)([0-9]+)")
outcome = { 'polar_r':0, 'polar_phi':0, 'rect_real':0, 'rect_imag':0 }
reg_map = []

# open QX source file
with open(sys.argv[1], 'r') as qcfile:
    for line in qcfile:
        if 'map q' in line:
            print line
            words = line.split()
            reg_index_pair = regex.match(words[2])
            register = reg_index_pair.group(1)
            index = int(reg_index_pair.group(2))

            reg_map.append((register,index))
            outcome[register] = 0

# print reg_map

with open(sys.argv[2], 'a+') as csvfile:

    writer = csv.DictWriter(csvfile, fieldnames=list(outcome.keys()))
    if not csvfile.read():
        writer.writeheader()

    filenames = glob.glob(os.path.splitext(sys.argv[1])[0]+'.trial_*.out')
    print filenames
    for filename in filenames:
        with open(filename) as file:

            # Parse QX Simulator output format
            state_lines = False
            first_basis = True
            phase_global = 0.0
            for line in file:
                print line
                if line.strip() == "--------------[quantum state]--------------":
                    print("--------------[quantum state]--------------")
                    state_lines = True
                elif state_lines and line.strip() == "-------------------------------------------":
                    print("-------------------------------------------")
                    state_lines = False
                elif state_lines:
                    strings = re.findall(r"[-+]?\d*\.\d+|\d+", line)

                    # zeros an outcome structure
                    outcome = dict.fromkeys(outcome, 0)

                    # grab real and imaginary parts of basis state amplitude
                    (outcome['polar_r'],outcome['polar_phi']) = cmath.polar(complex(float(strings[0]),float(strings[1])))

                    # if (outcome['polar_r']>0.0):
                    if (outcome['polar_r']>1.0/256.0):

                        # if this is the first basis state then this is the global phase to factor out
                        if first_basis:
                            phase_global = outcome['polar_phi']
                            first_basis = False

                        outcome['polar_phi'] -= phase_global
                        rect = cmath.rect(outcome['polar_r'],outcome['polar_phi'])
                        outcome['rect_real'] = rect.real
                        outcome['rect_imag'] = rect.imag

                        # print zip(strings[2][::-1],reg_mapping)
                        for elem in zip(strings[2][::-1],reg_map):
                            outcome[elem[1][0]] += int(elem[0]) << elem[1][1]

                        out_string = 'polar: ({:f},{:f}) rect: ({:f},{:f}) |{:s}>'.format(
                            outcome['polar_r'],
                            outcome['polar_phi'],
                            outcome['rect_real'],
                            outcome['rect_imag'],
                            strings[2],
                        )
                        print(out_string)
                        writer.writerow(outcome)
