#!/usr/bin/python

import pandas as pd
import json, getopt, os, sys, re


## Main
def main(argv):
    tweetsfile, noisefile, outputfile, length = get_inputfile(argv)
    tweets, noise = parseInput(tweetsfile, noisefile)
    data = getWordCounts(tweets, noise, length)
    dumpOutput(data, outputfile)

    print '\n --- All done! ---- \n'
    sys.exit()



## Process the arguments and return the settings
def get_inputfile(argv):
    err_msg = ('\n\n\n'
               'Please provide a json file of aggregated tweets:\n' 
               '\n\nOptional arguments are:\n'
               '-h, --help\t\tDisplay this message and exit\n'
               '-l, --length\t\tPreferred output length\n'
               '-n, --noise\t\tText file with noise terms to be filtered out\n'
               '-o, --output\t\tPrefix for output filename\n'
               '-t, --tweets\t\tJSON data file with tweets\n'
               'Example usage could be:\n'
               '$ ./filter.py data.json -O filtered_data.json\n\n')

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'l:n:o:t:hv', ['help', 'length', 'tweets', 'noise', 'output='])
    except getopt.GetoptError as err:
        print err_msg; sys.exit(2)

    length = None
    tweetsfile = ''
    noisefile = ''
    outputfile = ''

    for o, a in opts:
        if o in ('-h', '--help'):
            print err_msg; sys.exit()
        elif o in ("-l", "--length"):
            length = int(float(a))
        elif o in ("-n", "--noise"):
            noisefile = a
        elif o in ("-o", "--output"):
            outputfile = a
        elif o in ("-t", "--tweets"):
            tweetsfile = a

    #if not eventsfile or not entitiesfile or not timesfile or not opinionsfile: print err_msg; sys.exit()
    if not length: print '..... Output length not specified, using default: 1000 or max length'; length = 1000
    if not noisefile: print '..... Noise text file not specified, using default: noise.json'; noisefile = 'noise.json'
    if not outputfile: print '..... Output prefix not specified, using default: output.json'; outputfile = 'output'
    if not tweetsfile: print '..... Data file not specified, using default: data.json'; tweetsfile = 'data.json'

    return [tweetsfile, noisefile, outputfile, length]


## Parse input files
def parseInput(tweetsfile, noisefile):
    tweets = None

    try:
        print '....... Reading data file'
        print '                .... hold on ....'
        tweets = pd.read_json(tweetsfile)
    except IOError, e:
        print e; sys.exit()

    with open(noisefile) as f:
        noise = json.load(f)

    return tweets, noise


## Filter function used to filter out noise from tweet data
def allowed(value, noise):

    value = value.lower()

    if value.isdigit():
        return False

    if value in noise:
        return False

    if re.match( r'(^http|[^a-z])+', value):
        return False

    return True


## Translate values from one range to another
def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


## Get word counts
def getWordCounts(tweets, noise, length):
    print '.......... Pandas are working their magic now'
    print '                            ... might take a while .......'

    df = pd.DataFrame(columns=['text', 'size'])
    df['text'] = [re.sub(r'\W+$', '', word) for tweet in tweets['text'].str.split() for word in tweet if allowed(word, noise)]
    df['text'] = df['text'].str.lower()
    df['size'] = df.groupby('text')['text'].transform('count')
    df = df.dropna().drop_duplicates()
    df = df.sort(['size'], ascending=[0])

    max_size = df.iloc[0]['size']
    min_size = df.iloc[length if length < len(df.values) else len(df.values)-1]['size']

    return [{'text': x[0], 'size': translate(x[1], min_size, max_size, 10, 100)} for x in df.values[:length]]


## Dump aggregated tweets data
def dumpOutput(data, outputfile):

    with open(outputfile + '.json', 'w') as outfile:
        json.dump(data, outfile)

    print '...... Tweets data dumped into ' + outputfile + '.json'


if __name__ == "__main__":
    main(sys.argv[1:])
