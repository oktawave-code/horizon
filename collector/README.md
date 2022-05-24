Routing syntax
==============
Each route is defined by four values:
* "source" declares which incoming http header field should be used
to match for that particular route. Special case here is string "url"
which points to url used
* "filter" is a regexp match, that must succeed for the rule to take effect.
Capturing groups can be used here, and referenced later in "topic" field as
"$n" tokens.
* "topic" names the topic that message should be sent to. Parts of
the "filter" match can be used here.
* "final" is a binary switch, telling the code to stop processing further
rules if this one matched.

If no route matched after processing entire list, message gets sent to
"unroutedTopic", so simplest use case is to define empty rules list
and just single topic in "unroutedTopic".

Golang regexp syntax can be found here: https://golang.org/pkg/regexp/syntax/

Special cases
-------------
* If "source" is missing, then "filter" must be empty too, and "topic" is
required (such route matches all messages and blindly forwards them to
"topic")
* If "filter" is missing, it is assumed to be ".*" (which matches all
characters)
* If "topic" is missing, it is assumed to be "$0" (which means whole string
matched by "filter")

Examples
--------
| source   | filter               | topic     | final |                                                                                                                   |
|----------|----------------------|-----------|-------|-------------------------------------------------------------------------------------------------------------------|
| X-Num    | ^[0-9]+$             | t-$0      |       | Pull data from http "X-Num" header, match only when it is a number, sent to topic with name "t-" plus that number |
| X-XXX    | (X+)                 | $1        |       | Get data from "X-XXX" header, match only if it contains "X" characters sequence, sent to topic with that seqence  |
| url      | \\.html$             | test      | V     | All requests with url ending with ".html" will be sent to "test" topic, no more rules checked if this one matched |
|          |                      | backup    |       | Everything will be sent to "backup" topic (unless it matched previous rule and checking was stopped)              |
| X-Topic  | ^(alpha\|beta\|test) | $1        |       | Requests with header "X-Topic" starting with "alpha", "beta" or "test" will be send to corresponding topics       |

Metadata syntax
===============
This one is much simpler - just a list of from/to pairs:
* "source" points to an incoming http header (or "url", just like for
routing)
* "meta" names a destination metadata field in kafka message

Empty list is okay here.

TODO
====
* debug mode which accepts some predefined tokens?
* remove automatic topic creation?
* better logging
* add support for HEAD (required by HTTP spec)
* set timeout for TLS connections with idserver
* make sure to avoid memory copying
* add simple self monitoring?
