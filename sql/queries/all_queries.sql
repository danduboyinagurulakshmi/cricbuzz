-- QUERY 01: India players
SELECT full_name, role, batting_style, bowling_style
FROM player
WHERE country = 'India'
ORDER BY full_name;

-- QUERY 02: Matches in the last 30 days
SELECT m.match_id, m.match_date, m.match_type, m.status, v.venue_name, v.city
FROM "match" AS m
LEFT JOIN venue AS v ON v.venue_id = m.venue_id
WHERE date(m.match_date) >= date('now', '-30 days')
ORDER BY m.match_date DESC;

-- QUERY 03: ODI run scorers
SELECT p.full_name, SUM(perf.runs) AS total_runs,
       ROUND(1.0 * SUM(perf.runs) / NULLIF(SUM(CASE WHEN perf.dismissal NOT IN ('Not Out', 'not out') THEN 1 ELSE 0 END), 0), 2) AS batting_average,
       SUM(CASE WHEN perf.runs >= 100 THEN 1 ELSE 0 END) AS centuries
FROM player AS p
JOIN player_match_performance AS perf ON perf.player_id = p.player_id
JOIN "match" AS m ON m.match_id = perf.match_id
WHERE m.match_type = 'ODI'
GROUP BY p.player_id
ORDER BY total_runs DESC
LIMIT 10;

-- QUERY 04: Large venues
SELECT venue_name, city, country, capacity
FROM venue
WHERE capacity > 50000
ORDER BY capacity DESC;

-- QUERY 05: Team wins
SELECT t.team_name, COUNT(m.match_id) AS total_wins
FROM team AS t
LEFT JOIN "match" AS m ON m.winner_team_id = t.team_id
GROUP BY t.team_id
ORDER BY total_wins DESC, t.team_name;

-- QUERY 06: Players by role
SELECT role, COUNT(*) AS player_count
FROM player
GROUP BY role
ORDER BY player_count DESC;

-- QUERY 07: Highest score by format
SELECT m.match_type, MAX(perf.runs) AS highest_score
FROM player_match_performance AS perf
JOIN "match" AS m ON m.match_id = perf.match_id
GROUP BY m.match_type
ORDER BY m.match_type;

-- QUERY 08: Series started in 2024
SELECT series_name, host_country, match_type, start_date, planned_matches
FROM series
WHERE strftime('%Y', start_date) = '2024'
ORDER BY start_date;

-- QUERY 09: All-rounders with 1000 runs and 50 wickets
SELECT p.full_name, SUM(perf.runs) AS total_runs, SUM(COALESCE(bow.wickets, 0)) AS total_wickets
FROM player AS p
LEFT JOIN player_match_performance AS perf ON perf.player_id = p.player_id
LEFT JOIN bowling_performance AS bow ON bow.player_id = p.player_id
WHERE p.role = 'All-rounder'
GROUP BY p.player_id
HAVING total_runs > 1000 AND total_wickets > 50;

-- QUERY 10: Last 20 completed matches
SELECT m.match_id, m.match_date, m.match_type,
       GROUP_CONCAT(t.team_name, ' vs ') AS teams,
       winner.team_name AS winning_team, m.victory_margin, m.victory_type, v.venue_name
FROM "match" AS m
JOIN match_team AS mt ON mt.match_id = m.match_id
JOIN team AS t ON t.team_id = mt.team_id
LEFT JOIN team AS winner ON winner.team_id = m.winner_team_id
LEFT JOIN venue AS v ON v.venue_id = m.venue_id
WHERE m.status = 'Completed'
GROUP BY m.match_id
ORDER BY m.match_date DESC
LIMIT 20;

-- QUERY 11: Player performance by format
SELECT p.full_name,
       SUM(CASE WHEN m.match_type = 'Test' THEN perf.runs ELSE 0 END) AS test_runs,
       SUM(CASE WHEN m.match_type = 'ODI' THEN perf.runs ELSE 0 END) AS odi_runs,
       SUM(CASE WHEN m.match_type = 'T20I' THEN perf.runs ELSE 0 END) AS t20_runs,
       ROUND(AVG(perf.runs), 2) AS overall_average,
       COUNT(DISTINCT m.match_type) AS formats_played
