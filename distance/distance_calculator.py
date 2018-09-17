import math, argparse

EARTH_R = 6371000.0 # radius of earth for calculations
REF_LONGITUDE = -78.777 # this may or may not be used within graph script
REF_LATITUDE = 43.000 # this may or may not be used within graph script

parser = argparse.ArgumentParser(description="Get travel distance our ofwaypoint file.")
parser.add_argument("wp_file", help="The input waypoints file")

args = parser.parse_args()
    
######
# validating waypoint file based on first line
def validate_input_file(lines):
    if lines[0].strip() == "QGC WPL 110":
        return True
    return False
######
# reading mission waypoints from input file
def read_mission(lines):
    command    = []
    latitude   = []
    longitude  = []
    for l in lines[1:]:
        if not l.strip():
            continue
        # finish reading if encuontered a non-digit
        if not l.strip()[0].isdigit(): 
            print "non digit start of line. stop reading."
            print l
            break
        print l
        l = l.strip().split('\t')
        print l
        command.append(int(l[3]))
        latitude.append(float(l[8]))
        longitude.append(float(l[9]))

    return command, latitude, longitude,
######

wp_file=open(args.wp_file, "r")
input_lines = wp_file.readlines()

if not (validate_input_file(input_lines)):
    print "Input file is not valid (wrong file version?)"
    exit(0)


wp_command, wp_latitude, wp_longitude = read_mission(input_lines)

distance_step = [0]

for i in range(1, len(wp_command)):
    lat_start = math.radians(wp_latitude[i-1])
    lon_start = math.radians(wp_longitude[i-1])
    lat_end   = math.radians(wp_latitude[i])
    lon_end   = math.radians(wp_longitude[i])
    delta_lat = lat_end - lat_start
    delta_lon = lon_end - lon_start
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat_start) * math.cos(lat_end) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    dist = EARTH_R * c
    distance_step.append(dist)


total_distance = 0
print "ID \t  CMD \t   LAT   \t   LON   \t Step \t Total"
for i in range(len(wp_command)):
    total_distance += distance_step[i]
    print("{0:3d}\t{1:5d}\t{2:9.6f}\t{3:9.6f}\t{4:6.1f}\t{5:7.1f}".format(i, wp_command[i], wp_latitude[i], wp_longitude[i], distance_step[i], total_distance))

#looking for take off as starting point

