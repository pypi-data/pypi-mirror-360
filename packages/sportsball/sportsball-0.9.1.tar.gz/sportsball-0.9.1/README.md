# sportsball

<a href="https://pypi.org/project/sportsball/">
    <img alt="PyPi" src="https://img.shields.io/pypi/v/sportsball">
</a>

A library for pulling in and normalising sports stats.

<p align="center">
    <img src="sportsball.png" alt="sportsball" width="200"/>
</p>

## Dependencies :globe_with_meridians:

Python 3.11.6:

- [pandas](https://pandas.pydata.org/)
- [requests](https://requests.readthedocs.io/en/latest/)
- [requests-cache](https://requests-cache.readthedocs.io/en/stable/)
- [python-dateutil](https://github.com/dateutil/dateutil)
- [tqdm](https://github.com/tqdm/tqdm)
- [beautifulsoup](https://www.crummy.com/software/BeautifulSoup/)
- [openpyxl](https://openpyxl.readthedocs.io/en/stable/)
- [joblib](https://joblib.readthedocs.io/en/stable/)
- [pyarrow](https://arrow.apache.org/docs/python/index.html)
- [ipython](https://ipython.org/)
- [pytz](https://pythonhosted.org/pytz/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [geocoder](https://geocoder.readthedocs.io/)
- [retry-requests](https://github.com/bustawin/retry-requests)
- [timezonefinder](https://timezonefinder.michelfe.it/gui)
- [nba_api](https://github.com/swar/nba_api)
- [pydantic](https://docs.pydantic.dev/latest/)
- [flatten_json](https://github.com/amirziai/flatten)
- [pygooglenews](https://github.com/kotartemiy/pygooglenews)
- [extruct](https://github.com/scrapinghub/extruct)
- [wikipedia-api](https://github.com/martin-majlis/Wikipedia-API)
- [tweepy](https://www.tweepy.org/)
- [pytest-is-running](https://github.com/adamchainz/pytest-is-running)
- [PySocks](https://github.com/Anorov/PySocks)
- [func-timeout](https://github.com/kata198/func_timeout)
- [tenacity](https://github.com/jd/tenacity)
- [random_user_agent](https://github.com/Luqman-Ud-Din/random_user_agent)
- [wayback](https://github.com/edgi-govdata-archiving/wayback)
- [cryptography](https://cryptography.io/en/latest/)
- [feedparser](https://github.com/kurtmckee/feedparser)
- [dateparser](https://dateparser.readthedocs.io/en/latest/)
- [playwright](https://playwright.dev/)
- [cchardet](https://github.com/PyYoshi/cChardet)
- [lxml](https://lxml.de/)
- [gender-guesser](https://github.com/lead-ratings/gender-guesser)
- [scrapesession](https://github.com/8W9aG/scrapesession)
- [pyhigh](https://github.com/sgherbst/pyhigh)

## Raison D'être :thought_balloon:

`sportsball` aims to be a library for pulling in historical information about previous sporting games in a standardised fashion for easy data processing.
The models it uses are designed to be used for many different types of sports.

The supported leagues are:

* 🏉 [AFL](https://www.afl.com.au/)
* 🐎 [HKJC](https://www.hkjc.com/home/english/index.aspx)
* 🏀 [NBA](https://www.nba.com/)
* 🏀 [NCAAB](https://www.ncaa.com/sports/basketball-men/d1)
* 🏈 [NCAAF](https://www.ncaa.com/sports/football/fbs)
* 🏈 [NFL](https://www.nfl.com/)

## Architecture :triangular_ruler:

`sportsball` is an object orientated library. The entities are organised like so:

* **Game**: A game within a season.
    * **Team**: The team within the game. Note that in games with individual players a team exists as a wrapper.
        * **Player**: A player within the team.
            * **Address**: The address information of a players birth.
            * **Owner**: The owner of the player.
            * **Venue**: The college of the player.
        * **Odds**: The odds for the team to win the game.
            * **Bookie**: The bookie publishing the odds.
        * **News**: News about the team the day before the game.
        * **Social**: Social posts from the team the day before the game.
        * **Coach**: A coach for the team.
    * **Venue**: The venue the game was played in.
        * **Address**: The address information of a venue.
            * **Weather**: The weather at the address.
    * **Dividend**: The dividends the game pays out.

### Objects

A list of the attributes on each object.

#### Game

A representation of the game within a season.

* **dt**: The timezone aware date/time of the game start.
* **week**: The round of the game within the season.
* **game_number**: The index of the game within the round.
* **venue**: The venue the game took place at.
* **teams**: A list of teams within the game.
* **home_team**: The team representing the home team.
* **away_team**: The ream representing the away team.
* **end_dt**: The timzone aware date/time of the game end.
* **attendance**: How many people attended the game.
* **league**: The league the game belongs to.
* **year** The year the game was in.
* **season_type**: The type of the season the game was played in.
* **postponed**: Whether the game was postponed.
* **playoff**: Whether the game was a playoff game.
* **distance**: The distance the game was played over.
* **version**: The version of the game model.

#### Team

A representation of a team within a game.

* **identifier**: The unique identifier for the team.
* **name**: The name of the team.
* **location**: The home location of the team.
* **players**: A list of players with the team for the game.
* **odds**: A list of odds for the team on the game to win.
* **points**: The amount of points scored by this team on the game.
* **ladder_rank**: The ladder rank of the team at the beginning of the round of the game.
* **kicks**: The number of kicks a team produced.
* **news**: News articles about the team a day from the game.
* **social**: Social media posts from the team a day from the game.
* **field_goals**: The sum of the field goals made by the team in the game.
* **field_goals_attempted**: The sum of the field goals attempted by the team in the game.
* **offensive_rebounds**: The number of rebounds during offense by the team in the game.
* **assists**: The number of times the player on the team made a pass that resulted in a field goal in the game.
* **turnovers**: The number of times a player on the team loses possession of the ball in the game.
* **marks**: The number of times a player on the team marks the ball in the game.
* **handballs**: The number of times a player on the team handballs the ball in the game.
* **disposals**: The number of times a player on the team disposes of the ball in the game.
* **goals**: The number of times a player on the team scored a goal in the game.
* **behinds**: The number of times a player on the team scored a behind in the game.
* **hit_outs**: The number of times a player on the team hit out the ball in the game.
* **tackles**: The number of times a player on the team tackled another player in the game.
* **rebounds**: The number of times a player on the team gets a rebound in the game.
* **insides**: The number of times a player on the team kicks a ball inside 50 in the game.
* **clearances**: The number of times a player on the team performs a clearance in the game.
* **clangers**: The number of times a player on the team performs a clanger in the game.
* **free_kicks_for**: The number of times a player on the team was rewarded a free kick in the game.
* **free_kicks_against**: The number of times a player on the team gave a player on the other team a free kick in the game.
* **brownlow_votes**: The number of times a player on the team was given a brownlow vote in the game.
* **contested_possessions**: The number of times a player on the team got a contested posession in the game.
* **uncontested_possessions**: The number of times a player on the team got an uncontested posession in the game.
* **contested_marks**: The number of times a player on the team got a contested mark in the game.
* **marks_inside**: The number of times a player on the team got a mark inside 50 in the game.
* **one_percenters**: The number of times a player on the team performs a "one-percenter" in the game.
* **bounces**: The number of times a player on the team bounces a ball.
* **goal_assists**: The number of times a player on the team assists another player on the team with a goal in the game.
* **coaches**: The coaches on the team during the game.
* **lbw**: Length behind winner, expressed in metres.
* **dividends**: The dividends the game pays out.
* **field_goals_percentage**: The ratio of field goals scored by field goals attempted by the players on the team in the game.
* **three_point_field_goals**: The number of three point field goals scored by the players on the team in the game.
* **three_point_field_goals_attempted**: The number of three point field goals attempted by the players on the team in the game.
* **three_point_field_goals_percentage**: The ratio of three point field goals scored by the three point field goals attempted by the players on the team in the game.
* **free_throws**: The number of free throws scored by the players on the team in the game.
* **free_throws_attempted**: The number of free throws attempted by the players on the team in the game.
* **free_throws_percentage**: The ratio of free throws scored by the free throws attempted by the players on the team in the game.
* **defensive_rebounds**: The number of defensive rebounds made by the players on the team in the game.
* **total_rebounds**: The number of offensive and defensive rebounds made by the players on the team in the game.
* **steals**: The number of steals made by the players on the team in the game.
* **blocks**: The number of blocks made by the players on the team in the game.
* **personal_fouls**: The number of personal fouls made by the players on the team in the game.
* **version**: The version of the team model.

#### Player

A representation of a player within a team within a game.

* **identifier**: The unique identifier for the player.
* **jersey**: The jersey identifying the player.
* **kicks**: The number of kicks the player made in the game.
* **fumbles**: The number of times the player fumbled the ball in the game.
* **fumbles_lost**: The number of times the player loses possession of the ball due to a fumble and the opposing team recovers the ball.
* **field_goals**: The number of field goals the player made in the game.
* **field_goals_attempted**: The number of field goal attempts the player made in the game.
* **offensive_rebounds**: The number of rebounds during offense by the player made in the game.
* **assists**: The number of times the player made a pass that resulted in a field goal in the game.
* **turnovers**: The number of times a player loses possession of the ball in the game.
* **name**: The name of the player.
* **marks**: The number of marks the player performed in the game.
* **handballs**: The number of handballs the player performed in the game.
* **disposals**: The number of disposals the player performed in the game.
* **goals**: The number of goals scored by the player in the game.
* **behinds**: The number of behinds scored by the player in the game.
* **hit_outs**: The number of hit outs scored by the player in the game.
* **tackles**: The number of tackles performed by the player in the game.
* **rebounds**: The number of rebounds performed by the player in the game.
* **insides**: The number of insides performed by the player in the game.
* **clearances**: The number of clearances performed by the player in the game.
* **clangers**: The number of clangers performed by the player in the game.
* **free_kicks_for**: The number of free kicks given to the player in the game.
* **free_kicks_against**: The number of free kicks given against an action taken by the player in the game.
* **brownlow_votes**: The number of votes for the brownlow medal the player has in the current season.
* **contested_possessions**: The number of possessions the player had in the game that were contested.
* **uncontested_possessions**: The number of posessions the player had in the game that were uncontested.
* **contested_marks**: The number of marks the player had in the game that were contested.
* **marks_inside**: The number of marks the player had in the game inside the 50.
* **one_percenters:** The number of times the player spoils, knock-ons, smothers or shepherds the ball during the game.
* **bounces**: The number of bounces the player makes in the game.
* **goal_assists**: The number of assists on goal the player had in the game.
* **percentage_played**: The percentage of the game the player was on the field.
* **birth_date**: The birth date of the player.
* **species**: The species of the player.
* **handicap_weight**: The handicap weight of the player (in KGs).
* **father**: The player representing the father of the player.
* **sex**: The sex of the player.
* **age**: The age of the player in years.
* **starting_position**: The starting position of the player.
* **weight**: The weight of the player (in KGs).
* **birth_address**: The address model for the players birth location.
* **seconds_played**: The amount of seconds the player played the game for.
* **field_goals_percentage**: The ratio of field goals scored by field goals attempted for the player during the game.
* **three_point_field_goals**: The number of three point field goals scored by the player during the game.
* **three_point_field_goals_attempted**: The number of three point field goals attempted by the player during the game.
* **three_point_field_goals_percentage**: The ratio of three point field goals scored by three point field goals attempted by the player during the game.
* **free_throws**: The number of free throws scored by the player during the game.
* **free_throws_attempted**: The number of free throws attempted by the player during the game.
* **free_throws_percentage**: The ratio of free throws scored by free throws attempted by the player during the game.
* **defensive_rebounds**: The number of defensive rebounds made by the player during the game.
* **total_rebounds**: The number of rebounds (both offensive and defensive) made by the player during the game.
* **steals**: The number of steals made by the player during the game.
* **blocks**: The number of blocks made by the player during the game.
* **personal_fouls**: The number of personal fouls made by the player during the game.
* **points**: The points made by the player during the game.
* **game_score**: The [John Hollinger game score](https://www.nbastuffer.com/analytics101/game-score/) of the player during the game.
* **point_differential**: The points scored by the players team while the player was on the court minus the points scored by the opposing team when the player is off the court.
* **version**: The version of the player model.
* **height**: The height of the player in (in CMs).
* **college**: The college the player went to.
* **headshot**: An image URL representing the headshot of the player.
* **forced_fumbles**: The number of forced fumbles made by the player during the game.
* **fumbles_recovered**: The number of fumbles recovered made by the player during the game.
* **fumbles_recovered_yards**: The yards gained during fumbles recovered by the player during the game.
* **fumbles_touchdowns**: The number of fumble touchdowns made by the player during the game.
* **offensive_two_point_returns**: The number of offensive two point returns made by the player during the game.
* **offensive_fumbles_touchdowns**: The number of offensive fumbles touchdowns made by the player during the game.
* **defensive_fumbles_touchdowns**: The number of defensive fumbles touchdowns made by the player during the game.
* **average_gain**: The average number of yards gained by the player during the game.
* **completion_percentage**: The completion percentage of the player during the game.
* **completions**: The number of completions made by the player during the game.
* **espn_quarterback_rating**: The number of ESPN quarterback rating of the player.
* **interception_percentage**: The interception percentage of the player during the game.
* **interceptions**: The number of interceptions made by the player during the game.
* **long_passing**: The number of long passes made by the player during the game.
* **misc_yards**: The miscellaneous yards gained by the player during the game.
* **net_passing_yards**: The total passing yards gained by the player during the game.
* **net_total_yards**: The net total yards gained by the player during the game.
* **passing_attempts**: The number of attempted passes made by the player during the game.
* **passing_big_plays**: The number of passes that led to big plays made by the player during the game.
* **passing_first_downs**: The number of passes first downs made by the player during the game.
* **passing_fumbles**: The number of passing fumbles made by the player during the game.
* **passing_fumbles_lost**: The number of passing fumbles lost by the player during the game.
* **passing_touchdown_percentage**: The percentage of passing touchdowns by the player during the game.
* **passing_touchdowns**: The number of passing touchdowns made by the player during the game.
* **passing_yards**: The yards gained by the player during passing during the game.
* **passing_yards_after_catch**: The yards gained by the player after passing after a catch during the game.
* **passing_yards_at_catch**: The yards gained by the player after passing before a catch during the game.
* **quarterback_rating**: The quarterback rating of the player.
* **sacks**: The number of sacks made by the player during the game.
* **sacks_yards_lost**: The yards lost by the player performing a sack during the game.
* **net_passing_attempts**: The number of passing attempts made by the player during the game.
* **total_offensive_plays**: The number of offensive plays made by the player during the game.
* **total_points**: The number of points made by the player during the game.
* **total_touchdowns**: The number of touchdowns made by the player during the game.
* **total_yards**: The total yards gained by the player during the game.
* **total_yards_from_scrimmage**: The total yards gained by the player from scrimmage during the game.
* **two_point_pass**: The two point passes made by the player during the game.
* **two_point_pass_attempt**: The attempts at two point passes made by the player during the game.
* **yards_per_completion**: The yards gained per completion by the player during the game.
* **yards_per_pass_attempt**: The yards gained per pass attempt by the player during the game.
* **net_yards_per_pass_attempt**: The net number of yards gained per pass attempt by the player during the game.
* **long_rushing**: The long rushes made by the player during the game.
* **rushing_attempts**: The attempted rushes made by the player during the game.
* **rushing_big_plays**: The rushes resulting in big plays made by the player during the game.
* **rushing_first_downs**: The rushing first downs made by the player during the game.
* **rushing_fumbles**: The rushing fumbles made by the player during the game.
* **rushing_fumbles_lost**: The rushing fumbles lost by the player during the game.
* **rushing_touchdowns**: The rushing touchdowns made by the player during the game.
* **rushing_yards**: The yards made by rushing by the player during the game.
* **stuffs**: The stuffs made by the player during the game.
* **stuff_yards_lost**: The yards lost while stuffing by the player during the game.
* **two_point_rush**: The number of two point rushes made by the player during the game.
* **two_point_rush_attempts**: The number of attempted two point rushes made by the player during the game.
* **yards_per_rush_attempt**: The number of yards per rush attempt made by the player during the game.
* **espn_widereceiver**: The ESPN rating for the wide receiver.
* **long_reception**: The number of long receptions made by the player during the game.
* **receiving_big_plays**: The number of receives that resulted in big plays made by the player during the game.
* **receiving_first_downs**: The number of first down receives made by the player during the game.
* **receiving_fumbles**: The number of fumble receives made by the player during the game.
* **receiving_fumbles_lost**: The number of fumble receives lost by the player during the game.
* **receiving_targets**: The number of target receives made by the player during the game.
* **receiving_yards**: The number of yards gained by receives by the player during the game.
* **receiving_yards_after_catch**: The number of yards gained by receives by the player during the game after a catch.
* **receiving_yards_at_catch**: The number of yards gained by the receives by the player during the game at a catch.
* **receptions**: The number of receptions made by the player during the game.
* **two_point_receptions**: The number of two point receptions made by the player during the game.
* **two_point_reception_attempts**: The number of two point reception attempts made by the player during the game.
* **yards_per_reception**: The yards gained on average per reception by the player during the game.
* **assist_tackles**: The number of assist tackles made by the player during the game.
* **average_interception_yards**: The average number of yards gained by an interception made by the player during the game.
* **average_sack_yards**: The average number of yards gained by a sack made by the player during the game.
* **average_stuff_yards**: The average number of yards gained by a stuff made by the player during the game.
* **blocked_field_goal_touchdowns**: The number of blocked field goal touchdowns made by the player during the game.
* **blocked_punt_touchdowns**: The number of blocked punt touchdowns made by the player during the game.
* **defensive_touchdowns**: The number of defensive touchdowns made by the player during the game.
* **hurries**: The number of hurries made by the player during the game.
* **kicks_blocked**: The number of kicks blocked by the player during the game.
* **long_interception**: The number of long interceptions made by the player during the game.
* **misc_touchdowns**: The number of miscellaneous touchdowns made by the player during the game.
* **passes_batted_down**: The number of passes batted down by the player during the game.
* **passes_defended**: The number of passes defended by the player during the game.
* **quarterback_hits**: The number of quarterback hits made by the player during the game.
* **sacks_assisted**: The number of sacks the player assisted with during the game.
* **sacks_unassisted**: The number of sacks the player made unassisted during the game.
* **sacks_yards**: The number of yards gained by the player making a sack during the game.
* **safeties**: The safeties made by the player during the game.
* **solo_tackles**: The number of solo tackles made by the player during the game.
* **stuff_yards**: The yards gained by the stuffs made by the player during the game.
* **tackles_for_loss**: The tackles for losses made by the player during the game.
* **tackles_yards_lost**: The yards lost by tackles made by the player during the game.
* **yards_allowed**: The yards allowed to be gained by the player during the game.
* **points_allowed**: The points allowed to be gained by the player during the game.
* **one_point_safeties_made**: The one point safeties made by the player during the game.
* **missed_field_goal_return_td**: The missed field goal return TD made by the player during the game.
* **blocked_punt_ez_rec_td**: The blocked punt EZ rec TD of the player during the game.
* **interception_touchdowns**: The number of interception touchdowns made by the player during the game.
* **interception_yards**: The number of yards gained by interceptions made by the player during the game.
* **average_kickoff_return_yards**: The average number of kickoff return yards made by the player during the game.
* **average_kickoff_yards**: The average number of kickoff yards made by the player during the game.
* **extra_point_attempts**: The number of extra point attempts made by the player during the game.
* **extra_point_percentage**: The number of extra point percentages made by the player during the game.
* **extra_point_blocked**: The number of extra points blocked by the player during the game.
* **extra_points_blocked_percentage**: The percentage of extra points blocked by the player during the game.
* **extra_points_made**: The number of extra points made by the player during the game.
* **fair_catches**: The number of fair catches made by the player during the game.
* **fair_catch_percentage**: The percentage of fair catches made by the player during the game.
* **field_goal_attempts_max_19_yards**: The field goal attempts between 0-19 yards made by the player during the game.
* **field_goal_attempts_max_29_yards**: The field goal attempts between 19-29 yards made by the player during the game.
* **field_goal_attempts_max_39_yards**: The field goal attempts between 29-39 yards made by the player during the game.
* **field_goal_attempts_max_49_yards**: The field goal attempts between 39-49 yards made by the player during the game.
* **field_goal_attempts_max_59_yards**: The field goal attempts between 49-59 yards made by the player during the game.
* **field_goal_attempts_max_99_yards**: The field goal attempts between 59-99 yards made by the player during the game.
* **field_goal_attempts_above_50_yards**: The field goal attempts above 50 yards made by the player during the game.
* **field_goal_attempt_yards**: The yards gained by field goal attempts made by the player during the game.
* **field_goals_blocked**: The field goals blocked by the player during the game.
* **field_goals_blocked_percentage**: The percentage of field goals made by the player during the game.
* **field_goals_made**: The number of field goals made by the player during the game.
* **field_goals_made_max_19_yards**: The number of field goals made between 0-19 yards by the player during the game.
* **field_goals_made_max_29_yards**: The number of field goals made between 19-29 yards by the player during the game.
* **field_goals_made_max_39_yards**: The number of field goals made between 29-39 yards by the player during the game.
* **field_goals_made_max_49_yards**: The number of field goals made between 39-49 yards by the player during the game.
* **field_goals_made_max_59_yards**: The number of field goals made between 49-59 yards by the player during the game.
* **field_goals_made_max_99_yards**: The number of field goals made between 59-99 yards by the player during the game.
* **field_goals_made_above_50_yards**: The number of field goals made over 50 yards by the player during the game.
* **field_goals_made_yards**: The number of yards gained by field goals made by the player during the game.
* **field_goals_missed_yards**: The number of yards gained by missed field goals made by the player during the game.
* **kickoff_out_of_bounds**: The number of out of bounds kickoffs made by the player during the game.
* **kickoff_returns**: The number of kickoff returns made by the player during the game.
* **kickoff_returns_touchdowns**: The number of kickoff returns touchdowns made by the player during the game.
* **kickoff_return_yards**: The yards gained by kickoff returns made by the player during the game.
* **long_field_goal_attempt**: The number of long field goal attempts made by the player during the game.
* **long_field_goal_made**: The number of long field goals made by the player during the game.
* **long_kickoff**: The number of long kickoffs made by the player during the game.
* **total_kicking_points**: The number of kicking points made by the player during the game.
* **touchback_percentage**: The percentage of touchbacks made by the player during the game.
* **touchbacks**: The touchbacks made by the player during the game.
* **defensive_fumble_returns**: The number of defensive fumble returns made by the player during the game.
* **defensive_fumble_return_yards**: The yards gained by defensive fumble returns made by the player during the game.
* **fumble_recoveries**: The fumble recoveries made by the player during the game.
* **fumble_recovery_yards**: The yards gained by fumble recoveries made by the player during the game.
* **kick_return_fair_catches**: The kick return fair catches made by the player during the game.
* **kick_return_fair_catch_percentage**: The percentage of kick return fair catches made by the player during the game.
* **kick_return_fumbles**: The kick return fumbles made by the player during the game.
* **kick_return_fumbles_lost**: The kick return fumbles lost by the player during the game.
* **kick_returns**: The kick returns made by the player during the game.
* **kick_return_touchdowns**: The kick return touchdowns made by the player during the game.
* **kick_return_yards**: The yards gained by kick returns made by the player during the game.
* **long_kick_return**: The long kick returns made by the player during the game.
* **long_punt_return**: The long punt returns made by the player during the game.
* **misc_fumble_returns**: The miscellaneous fumble returns made by the player during the game.
* **misc_fumble_return_yards**: The yards gained by miscellaneous fumble returns made by the player during the game.
* **opposition_fumble_recoveries**: The opposition fumble recoveries made by the player during the game.
* **opposition_fumble_recovery_yards**: The yards gained by opposition fumble recoveries made by the player during the game.
* **opposition_special_team_fumble_returns**: The opposition special team fumble returns made by the player during the game.
* **opposition_special_team_fumble_return_yards**: The opposition special team fumble return yards made by the player during the game.
* **punt_return_fair_catches**: The number of punt return fair catches made by the player during the game.
* **punt_return_fair_catch_percentage**: The percentage of punt return fair catches made by the player during the game.
* **punt_return_fumbles**: The number of punt return fumbles made by the player during the game.
* **punt_return_fumbles_lost**: The number of punt return fumbles lost by the player during the game.
* **punt_returns**: The number of punt returns made by the player during the game.
* **punt_returns_started_inside_the_10**: The number of punt returns started inside the 10 yard line by the player during the game.
* **punt_returns_started_inside_the_20**: The number of punt returns started inside the 20 yard line by the player during the game.
* **punt_return_touchdowns**: The number of punt return touchdowns made by the player during the game.
* **punt_return_yards**: The yards gained by the player during the game.
* **special_team_fumble_returns**: The special team fumble returns made by the player during the game.
* **yards_per_kick_return**: The yards gained per kick return made by the player during the game.
* **yards_per_punt_return**: The yards gained per punt return made by the player during the game.
* **yards_per_return**: The yards gained per return made by the player during the game.
* **average_punt_return_yards**: The average yards gained per punt return made by the player during the game.
* **fair_catches**: The number of fair catches made by the player during the game.
* **gross_average_punt_yards**: The gross average punt yards made by the player during the game.
* **long_punt**: The long punts made by the player during the game.
* **net_average_punt_yards**: The net average punt yards made by the player during the game.
* **punts**: The punts made by the player during the game.
* **punts_blocked**: The punts blocked made by the player during the game.
* **punts_blocked_percentage**: The percentage of punts blocked by the player during the game.
* **punts_inside_10**: The punts made by the player inside the 10 yard line during the game.
* **punts_inside_10_percentage**: The percentage of punts made by the player inside the 10 yard line during the game.
* **punts_inside_20**: The punts made by the player inside the 20 yard line during the game.
* **punts_inside_20_percentage**: The percentage of punts made by the player inside the 20 yard line during the game.
* **punts_over_50**: The punts over the 50 yard line made by the player during the game.
* **punt_yards**: The punt yards made by the player during the game.
* **defensive_points**: The points scored defensively by the player during the game.
* **misc_points**: The miscellaneous points made by the player during the game.
* **return_touchdowns**: The return touchdowns made by the player during the game.
* **total_two_point_conversions**: The total two point conversions made by the player during the game.
* **passing_touchdowns_9_yards**: The passing touchdowns made by the player during the game from 9 yards.
* **passing_touchdowns_19_yards**: The passing touchdowns made by the player during the game from 19 yards.
* **passing_touchdowns_29_yards**: The passing touchdowns made by the player during the game from 29 yards.
* **passing_touchdowns_39_yards**: The passing touchdowns made by the player during the game from 39 yards.
* **passing_touchdowns_49_yards**: The passing touchdowns made by the player during the game from 49 yards.
* **passing_touchdowns_above_50_yards**: The passing touchdowns made by the player during the game above 50 yards.
* **receiving_touchdowns_9_yards**: The receiving touchdowns made by the player during the game from 9 yards.
* **receiving_touchdowns_19_yards**: The receiving touchdowns made by the player during the game from 19 yards.
* **receiving_touchdowns_29_yards**: The receiving touchdowns made by the player during the game from 29 yards.
* **receiving_touchdowns_39_yards**: The receiving touchdowns made by the player during the game from 39 yards.
* **receiving_touchdowns_49_yards**: The receiving touchdowns made by the player during the game from 49 yards.
* **receiving_touchdowns_above_50_yards**: The receiving touchdowns made by the player during the game above 50 yards.
* **rushing_touchdowns_9_yards**: The rushing touchdowns made by the player during the game from 9 yards.
* **rushing_touchdowns_19_yards**: The rushing touchdowns made by the player during the game from 19 yards.
* **rushing_touchdowns_29_yards**: The rushing touchdowns made by the player during the game from 29 yards.
* **rushing_touchdowns_39_yards**: The rushing touchdowns made by the player during the game from 39 yards.
* **rushing_touchdowns_49_yards**: The rushing touchdowns made by the player during the game from 49 yards.
* **rushing_touchdowns_above_50_yards**: The rushing touchdowns made by the player during the game above 50 yards.

#### Odds

A representation of the odds for a team to win within a game.

* **odds**: The decimal odds offered by a bookie for the team to win in the game.
* **bookie**: The bookie offering these odds.
* **dt**: When the odds were posted.
* **canonical**: Whether these odds can be treated as canonical for the purposes of backtesting.
* **bet**: The type of bet the odds represent.

#### Venue

The venue the game is played at.

* **identifier**: The unique identifier for the venue.
* **names**: The name of the venue.
* **address**: The address of the venue.
* **is_grass**: Whether the venue has a grass field.
* **is_indoor**: Whether the venue is indoors.
* **is_turf**: Whether the venue is turf.
* **is_dirt**: Whether the venue is dirt.
* **version**: The version of the game model.

#### Address

The address of the venue.

* **city**: The city of the address.
* **state**: The state of the address.
* **zipcode**: The postal/zip code of the address.
* **latitude**: The latitude of the address.
* **longitude**: The longitude of the address.
* **housenumber**: The house/street number of the address.
* **weather**: The weather at the address at the game start time.
* **timezone**: The time zone at the address.
* **country**: The country of the address.
* **altitude**: The altitude of the address.
* **version**: The version of the address model.

#### Weather

The forecasted weather one day out at the address of the game start time.

* **temperature**: The temperature at the address at the game start time.
* **relative_humidity**: The relative humidity at the address at the game start time.
* **dew_point**: The temperature at the address at the game start time.
* **apparent_temperature**: The apparent temperature at the address at the game start time.
* **precipitation_probability**: The precipitation probability at the address at the game start time.
* **precipitation**: The precipitation at the address at the game start time.
* **rain**: The rain at the address at the game start time.
* **showers**: The showers at the address at the game start time.
* **snowfall**: The snowfall at the address at the game start time.
* **snow_depth**: The snow depth at the address at the game start time.
* **weather_code**: The weather code at the address at the game start time.
* **sealevel_pressure**: The sealevel pressure at the address at the game start time.
* **surface_pressure**: The surface pressure at the address at the game start time.
* **cloud_cover_total**: The total cloud cover at the address at the game start time.
* **cloud_cover_low**: The low cloud cover at the address at the game start time.
* **cloud_cover_mid**: The mid cloud cover at the address at the game start time.
* **cloud_cover_high**: The high cloud cover at the address at the game start time.
* **visibility**: The visibility at the address at the game start time.
* **evapotranspiration**: The evapotranspiration at the address at the game start time.
* **reference_evapotranspiration**: The reference evapotranspiration at the address at the game start time.
* **vapour_pressure_deficit**: The vapour pressure deficit at the address at the game start time.
* **wind_speed_10m**: The wind speed at 10m at the address at the game start time.
* **wind_speed_80m**: The wind speed at 80m at the address at the game start time.
* **wind_speed_120m**: The wind speed at 120m at the address at the game start time.
* **wind_speed_180m**: The wind speed at 180m at the address at the game start time.
* **wind_direction_10m**: The wind direction at 10m at the address at the game start time.
* **wind_direction_80m**: The wind direction at 80m at the address at the game start time.
* **wind_direction_120m**: The wind direction at 120m at the address at the game start time.
* **wind_direction_180m**: The wind direction at 180m at the address at the game start time.
* **wind_gusts**: The wind gusts at the address at the game start time.
* **temperature_80m**: The temperature at 80m at the address at the game start time.
* **temperature_120m**: The temperature at 120m at the address at the game start time.
* **temperature_180m**: The temperature at 180m at the address at the game start time.
* **soil_temperature_0cm**: The soil temperature at the address at the game start time.
* **soil_temperature_6cm**: The soil temperature at 6cm at the address at the game start time.
* **soil_temperature_18cm**: The soil temperature at 18cm at the address at the game start time.
* **soil_temperature_54cm**: The soil temperature at 54cm at the address at the game start time.
* **soil_moisture_0cm**: The soil moisture at the address at the game start time.
* **soil_moisture_1cm**: The soil moisture at 1cm at the address at the game start time.
* **soil_moisture_3cm**: The soil moisture at 3cm at the address at the game start time.
* **soil_moisture_9cm**: The soil moisture at 9cm at the address at the game start time.
* **soil_moisture_27cm**: The soil moisture at 27cm at the address at the game start time.
* **daily_weather_code**: The daily weather code at the address at the game start time.
* **daily_maximum_temperature_2m**: The daily maximum temperature at 2m at the address at the game start time.
* **daily_minimum_temperature_2m**: The daily minimum temperature at 2m at the address at the game start time.
* **daily_maximum_apparent_temperature_2m**: The daily maximum apparent temperature at 2m at the address at the game start time.
* **daily_minimum_apparent_temperature_2m**: The daily minimum apparent temperature at 2m at the address at the game start time.
* **sunrise**: The sunrise at the address at the game start time.
* **sunset**: The sunset at the address at the game start time.
* **daylight_duration**: The daylight duration at the address at the game start time.
* **sunshine_duration**: The sunshine duration at the address at the game start time.
* **uv_index**: The UV index at the address at the game start time.
* **uv_index_clear_sky**: The UV index for clear sky at the address at the game start time.
* **rain_sum**: The rain sum at the address at the game start time.
* **showers_sum**: The showers sum at the address at the game start time.
* **snowfall_sum**: The snowfall sum at the address at the game start time.
* **precipitation_sum**: The precipitation sum at the address at the game start time.
* **precipitation_hours**: The precipitation hours at the address at the game start time.
* **precipitation_probability_max**: The maximum precipitation probability at the address at the game start time.
* **maximum_wind_speed_10m**: The maximum wind speed at 10m at the address at the game start time.
* **maximum_wind_gusts_10m**: The maximum wind gusts at 10m at the address at the game start time.
* **dominant_wind_direction**: The dominant wind direction at the address at the game start time.
* **shortwave_radiation_sum**: The shortwave radiation sum at the address at the game start time.
* **daily_reference_evapotranspiration**: The daily reference evapotranspiration at the address at the game start time.
* **version**: The version of the weather model.

#### News

The news one day out from the game.

* **title**: The title of the article
* **published**: When the article was published.
* **summary**: The summary of the article.
* **source**: The source of the article.

#### Social

Social media posts one day out from the game.

* **network**: The social network this post was made from.
* **post**: The text of the post.
* **comments**: The number of comments on the post.
* **reposts**: The number of reposts.
* **likes**: The number of likes the post received.
* **views**: The number of views the post has.
* **published**: When the post was published.

#### Coach

The coach on the team at the time of the game.

* **identifier**: The unique identifier for the coach.
* **name**: The name of the coach.
* **birth_date**: The birth date of the coach.
* **age**: The age of the coach.
* **sex**: The sex of the coach.
* **version**: The version of the coach model.

#### Dividend

The dividend payout at the end of the game.

* **pool**: The type of bet paying the dividend.
* **combination**: The combination of team identifiers making up the dividend.
* **dividend**: The payout of the dividend.

#### Owner

The owner of a player.

* **name**: The name of the owner.
* **identifier**: The unique identifier of the owner.

## Caching

This library uses very aggressive caching due to the large data requirements. If the requests are about a recent game (generally in the last 7 days) the caching is bypassed. The caching is as follows:

1. A joblib disk cache that caches calls to pydantic model creation functions. This changes on every version update to keep the models in sync. This is the fastest cache.
2. A requests cache backed by sqlite that caches requests forever.
3. An attempt to find the response is made to the wayback machine, and used if found.

It's very recommended that the user uses proxies defined in the `PROXIES` environment variable. The more proxies the easier it is to collect data.

## Installation :inbox_tray:

This is a python package hosted on pypi, so to install simply run the following command:

`pip install sportsball`

or install using this local repository:

`python setup.py install --old-and-unmanageable`

## Usage example :eyes:

There are many different ways of using sportsball, but we generally recommend the CLI.

### CLI

To fetch a dataframe containing information about a league, you can use the following CLI:

```
sportsball --league=nfl -
```

The final argument denotes the file to write to, in this case `-` is stdout.

### Python

To pull a dataframe containing all the information for a particular league, the following example can be used:

```python
from sportsball import sportsball as spb

ball = spb.SportsBall()
league = ball.league(spb.League.AFL)
df = league.to_frame()
```

This results in a dataframe where each game is represented by all its features.

### Environment

If you wish to use the providers that require API keys, you can create a `.env` file with the following variables inside it:

```
GOOGLE_API_KEY=APIKEY
GRIBSTREAM_API_KEY=APIKEY
X_API_KEY=APIKEY
X_API_SECRET_KEY=APISECRETKEY
X_ACCESS_TOKEN=ACCESSTOKEN
X_ACCESS_TOKEN_SECRET=ACCESSTOKENSECRET
PROXIES=CSVPROXIESLIST
```

## License :memo:

The project is available under the [MIT License](LICENSE).
