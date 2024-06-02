# Returns ranges if command is correct, or None if parsing failed (incorrect command)
def parse_ranges(cmd, data_size):
    if cmd == "#":
        return [(0, data_size - 1)]

    num1, num2 = "", ""
    ranges = []

    cmd += ","
    for c in cmd:
        if c.isdigit():
            num1 += c
        elif c == '-':
            if num2 != "":
                print("[COMMAND PARSER] Incorrect usage of '-'")
                return None
            num1, num2 = num2, num1
        elif c == ',':
            if num2 == "" and num1 == "":
                print("[COMMAND PARSER] Incorrect usage of ','")
                return None
            elif num2 == "":
                if int(num1) <= 0:
                    print("[COMMAND PARSER] Incorrect indices: you can use only positive values")
                    return None
                ranges.append((int(num1) - 1, int(num1) - 1))
            else:
                if int(num1) <= 0 or int(num2) <= 0:
                    print("[COMMAND PARSER] Incorrect indices: you can use only positive values")
                    return None
                elif int(num2) > int(num1):
                    print("[COMMAND PARSER] Incorrect indices: first index is greater than second")
                    return None
                ranges.append((int(num2) - 1, int(num1) - 1))
            num1, num2 = "", ""
        elif c == ' ':
            continue
        else:
            print("[COMMAND PARSER] Invalid symbol:", c)
            return None

    return ranges


def merge_ranges(ranges: list):
    # Sort by first value ascending, and then by second value descending
    ranges.sort(key=lambda x: (x[0], -x[1]))

    results = []
    error_value = -3
    min_bound, max_bound = error_value, error_value
    for r in ranges:
        if r[0] > max_bound + 1:
            if min_bound != error_value:
                results.append((min_bound, max_bound))
            min_bound = r[0]
            max_bound = r[1]
        elif r[1] > max_bound:
            max_bound = r[1]
    if min_bound != error_value:
        results.append((min_bound, max_bound))

    return results


# if __name__ == "__main__":
#     cmd = "1-7, 5, 10-18"
#     ranges = parse_ranges(cmd, 100)
#     print("After parsing:", ranges)
#     merged = merge_ranges(ranges)
#     print("After merge:", merged)