FROM player AS p
JOIN player_match_performance AS perf ON perf.player_id = p.player_id
JOIN "match" AS m ON m.match_id = perf.match_id
GROUP BY p.player_id
HAVING formats_played >= 2
ORDER BY p.full_name;

-- QUERY 12: Home versus away wins
WITH appearances AS (
    SELECT mt.team_id, m.match_id, m.winner_team_id,
           CASE WHEN v.country = t.country THEN 'Home' ELSE 'Away' END AS location
    FROM match_team AS mt
    JOIN "match" AS m ON m.match_id = mt.match_id
    JOIN team AS t ON t.team_id = mt.team_id
    JOIN venue AS v ON v.venue_id = m.venue_id
)
SELECT t.team_name, a.location, COUNT(*) AS matches,
       SUM(CASE WHEN a.winner_team_id = a.team_id THEN 1 ELSE 0 END) AS wins
FROM appearances AS a
JOIN team AS t ON t.team_id = a.team_id
GROUP BY a.team_id, a.location
ORDER BY t.team_name, a.location;

-- QUERY 13: Consecutive batting partnerships over 100
SELECT p1.full_name AS batsman_one, p2.full_name AS batsman_two,
       partnership.runs, partnership.innings, partnership.match_id
FROM partnership
JOIN player AS p1 ON p1.player_id = partnership.batsman1_id
JOIN player AS p2 ON p2.player_id = partnership.batsman2_id
WHERE ABS(partnership.batsman1_position - partnership.batsman2_position) = 1
  AND partnership.runs >= 100
ORDER BY partnership.runs DESC;

-- QUERY 14: Bowlers by venue
SELECT p.full_name, v.venue_name, COUNT(DISTINCT b.match_id) AS matches,
       ROUND(AVG(b.economy_rate), 2) AS average_economy, SUM(b.wickets) AS total_wickets
FROM bowling_performance AS b
JOIN player AS p ON p.player_id = b.player_id
JOIN "match" AS m ON m.match_id = b.match_id
JOIN venue AS v ON v.venue_id = m.venue_id
WHERE b.overs >= 4
GROUP BY b.player_id, m.venue_id
HAVING matches >= 3
ORDER BY average_economy;

-- QUERY 15: Players in close matches
SELECT p.full_name, COUNT(DISTINCT perf.match_id) AS close_matches,
       ROUND(AVG(perf.runs), 2) AS average_runs,
       SUM(CASE WHEN m.winner_team_id = perf.team_id THEN 1 ELSE 0 END) AS team_wins
FROM player_match_performance AS perf
JOIN player AS p ON p.player_id = perf.player_id
JOIN "match" AS m ON m.match_id = perf.match_id
WHERE (m.victory_type = 'runs' AND m.victory_margin < 50)
   OR (m.victory_type = 'wickets' AND m.victory_margin < 5)
GROUP BY p.player_id
ORDER BY average_runs DESC;

-- QUERY 16: Yearly batting performance since 2020
SELECT p.full_name, strftime('%Y', m.match_date) AS year,
       COUNT(DISTINCT m.match_id) AS matches,
       ROUND(AVG(perf.runs), 2) AS average_runs,
       ROUND(AVG(perf.strike_rate), 2) AS average_strike_rate
FROM player AS p
JOIN player_match_performance AS perf ON perf.player_id = p.player_id
JOIN "match" AS m ON m.match_id = perf.match_id
WHERE date(m.match_date) >= date('2020-01-01')
GROUP BY p.player_id, year
HAVING matches >= 5
ORDER BY year, average_runs DESC;

-- QUERY 17: Toss advantage by decision
SELECT m.toss_decision, COUNT(*) AS tosses,
       SUM(CASE WHEN m.toss_winner_team_id = m.winner_team_id THEN 1 ELSE 0 END) AS toss_winner_wins,
       ROUND(100.0 * SUM(CASE WHEN m.toss_winner_team_id = m.winner_team_id THEN 1 ELSE 0 END) / COUNT(*), 2) AS win_percentage
FROM "match" AS m
WHERE m.winner_team_id IS NOT NULL
GROUP BY m.toss_decision;

