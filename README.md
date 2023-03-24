# PD

Simple script to read and group PagerDuty Incidents

### Setup

Add a Pagerduty API key to `~/.pd.toml` or use flag `--key='<your key>'`

### Optional Config file

A config file can be provided at `~/.pd.toml`

Format is: 
```toml
#Required
[pagerduty]
api_token="xxxyyyzzzaaabbbccc"

#Optional
[confluence]
user_email="bob@example.com"
api_token="<your Confluence key>"
space_key="<The Confluence Space key where you want to create documents>"

```



### Help

`./pd.py -h`

### Flags


--help (-h)        Show this help message

--teams (-t)       Pagerduty Team IDs, comma separated

--services (-s)    Pagerduty Service IDs, comma separated

--logs (-l)        Read log entries for each incident

--notes (-n)       Read notes for each incident

--key (-k)         PagerDuty API key - defaults to looking for a ~/.pd.toml file

--csv (-c)         Output as csv

--group (-g)       Group by field, e.g. --group="description"

--fuzz (-z)        Fuzz matching on grouping

--fuzz-score (-m)  Fuzz matching threshold - default is 90%

--full (-f)        Full descriptions, default is to shorten

--debug (-x)       Debug output

--report (-r)      Output full report

--confluence (-w)  Create a page in Confluence with the results [Not implemented]

### Examples

Show incidents for a team and service.

`./pd --teams=PXXXXX --services=P2APAXX 2022-10-25`

'Full' report on a couple of teams/services. Parse the logs for acknowledger names, full descriptions in output, fuzzy match descriptions when grouping 

`./pd -t PXXXXX,PXXXXY -s P2APAXX,P2APAXY --report -l -f -z 2023-03-2`

[Super simple implementation] create a doc in Confluence with grouped incidents

`./pd -t PXXXXX --format=confluence -l -f -z --group="Description" 2023-03-08`