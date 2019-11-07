from string import Template

# Link for accessing all scores of contest, in JSON format.
HACKERRANK_LINK = Template(
    "https://www.hackerrank.com/rest/contests/"
    "${contest_name}/"
    "leaderboard?offset=${offset}&limit=${limit}"
    "&_=1489594857572"
)