-- QUERY 18: Economical limited-overs bowlers
SELECT p.full_name, COUNT(*) AS matches, SUM(b.wickets) AS wickets,
       ROUND(AVG(b.economy_rate), 2) AS economy_rate,
       ROUND(AVG(b.overs), 2) AS average_overs
FROM bowling_performance AS b
JOIN player AS p ON p.player_id = b.player_id
JOIN "match" AS m ON m.match_id = b.match_id
WHERE m.match_type IN ('ODI', 'T20', 'T20I')
GROUP BY p.player_id
HAVING matches >= 10 AND average_overs >= 2
ORDER BY economy_rate, wickets DESC;

-- QUERY 19: Batting consistency
SELECT p.full_name, COUNT(*) AS innings, ROUND(AVG(perf.runs), 2) AS average_runs,
       ROUND(sqrt(AVG(perf.runs * perf.runs) - AVG(perf.runs) * AVG(perf.runs)), 2) AS runs_standard_deviation
FROM player AS p
JOIN player_match_performance AS perf ON perf.player_id = p.player_id
JOIN "match" AS m ON m.match_id = perf.match_id
WHERE perf.balls >= 10 AND date(m.match_date) >= date('2022-01-01')
GROUP BY p.player_id
HAVING innings >= 1
ORDER BY runs_standard_deviation;

-- QUERY 20: Format appearances and batting averages
SELECT p.full_name,
       COUNT(DISTINCT CASE WHEN m.match_type = 'Test' THEN m.match_id END) AS test_matches,
       COUNT(DISTINCT CASE WHEN m.match_type = 'ODI' THEN m.match_id END) AS odi_matches,
       COUNT(DISTINCT CASE WHEN m.match_type IN ('T20', 'T20I') THEN m.match_id END) AS t20_matches,
       ROUND(AVG(CASE WHEN m.match_type = 'Test' THEN perf.runs END), 2) AS test_average,
       ROUND(AVG(CASE WHEN m.match_type = 'ODI' THEN perf.runs END), 2) AS odi_average,
       ROUND(AVG(CASE WHEN m.match_type IN ('T20', 'T20I') THEN perf.runs END), 2) AS t20_average
FROM player AS p
JOIN player_match_performance AS perf ON perf.player_id = p.player_id
JOIN "match" AS m ON m.match_id = perf.match_id
GROUP BY p.player_id
HAVING COUNT(DISTINCT m.match_id) >= 20;

-- QUERY 21: Weighted player performance ranking
WITH batting AS (
    SELECT player_id, SUM(runs) AS runs, AVG(strike_rate) AS strike_rate,
           AVG(runs) AS batting_average
    FROM player_match_performance GROUP BY player_id
), bowling AS (
    SELECT player_id, SUM(wickets) AS wickets, AVG(economy_rate) AS economy_rate,
           AVG(CASE WHEN wickets > 0 THEN runs_conceded * 1.0 / wickets END) AS bowling_average
    FROM bowling_performance GROUP BY player_id
), fielding AS (
    SELECT player_id, SUM(catches) AS catches, SUM(stumpings) AS stumpings
    FROM fielding_performance GROUP BY player_id
)
SELECT p.full_name,
       ROUND(COALESCE(b.runs, 0) * 0.01 + COALESCE(b.batting_average, 0) * 0.5 + COALESCE(b.strike_rate, 0) * 0.3
           + COALESCE(w.wickets, 0) * 2 + (50 - COALESCE(w.bowling_average, 50)) * 0.5 + (6 - COALESCE(w.economy_rate, 6)) * 2
           + COALESCE(f.catches, 0) * 3 + COALESCE(f.stumpings, 0) * 5, 2) AS performance_score
FROM player AS p
LEFT JOIN batting AS b ON b.player_id = p.player_id
LEFT JOIN bowling AS w ON w.player_id = p.player_id
LEFT JOIN fielding AS f ON f.player_id = p.player_id
ORDER BY performance_score DESC;

