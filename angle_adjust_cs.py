"""Created by Wettham77 :3"""

import time
import os


def read_lines(filename):
    """Reads the lines from the file"""
    with open(filename, 'r', errors="ignore") as file:
        for line in file:
            yield line.strip()
    file.close()


def write_lines(filename, lines):
    with open(filename, 'w') as file:
        for line in lines:
            file.write(line + '\n')


BASE_SIZE = 106.75
ALLOWED_CATCH_RANGE = 0.8

def catch_width(circle_size):
    """calculates the size of the catcher for this cs"""
    dr = (circle_size - 5) / 5
    scale = (1.0 - 0.7 * dr) / 2
    return 2 * BASE_SIZE * abs(scale) * ALLOWED_CATCH_RANGE

def circle_size_from_catch_width(cw):
    """calculates the cs from a catcher size"""
    abs_scale = cw / (2 * BASE_SIZE * ALLOWED_CATCH_RANGE)
    dr = (1.0 - 2 * abs_scale) / 0.7
    return dr * 5 + 5

def process_file(filename, rate_edit):
    """Process and edit the file's distances so the angles are the same"""
    time.sleep(3)
    passed_hit_object_tag = False
    pre_hit_object_lines = []
    hit_objects = []
    sv_changed = False
    for line in read_lines(filename):
        if line.startswith("CircleSize"):
            line_split = line.split(":")
            line_split[-1] = float(line_split[-1])
            cs = line_split[-1]
            catcher_size =  catch_width(cs)
            new_catcher_size = catcher_size/rate_edit
            new_cs = circle_size_from_catch_width(new_catcher_size)
            line_split[-1] = str(new_cs)
            pre_hit_object_lines.append(":".join(line_split))
        elif line.startswith("SliderMulti"):
            line_split = line.split(":")
            line_split[-1] = float(line_split[-1])
            line_split[-1] = str(line_split[-1] / rate_edit)
            pre_hit_object_lines.append(":".join(line_split))

        elif line == "[HitObjects]":
            passed_hit_object_tag = True
            pre_hit_object_lines.append(line)
        elif passed_hit_object_tag:
            hit_objects.append(line)
        else:
            pre_hit_object_lines.append(line)

    if not passed_hit_object_tag:  # Means that something has gone wrong
        raise Exception("No hit object tag found in the file")
    print("Hit objects found:                  " + str(filename))
    for i, hit_object in enumerate(hit_objects):
        # Convert the hit objects to 0 being the middle, 256 as rightmost and -256 as left most
        hit_object_parameters = hit_object.split(",")  # only should care about the first entry which is the x position
        hit_object_parameters[0] = float(hit_object_parameters[0]) - 256
        # Scaling the x distance so that the angle of the y (which is the time) and x (x distance) triangle are the same
        # as the original speed
        hit_object_parameters[0] = hit_object_parameters[0] / rate_edit
        hit_object_parameters[0] += 256  # Converting back to the regular x coordinate system
        hit_object_parameters[0] = str(hit_object_parameters[0])

        if "|" in hit_object:  # probably a slider idfk
            hit_object_parameters[7] = str(
                float(hit_object_parameters[7]) / rate_edit)  # SHOULD BE LENGTH HOPEFULLY IDK
            curve_data = hit_object_parameters[5]  # should be curve type including all the points
            curve_data_list = curve_data.split("|")
            for j, points in enumerate(curve_data_list[1:], start=1):
                x, y = points.split(":")
                new_xy = []
                # Process x (width = 512, half = 256) and y (height = 384, half = 192), scuffed cuz i wanted to save
                # lines like its some limited supply resource, what a dumbass
                for idx, position in enumerate([x, y]):
                    position = float(position)
                    if idx == 0:  # x coordinate
                        position -= 256
                        position = position / rate_edit
                        position += 256
                    else:  # y coordinate
                        position -= 192
                        position = position / rate_edit
                        position += 192
                    new_xy.append(str(position))
                curve_data_list[j] = ":".join(new_xy)

            curve_data = "|".join(curve_data_list)
            hit_object_parameters[5] = curve_data

        hit_objects[i] = ",".join(hit_object_parameters)

    write_lines(filename, pre_hit_object_lines + hit_objects)


# process_file("nao - Towa naru Kizuna to Omoi no Kiseki (rew0825) [Miracle 1.5x (435bpm) AR10 OD8.4].osu", 1.5)

def check_and_process(previous_path, modified_mp3_path):
    lines = list(read_lines(modified_mp3_path))
    last_modified = lines[-1]
    path = last_modified.split("|")[-1]
    path = path.lstrip()
    if previous_path is None:
        print("Found path successfully, previously edited map recorded")
        previous_path = path

    if previous_path == path:
        return previous_path, False

    mp3_name = last_modified.split("|")[0]
    mp3_name_parts = mp3_name.split(" ")
    rate_mp3 = mp3_name_parts[-2]
    rate = ""
    for character in rate_mp3:
        if character != "x":
            rate += character
        else:
            break

    rate = float(rate)

    if rate == None:
        print("rate not found")

    if path != previous_path:
        process_file(path, rate)
    print(path + " has been refactored")
    return path, True  # to use as previous path

reenter_path = int(input("Do you wish to reenter the path?, 1 yes, 0 no"))
location = read_lines("location")
file_name = [fil for fil in location]
modified_mp3_path = None
if len(file_name) != 0:
    modified_mp3_path = file_name[0]
if modified_mp3_path == None or reenter_path:
    modified_mp3_path = input(
        "Please enter the path to your 'modified_mp3_list.txt' file from osu!trainer. (Something along the lines of C:/.....osu!/Songs/modified_mp3_list.txt) \n")
    write_lines("location", [modified_mp3_path])

print("This should now probably edit any new rate adjusted maps from now on")
previous_path = None
while True:
    try:
        previous_path, bool = check_and_process(previous_path, modified_mp3_path)

    except Exception as e:
        print("An error occured with a file, " + str(type(Exception)))
    if not bool:
        time.sleep(3)
