BettingOnTrumpTweets
==============================

### TL;DR of the Project

The top-line objective for this project was to a) create a smart forecast for the volume of tweets Trump would make in a given time period, and b) use that refined expectation to identify EV-positive trading opportunities on the PredictIt Tweet Volume markets.  I succeeded: I made about a 150% return over about 50 bets in the few weeks that the project was live but prior to PredictIt shutting down the tweet markets.

While I have a background in strategy analytics from my Consulting days, this was my first off-the-shelf Python project.  It was structured badly.  Please forgive me.  That said, I was able to practice a ton of skills so I consider it a success:

* Web scraping.  Ultimately using Tweepy, but that was only after my adventures with Beautiful Soup hit up against Twitter systems admin protections
* Using web APIs.  In part through Tweepy above, but also as a way to automate data gathering for PredictIt's various markets
* Connecting python scripts with SQL databases.  After downloading a bundle of tweets from a given politician, the tweets were stored in a SQL database that was then used for downstream purposes
* Publishing content on the web using Dash.  The end result of all of the work was a dashboard of historic and forecast tweets that helped inform me whether now would be a good time to trade into or out of positions
* Soup-to-nuts real-time model pipeline.  As I mentioned above, the structure of the project was garbage, but I automated all of the steps for real-time modeling, from data gathering and processing to model fitting.

Note: the key point of differentiation between the way my model projected tweet volume compared to other approaches I saw on the internet came down to my understanding that different time periods drive different output behaviors.  Most of the sources I found online presumed a linear extrapolation of tweet volume (if we are 20% of the way into the market, presume that the end tweet volume will be 5x current volume).

However, my research was premised that Trump tweeted at different times: he was a morning tweeter and an evening tweeter; a tweetstorm today was a relatively poor predictor of a tweetstorm tomorrow; he didn't tweet on weekends when he was golfing or when he was traveling internationally, etc.  All of these dynamics allowed me to more narrowly refine my forecast compared to the lion's share of extrapolation traders.

### Preliminary View of the Dash Web Dashboard

Note: with Trump kicked off of twitter and with the PredictIt tweet markets shutting down, I stopped keeping the Heroku server running the tweetbot active.  I just spun up the dev environment with the data I had readily available to reproduce a near-final version of the dashboard.

![Dash Dashboard](https://github.com/weswest/BettingOnTrumpTweets/blob/master/references/Trump%20Tweet%20Screenshot.png)

### Background and Motivation

Prior to getting kicked off of Twitter, President Trump was known as a tweet machine.  Given his position of authority, his tweets had the impact to materially shape the discourse of the day, and political pundits followed his tweeting habits carefully.

His tweeting became such a sensation that folks started betting on his tweets.  [PredictIt.org](https://www.predictit.org/), a political betting site run out of New Zealand, really got into the action, running weekly markets where traders bought and sold based on the expected volume of tweets from Mr President for that week.  Pulling up a [random tweet market](https://www.predictit.org/markets/detail/6400/How-many-tweets-will-@realDonaldTrump-post-from-noon-Feb-5-to-12) shows over $1mm traded hands in a single week between Feb 5, 2020 through Feb 12, 2020.  If you bet that Trump would tweet between 270-279 times that week, you won; otherwise, you lost.

The structure of PredictIt betting markets is fascinating overall, but in short folks can buy and sell positions from the start of the market until the close.  In the market above, plenty of folks scored big by holding 270-279 to the end of the market, but folks also made money by buying the 260-269 bracket when it seemed unlikely and then selling at a higher price when it seemed more likely.

PredictIt expanded its tweet markets to the other Trump handles (e.g., the official White House twitter handle), and then expanded to other politicians.  It was a huge moneymaker for them, and I wouldn't be surprised if it's one of the reasons they lost their charter.  But that's an issue for another day.

Websites cropped up that tracked tweet volumes and produced a simplistic set of dashboards that presumed tweet volumes were consistent.  These websites posited a linear extrapolation of tweets: if the market - which ran from Noon Wednesday to Noon Wednesday - was 1/3 over, then take his current tweet volume through the week and multiply by 3 to get the "expected" volume of tweets.

Like I said, millions of dollars were trading hands based on these insights.  I have a background in time series forecasting so I understand seasonality and idiosyncratic events and all sorts of things that challenge the premise that tomorrow's behavior can be really different from yesterday's behavior.  I set out to build a better tweet bot.

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
