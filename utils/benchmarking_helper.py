import sys

if __name__=="__main__":
    filename = sys.argv[1] # input file or measurement for plot mode
    output_name = sys.argv[2] # name of output file
    f = open("../benchmarking_temps/" + output_name + ".txt", "w")
    f.write("Woops! I have deleted the content!")
    f.close()