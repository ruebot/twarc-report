#!/usr/bin/env python

import os
import sys
import json
import math
import re
import optparse
import fileinput
import d3output # local module
import ast
from profiler import Profiler # local module
from profiler import LinkNodesProfiler # local module
from collections import Counter
import dateutil.parser # $ pip install python-dateutil


opt_parser = optparse.OptionParser()
opt_parser.add_option("-m", "--mode", dest="mode", help="retweets (default) | mentions | replies",
    default='retweets')
opt_parser.add_option("-t", "--threshold", dest="threshold", type="int", 
    help="minimum links to qualify for inclusion (default: 1)", default=1)
opt_parser.add_option("-o", "--output", dest="output", type="str", 
    help="embed | json (default: embed)", default="embed")
opt_parser.add_option("-p", "--template", dest="template", type="str", 
    help="name of template in utils/template (default: graph.html)", default="graph.html")
    
opts, args = opt_parser.parse_args()

output = opts.output

# prepare to serialize opts and args as json
# converting opts to str produces string with single quotes,
# but json requires double quotes
optsdict = ast.literal_eval(str(opts))
argsdict = ast.literal_eval(str(args))

class DirectedProfiler(LinkNodesProfiler):
    def __init__(self, opts):
        LinkNodesProfiler.__init__(self, opts)

    def process(self, tweet):
        Profiler.process(self, tweet)
        user = tweet["user"]["screen_name"]
        if self.mode == 'mentions':
            if "user_mentions" in tweet["entities"]:
                for mention in tweet["entities"]["user_mentions"]:
                    self.addlink(user, str(mention["screen_name"]))
        elif self.mode == 'replies':
            if not(tweet["in_reply_to_screen_name"] == None):
                self.addlink(tweet["in_reply_to_screen_name"], user)
        else: # default mode: retweets
            if "retweeted_status" in tweet:
                self.addlink(user, tweet["retweeted_status"]["user"]["screen_name"])
        # add to tweet count for this tag
        if not user in self.nodes:
            self.addsingle(user)
        self.nodes[user]["tweetcount"] += 1


    def report(self):
        return LinkNodesProfiler.report(self)

profiler = DirectedProfiler({"mode": opts.mode})

for line in fileinput.input(args):
    try:
        tweet = json.loads(line)
        profiler.process(tweet)
    except ValueError as e:
        sys.stderr.write("uhoh: %s\n" % e)

data = profiler.report()

profile = data["profile"]
nodes = data["nodes"]

optsdict["graph"] = "directed"
optsdict["field"] = "user"

if type(data) is dict:
    data["opts"] = optsdict
    data["args"] = argsdict

if output == "csv":
    print d3output.nodeslinkcsv(nodes)
elif output == 'json':
    values = d3output.nodeslinktrees(profile, nodes, optsdict, argsdict)
    print {"profile": profile, "values": values}
elif output == 'embed':
    print d3output.embed(opts.template, d3output.nodeslinktrees(profile, nodes, optsdict, argsdict))

