from string import Template

# Link for accessing all scores of contest, in JSON format.
HACKERRANK_CONTEST_LINK = Template(
    "https://www.hackerrank.com/rest/contests/"
    "${contest_name}"
)

HACKERRANK_LEADERBOARD_LINK = Template(
    "https://www.hackerrank.com/rest/contests/"
    "${contest_name}/"
    "leaderboard?offset=${offset}&limit=${limit}"
    "&_=1489594857572"
)
