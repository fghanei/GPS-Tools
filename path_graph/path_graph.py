import math, argparse, time

UPDATE_REF = False # update reference point based on the first waypoint
EARTH_R = 6371000.0 # radius of earth for calculations
INITIAL_LONGITUDE = -78.77810 # this may or may not be used within graph script
INITIAL_LATITUDE = 42.99849   # this may or may not be used within graph script
ROUND_ANGLES = [0 , 45, 90, 135, 180]

global GRAPH_NAME   #name of graph file
GRAPH_FORMAT='png'   #png, pdf, ps, eps, svg.
GRAPH_DPI=300
GRAPH_FIG_WIDTH = 25
GRAPH_FIG_HEIGHT= 10
GRAPH_IMAGE_SCALE = 10#7.725
GRAPH_MARKER_SIZE = 12
GRAPH_LINE_WIDTH = 3

global SUFFIX
global DUMP_FILE # file to store results
global VERBOSE
global VERBOSE_STR #
class DUMP: # level of verbose
    ERROR=0
    WARNING=1
    INFO=2
    DEBUG=3

VERBOSE_STR=["ERROR", "WARNING", "INFO", "DEBUG"]

# setting up the parser
parser = argparse.ArgumentParser(description="Get travel distance our ofwaypoint file. As of now it only takes on mission file, consiss only of waypoints")
# input mission file
parser.add_argument("wp_file", help="The input waypoints file")
parser.add_argument("-g", "--graph", help="Draws the path. Needs matplotlib and pillow (from PIL import Image rather than import Image)", action="store_true")
parser.add_argument("-e", "--exact", help="Report exact angles instead of rounding them into 0, 45, 90, 135, 180", action="store_true")
parser.add_argument("-v", "--verbose", help="level of verbosity (1 WARNINGS only, 2 INFO, 3 DEBUG level")
parser.add_argument("-r", "--resolution", help="The resolution of grid. thi is tu adjust image boundary only.")
parser.add_argument("-a", "--lambda_param", help="coefficient for distance (kj/m)")
parser.add_argument("-m", "--gamma_param", help="coefficient for turn (kj/degree)")
parser.add_argument("-x", "--suffix", help="A suffix for the log file and graph file name")

args = parser.parse_args()

#default vallues
ROUND_FLAG = True # round angles to 0, 45, 90, 135 by default. -> overriden by --exact
VERBOSE = 2
RESOLUTION = 10.0 #by default
LAMBDA = 1
GAMMA = -1
TURN_COST = [0.0, 0.09592376, 0.90877848, 2.50663892] #non linear for each turn, in case GAMMA is not given
GRAPH_NAME="path"
SUFFIX=""

if args.exact:
    ROUND_FLAG = False

if args.verbose>0:
    VERBOSE=args.verbose

if args.resolution:
    RESOLUTION = float(args.resolution)

if args.lambda_param>0:
    LAMBDA = float(args.lambda_param)

if args.gamma_param>0:
    GAMMA = float(args.gamma_param)

if GAMMA > 0:
    TURN_COST = [0 * GAMMA, 45.0 * GAMMA, 90.0 * GAMMA, 135.0 * GAMMA]
else:
    print "gamma is not set, using the table for 45, 90, and 135 degrees"

if args.suffix:
    SUFFIX = "_"+args.suffix

GRAPH_NAME = GRAPH_NAME + SUFFIX
DUMP_FILE=open("path_log"+SUFFIX+".txt","a")

###################################
def dump(verb, myStr):
    global DUMP_FILE
    global VERBOSE

    if (verb<=VERBOSE):
        print myStr

    now = time.time()
    myStr = "{0:8s}\t{1:14s}\t{2:s}".format(VERBOSE_STR[verb],time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime(now)),myStr)
    DUMP_FILE.write(myStr+"\n")
    return
###################################
# validating waypoint file based on first line
def validate_input_file(lines):
    if lines[0].strip() == "QGC WPL 110":
        return True
    return False
####################################
# reading mission waypoi from input file
def read_mission(lines):
    command    = []
    latitude   = []
    longitude  = []
    for line in lines[1:]: #skipping the version line
        if not line.strip():
            continue
        # finish reading if encuontered a non-digit
        l = line.strip().split('\t')
        if not l[0][0].isdigit(): 
            dump(DUMP.WARNING, "Encountered non digit start of line in mission file. stop reading: \t"+ line)
            break
        command.append(int(l[3]))
        latitude.append(float(l[8]))
        longitude.append(float(l[9]))

        # as of now only supports waypoint/takeoff/land only
        # http://mavlink.org/messages/common
        if not (command[-1] in [16,21,22]):
            dump(DUMP.ERROR, "Unknown command in mission file %d, aborting: \t"%(command[-1])+ line)
            exit(0)

    return command, latitude, longitude
