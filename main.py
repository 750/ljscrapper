#!/usr/bin/env python3

from ljscrapper import *
#import json_to_html
import os
import sys
import argparse
import json

hello = "Thou shalt not read source files"

def main():
    parser = argparse.ArgumentParser(description='Parse LiveJournal blogs. \n This tool does not know how to work with blogs that dont have any articles, consider yourself warned.', prog='LJScrapper CLI tool')
    parser.add_argument('blogname', type=str, help='blogname as in blogname.livejournal.com domain; if the domain is not *.livejournal.com, this argument should be the whole domain name, like varlamov.ru')
    parser.add_argument('--input_file', '-i', help='path to input file; if not specified, starts from scratch',default=None)
    parser.add_argument('--output_file', '-o', help='path to output file; required',required=True)
    parser.add_argument('--period', '-p', type=int, default=10, help='saves every PERIOD articles, default is 10')
    args = parser.parse_args()
    parseArgs(args.blogname, args.input_file, args.output_file, args.period)

def parseArgs(blogname, input_path, output_path, chunk_size):
    url_template = "https://{}.livejournal.com/"
    the_url = url_template.format(blogname)
    is_404 = requests.get(the_url,verify=False).status_code == 404
    if is_404:
        print("Blog \"{}\" does not exist. Quitting...".format(blogname))
        sys.exit()
    else:
        print("Blog \"{}\" exists. Working...".format(blogname))
    #print(input_path)
    if input_path:
        '''
        Input path specified
        '''
        try:
            f = open(input_path)
            starting_data = json.load(f)
            if starting_data["blogname"] != blogname:
                raise IOError("DifferentBlognamesError")
            a = Blog()
            a.read_from_json(starting_data)
            f.close()
        except (FileNotFoundError, json.JSONDecodeError, IOError("DifferentBlognamesError")) as e:
            if e == FileNotFoundError:
                print("Input file \"{}\" was specified, but does not exist. Quitting...".format(input_file))
            elif e == json.JSONDecodeError:
                print("Input file \"{}\" exists, but is not a correct JSON file. Quitting...".format(input_file))
            elif e == IOError("DifferentBlognamesError"):
                print("Specified blogname \"{}\" and input file's \"{}\" blogname \"{}\" are different. This probably means that you specified wrong input file. Quitting...".format(blogname, input_path, starting_data["blogname"]))
            sys.exit()
        print("Succesfully read file. It has {} articles. Working...".format(a.get_size()))
    else:
        '''
        Input path not specified
        '''
        a = Blog(blogname)
        print("Created Blog object. Working...")
    while not a.is_full():
        print("Articles in file: {}".format(a.get_size()))
        a.retrieve_up(how_many=chunk_size)
        a.retrieve_down(how_many=chunk_size)
        try:
            f = open(output_path, 'w', encoding='utf8')
            json.dump(a.save(), f, ensure_ascii=False, sort_keys=True, indent=4)
            f.close()
            print("Saved yet another batch of articles. Working...")
        except:
            print("Something went wrong with writing process. Check how you specified output_path. Maybe you are trying to write to a restricted location. \nIf the problem is related to your internet connection, just restart script with the current output file path as both your input and output paths")
            sys.exit()
    print("It appears the script has done its job. \nTotal number of articles is {}. Quitting for a good reason...".format(a.get_size()))

if __name__ == "__main__":
    main()
