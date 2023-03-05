# PD

Simple script to read and group PagerDuty Incidents

### Setup

Add a Pagerduty API key to `~/.pd.toml` or use flag `--key='<your key>'`

### Optional Config file

A config file can be provided at `~/.pd.toml`

Format is: 
```toml
[pagerduty]
api_token="xxxyyyzzzaaabbbccc"
```

### Help

`./pd.py -h`

### Example

`./pd.py --team=PSYEN6X --service=P2APASH --report 2022-10-25`