-- QUERY 22: Head-to-head team records
WITH pairs AS (
    SELECT m.match_id, MIN(mt.team_id) AS team_one_id, MAX(mt.team_id) AS team_two_id, m.winner_team_id,
           m.victory_margin, m.victory_type
    FROM "match" AS m JOIN match_team AS mt ON mt.match_id = m.match_id
    WHERE date(m.match_date) >= date('now', '-3 years')
    GROUP BY m.match_id
    HAVING COUNT(*) = 2
)
SELECT t1.team_name AS team_one, t2.team_name AS team_two, COUNT(*) AS matches,
       SUM(CASE WHEN p.winner_team_id = p.team_one_id THEN 1 ELSE 0 END) AS team_one_wins,
       SUM(CASE WHEN p.winner_team_id = p.team_two_id THEN 1 ELSE 0 END) AS team_two_wins,
       ROUND(AVG(CASE WHEN p.winner_team_id = p.team_one_id THEN p.victory_margin END), 2) AS team_one_average_margin,
       ROUND(AVG(CASE WHEN p.winner_team_id = p.team_two_id THEN p.victory_margin END), 2) AS team_two_average_margin
FROM pairs AS p JOIN team AS t1 ON t1.team_id = p.team_one_id JOIN team AS t2 ON t2.team_id = p.team_two_id
GROUP BY p.team_one_id, p.team_two_id
HAVING matches >= 5;

-- QUERY 23: Recent player form
WITH recent AS (
    SELECT perf.*, ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY match_id DESC) AS form_rank
    FROM player_match_performance AS perf
)
SELECT p.full_name,
       ROUND(AVG(CASE WHEN r.form_rank <= 5 THEN r.runs END), 2) AS last_five_average,
       ROUND(AVG(r.runs), 2) AS last_ten_average,
       ROUND(AVG(r.strike_rate), 2) AS recent_strike_rate,
       SUM(CASE WHEN r.runs >= 50 THEN 1 ELSE 0 END) AS scores_over_50
FROM recent AS r JOIN player AS p ON p.player_id = r.player_id
WHERE r.form_rank <= 10
GROUP BY r.player_id
ORDER BY last_five_average DESC;

-- QUERY 24: Successful batting partnerships
SELECT p1.full_name AS batsman_one, p2.full_name AS batsman_two,
       COUNT(*) AS partnerships, ROUND(AVG(pa.runs), 2) AS average_runs,
       SUM(CASE WHEN pa.runs > 50 THEN 1 ELSE 0 END) AS partnerships_over_50,
       MAX(pa.runs) AS highest_partnership,
       ROUND(100.0 * SUM(CASE WHEN pa.runs > 50 THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate
FROM partnership AS pa
JOIN player AS p1 ON p1.player_id = pa.batsman1_id
JOIN player AS p2 ON p2.player_id = pa.batsman2_id
WHERE ABS(pa.batsman1_position - pa.batsman2_position) = 1
GROUP BY pa.batsman1_id, pa.batsman2_id
HAVING partnerships >= 5
ORDER BY success_rate DESC, average_runs DESC;

-- QUERY 25: Quarterly batting trajectory
WITH quarterly AS (
    SELECT perf.player_id, strftime('%Y', m.match_date) || '-Q' || ((CAST(strftime('%m', m.match_date) AS INTEGER) - 1) / 3 + 1) AS quarter,
           AVG(perf.runs) AS average_runs, AVG(perf.strike_rate) AS average_strike_rate,
           COUNT(DISTINCT m.match_id) AS matches
    FROM player_match_performance AS perf JOIN "match" AS m ON m.match_id = perf.match_id
    GROUP BY perf.player_id, quarter
), trends AS (
    SELECT quarterly.*, LAG(average_runs) OVER (PARTITION BY player_id ORDER BY quarter) AS previous_average
    FROM quarterly WHERE matches >= 3
)
SELECT p.full_name, t.quarter, ROUND(t.average_runs, 2) AS average_runs,
       ROUND(t.average_strike_rate, 2) AS average_strike_rate,
       CASE WHEN t.previous_average IS NULL THEN 'Baseline'
            WHEN t.average_runs > t.previous_average THEN 'Improving'
            WHEN t.average_runs < t.previous_average THEN 'Declining'
            ELSE 'Stable' END AS trajectory
FROM trends AS t JOIN player AS p ON p.player_id = t.player_id
ORDER BY p.full_name, t.quarter;