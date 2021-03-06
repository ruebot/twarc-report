# twarc-report
Data conversions and examples for generating reports from [twarc](https://github.com/edsu/twarc) collections using tools such as D3.js

- [D3 Visualizations](#user-content-d3-visualizations)
- [Exploring D3 Examples](#user-content-exploring-d3-examples)
- [Adding Scripts](#user-content-adding-scripts)
- [License](#user-content-license)

These utilities accept a Twitter json file (as fetched by twarc),
analyze it various ways, and output a json or csv file. The initial
purpose is to feed data into D3.js for various visualizations, but the
intention is to make the outputs generic enough to serve other uses as
well. Each utility has a D3 example template, which it can use to
generate a self-contained html file. It can also generate csv or json
output, and there is a [worked example](#user-content-exploring-d3-examples) of how
to use csv in a pre-existing D3 chart.

The d3graph.py utility was originally added to the twarc repo as
directed.py but is moving here for consistency.

**Requirements**

* dateutil - `python-dateutil`
* pytz - `pip install pytz`
* tzlocal - `pip install tzlocal`

## D3 visualizations

Some utilities to generate [D3](http://d3js.org/) visualizations of aspects of a collection
of tweets are provided. Use "--output=json" or "--output=csv" to output the data for use with 
other D3 examples, or "--help" for other options.

### d3graph.py

A directed graph of mentions or retweets, in which nodes are users and
arrows point from the original user to the user who mentions or retweets
them:

    % d3graph.py --mode mentions nasa-20130306102105.json > nasa-directed-mentions.html
    % d3graph.py --mode retweets nasa-20130306102105.json > nasa-directed-retweets.html
    % d3graph.py --mode replies nasa-20130306102105.json > nasa-directed-replies.html
    
### d3cotag.py

An undirected graph of co-occurring hashtags:

    % d3cotag.py nasa-20130306102105.json > nasa-cotags.html
    
A threshold can be specified with -t: hashtags whose number of
occurrences falls below this will not be linked. Instead, if -k is set,
they will be replaced with the pseudo-hashtag "-OTHER". Hashtags can be
excluded with -e (takes a comma-delimited list). If the tweets were
harvested by a search for a single hashtag then it's a good idea to
exclude that tag, since every other tag will link to it.
    
### d3timebar.py

A bar chart timeline with arbitrary intervals, here five minutes:

    % d3times.py -a -t local -i 5M nasa-20130306102105.json > nasa-timebargraph.html

[Examples](https://wallandbinkley.com/twarc/bill10/)

The output timezone is specified by -t; the interval is specified by -i,
using the [standard
abbreviations](https://docs.python.org/2/library/time.html#time.strftime
): seconds = S, minutes = M, hours = H, days = d, months = m, years = Y.
The example above uses five-minute intervals. Output may be aggregated
using -a: each row has a time value and a count. Note that if you are
generating the embedded example, you must use -a.

## Exploring D3 Examples

The json and csv outputs can be used to view your data in D3 example
visualizations with minimal fuss. There are many many examples to be
explored; Mike Bostock's
[Gallery](https://github.com/mbostock/d3/wiki/Gallery) is a good place
to start. Here's a worked example, using Bostock's [Zoomable Timeline
Area
Chart](http://mbostock.github.io/d3/talk/20111018/area-gradient.html).
It assumes no knowledge of D3.

First, look at the data input. In line 137 this example loads a csv file 

    d3.csv("flights-departed.csv", function(data) {

The [csv file](http://mbostock.github.io/d3/talk/20111018/flights-departed.csv) looks like this: 

    date,value
    1988-01-01,12681
    ...

We can easily generate a csv file that matches that format:

    % ./d3times.py -a -i 1d -o csv

(I.e. aggregate, one-day interval, output csv). We then just need to edit the
output to make the column headers match the original csv,
i.e. change them to "date,value".

We also need to check the way the example loads scripts and css assets,
especially the D3 library. In this case it expects a local copy:

    <script type="text/javascript" src="d3/d3.js"></script>
    <script type="text/javascript" src="d3/d3.csv.js"></script>
    <script type="text/javascript" src="d3/d3.time.js"></script>
    <link type="text/css" rel="stylesheet" href="style.css"/>
    
Either change those links to point to the original location, or save a
local copy. (Note that if you're going to put your example online you'll
want local copies of scripts, since the [same-origin policy](https://en.wikipedia.org/wiki/Same-origin_policy) 
will prevent them from being loaded from the source).

Once you've matched your data to the example and made sure it can load the
D3.js library, the example may work. In this case it doesn't - it shows
an empty chart. The title "U.S. Commercial Flights, 1999-2001" and the
horizontal scale explain why: it expects dates within a certain
(pre-Twitter) range, and the x domain is hard-coded accordingly. The
setting is easy to find, in line 146:

    x.domain([new Date(1999, 0, 1), new Date(2003, 0, 0)]);
    
Change those dates to include the date range of your data, and the
example should work. Don't worry about matching your dates closely: the
chart is zoomable, after all.

A typical Twarc harvest gets you a few days worth of tweets, so the
day-level display of this example probably isn't very interesting. We're
not bound by the time format of the example, however. We can see it in
line 63:

    parse = d3.time.format("%Y-%m-%d").parse,
    
We can change that to parse at the minute interval: "%Y-%m-%d %H:%M",
and generate our csv at the same interval with "-i 1M". With those
changes we can zoom in until bars represent a minute's worth of tweets.

This example doesn't work perfectly: I see some odd artifacts around the
bottom of the chart, as if the baseline were slightly above the x axis
and small values are presented as negative. And it doesn't render in
Chrome at all (Firefox and Safari are fine). The example is from 2011
and uses an older version of the D3 library, and with some tinkering it
could probably be updated and made functional. It serves to demonstrate,
though, that only small changes and no knowledge of the complexities of D3 
are needed to fit your data into an existing D3 example.

## Adding Scripts

The heart of twarc-report is the Profiler class in profiler.py. The
scripts pass json records from the twarc harvests to this class, and it
tabulates some basic properties: number of tweets and authors, earliest
and latest timestamp, etc. The scripts create their own profilers that
inherit from this class and that process the extra fields etc. needed by
the script. To add a new script, start by working out its profiler class
to collect the data it needs from each tweet in the process() method,
and to organize the output in the report() method.

The various output formats are generated by functions in d3output.py. 

License
-------

* CC0