####################################
# drawing a path and graph it
# using projection in https://en.wikipedia.org/wiki/Equirectangular_projection
def draw_path(lats, lons):
    dump(DUMP.DEBUG, "******* drawing path *******")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    LON_RATIO = math.cos(math.radians(INITIAL_LATITUDE))
    X=[]
    Y=[]
    dump(DUMP.DEBUG, "ID \t    X(m) \t    Y(m)")
    for i in range(len(lats)):
        Y.append(EARTH_R * math.radians(lats[i]-INITIAL_LATITUDE))
        X.append(EARTH_R * math.radians(lons[i]-INITIAL_LONGITUDE) * LON_RATIO)
        dump(DUMP.DEBUG, "{0:3d}\t{1:8.2f}\t{2:8.2f}".format(i, X[-1], Y[-1]))

    # from meters to pixel, based on the background map size
    X = [x * GRAPH_IMAGE_SCALE for x in X]
    Y = [y * GRAPH_IMAGE_SCALE for y in Y]

    min_x = int(min(X) - 1.5 * RESOLUTION * GRAPH_IMAGE_SCALE)
    max_x = int(max(X) + 1.5 * RESOLUTION * GRAPH_IMAGE_SCALE)
    min_y = int(min(Y) - 1.5 * RESOLUTION * GRAPH_IMAGE_SCALE)
    max_y = int(max(Y) + 1.5 * RESOLUTION * GRAPH_IMAGE_SCALE)

    img=plt.imread("map.png")
    IMG_LEN = len(img)
    img2 = img[IMG_LEN-max_y:IMG_LEN-min_y, min_x:max_x]
    ax.imshow(img2, extent=[min_x, max_x, min_y, max_y])

    ax.plot(X, Y, '-or', markersize=GRAPH_MARKER_SIZE, linewidth=GRAPH_LINE_WIDTH)
    ax.plot(X[0:3], Y[0:3], '-og', markersize=GRAPH_MARKER_SIZE, linewidth=GRAPH_LINE_WIDTH)
    ax.plot(X[0], Y[0], '-ob', markersize=GRAPH_MARKER_SIZE, linewidth=GRAPH_LINE_WIDTH)

    #plt.gca().set_aspect('equal', adjustable='box')
    #plt.show()
    plt.savefig("%s.%s"%(GRAPH_NAME, GRAPH_FORMAT), dpi=GRAPH_DPI, format=GRAPH_FORMAT)
    return
####################################
###### start of the main script
####################################

# readin the input file and validate it
wp_file=open(args.wp_file, "r")

input_lines = wp_file.readlines()

if not (validate_input_file(input_lines)):
    dump(DUMP.ERROR,"Input file is not valid (wrong file version?)")
    exit(0)

wp_command, wp_latitude, wp_longitude = read_mission(input_lines)

# updating reference coordiante
if UPDATE_REF:
    INITIAL_LATITUDE = wp_latitude[0]
    INITIAL_LONGITUDE = wp_longitude[0]

rad_lat = [math.radians(l) for l in wp_latitude]
rad_lon = [math.radians(l) for l in wp_longitude]

# calculating distances and turns for each step
distance_step = [0,0]
turn_step = [0,0]
for i in range(2, len(wp_command)):
    # using Haversine formula from https://www.movable-type.co.uk/scripts/latlong.html
    delta_lat = rad_lat[i] - rad_lat[i-1]
    delta_lon = rad_lon[i] - rad_lon[i-1]
    a = math.sin(delta_lat / 2) ** 2 + math.cos(rad_lat[i-1]) * math.cos(rad_lat[i]) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    dist = EARTH_R * c
    distance_step.append(dist)

    # using law of Cosines to calculate angle
    r = distance_step[-2]
    e = distance_step[-1]
    if (r*e > 0): #avoid division by zero
        delta_lat = rad_lat[i] - rad_lat[i-2]
        delta_lon = rad_lon[i] - rad_lon[i-2]
        a = math.sin(delta_lat / 2) ** 2 + math.cos(rad_lat[i-2]) * math.cos(rad_lat[i]) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        s = EARTH_R * c
        t = (r * r + e * e - s * s) / (2.0 * r * e)
        if (t>1.0):
            t=1.0
        if (t<-1.0):
            t=-1.0
        turn = math.pi - math.acos(t)
    else:
        turn = 0.0
    turn = math.degrees(turn)
    if ROUND_FLAG:
        turn = min(ROUND_ANGLES, key=lambda x:abs(x-turn))
    turn_step.append(int(turn))

# calculating todal distance and pring results
total_distance = 0
total_turn = 0
total_turn_cost = 0
dump(DUMP.DEBUG, "ID \t  CMD \t   LAT   \t   LON   \t   Step  \t Total  \t Turn \t Total")
for i in range(len(wp_command)):
    total_distance += distance_step[i]
    total_turn += turn_step[i]
    total_turn_cost += TURN_COST[turn_step[i]/45]

    dump(DUMP.DEBUG, "{0:3d}\t{1:5d}\t{2:9.6f}\t{3:9.6f}\t{4:8.1f}\t{5:8.1f}\t{6:6d}\t{7:7d}".format(
            i, wp_command[i], wp_latitude[i], wp_longitude[i], distance_step[i], total_distance, turn_step[i],total_turn))


dump(DUMP.INFO, "****************************************")
dump(DUMP.INFO, "For input file: "+args.wp_file)
dump(DUMP.INFO, "Total Distance: %.1f | Total Turn: %.1f | Number of 45' Turn: %d | Number of 90' Turn: %d | Number of 135' Turn: %d | Number of 180' Turn: %d"%
                    (total_distance,  total_turn, turn_step.count(45), turn_step.count(90), turn_step.count(135), turn_step.count(180)))
dump(DUMP.INFO, "Distance Cost (lambda=%.4f): %.3f"%(LAMBDA, total_distance * LAMBDA))
dump(DUMP.INFO, "Turn Cost (gamma, gamma_45, gamma_90, gamma_135 =%.4f %.4f %.4f %.4f):      %.3f"%(GAMMA, TURN_COST[1], TURN_COST[2], TURN_COST[3],  total_turn_cost))
dump(DUMP.INFO, "Total Cost:                  %.3f"%(total_distance * LAMBDA + total_turn_cost))
dump(DUMP.INFO, "****************************************")


# calling the graph
if args.graph:
    draw_path(wp_latitude, wp_longitude)

####################################
