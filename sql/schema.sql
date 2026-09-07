-- ============================================================
-- CRICBUZZ LIVESTATS
-- Database Schema
-- ============================================================


-- ============================================================
-- 1. PLAYER
-- ============================================================

CREATE TABLE player (
    player_id INTEGER PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(30) NOT NULL,
    batting_style VARCHAR(50),
    bowling_style VARCHAR(50),
    country VARCHAR(50) NOT NULL
);


-- ============================================================
-- 2. TEAM
-- ============================================================

CREATE TABLE team (
    team_id INTEGER PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL UNIQUE,
    country VARCHAR(50) NOT NULL,
    team_type VARCHAR(30)
);


-- ============================================================
-- 3. VENUE
-- ============================================================

CREATE TABLE venue (
    venue_id INTEGER PRIMARY KEY,
    venue_name VARCHAR(150) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(50) NOT NULL,
    capacity INTEGER CHECK (capacity >= 0)
);


-- ============================================================
-- 4. SERIES
-- ============================================================

CREATE TABLE series (
    series_id INTEGER PRIMARY KEY,
    series_name VARCHAR(150) NOT NULL,
    host_country VARCHAR(50) NOT NULL,
    match_type VARCHAR(20) NOT NULL,
    start_date DATE,
    planned_matches INTEGER CHECK (planned_matches >= 0)
);


-- ============================================================
-- 5. MATCH
-- ============================================================

CREATE TABLE match (
    match_id INTEGER PRIMARY KEY,
    series_id INTEGER,
    venue_id INTEGER,
    match_date DATE NOT NULL,
    match_type VARCHAR(20) NOT NULL,
    status VARCHAR(30) NOT NULL,

    winner_team_id INTEGER,
    toss_winner_team_id INTEGER,
    toss_decision VARCHAR(10),

    victory_margin INTEGER CHECK (victory_margin >= 0),
    victory_type VARCHAR(10),

    FOREIGN KEY (series_id)
        REFERENCES series(series_id),

    FOREIGN KEY (venue_id)
        REFERENCES venue(venue_id),

    FOREIGN KEY (winner_team_id)
        REFERENCES team(team_id),

    FOREIGN KEY (toss_winner_team_id)
        REFERENCES team(team_id),

    CHECK (
        toss_decision IS NULL
        OR toss_decision IN ('bat', 'bowl')
    ),

    CHECK (
        victory_type IS NULL
        OR victory_type IN ('runs', 'wickets')
    )
);


-- ============================================================
-- 6. MATCH_TEAM
-- ============================================================

CREATE TABLE match_team (
    match_team_id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    team_position INTEGER NOT NULL,

    FOREIGN KEY (match_id)
        REFERENCES match(match_id),

    FOREIGN KEY (team_id)
        REFERENCES team(team_id),

    UNIQUE (match_id, team_id),

    UNIQUE (match_id, team_position)
);


-- ============================================================
-- 7. PLAYER_MATCH_PERFORMANCE
-- ============================================================

CREATE TABLE player_match_performance (
    performance_id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    innings INTEGER NOT NULL,
    batting_position INTEGER,
    runs INTEGER NOT NULL DEFAULT 0,
    balls INTEGER NOT NULL DEFAULT 0,
    fours INTEGER NOT NULL DEFAULT 0,
    sixes INTEGER NOT NULL DEFAULT 0,
    strike_rate DECIMAL(6,2),

    dismissal VARCHAR(100),

    FOREIGN KEY (match_id)
        REFERENCES match(match_id),

    FOREIGN KEY (player_id)
        REFERENCES player(player_id),

    FOREIGN KEY (team_id)
        REFERENCES team(team_id),

    CHECK (innings > 0),
    CHECK (batting_position IS NULL OR batting_position > 0),
    CHECK (runs >= 0),
    CHECK (balls >= 0),
    CHECK (fours >= 0),
    CHECK (sixes >= 0),

    UNIQUE (match_id, player_id, innings)
);


-- ============================================================
-- 8. BOWLING_PERFORMANCE
-- ============================================================

CREATE TABLE bowling_performance (
    bowling_id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    innings INTEGER NOT NULL,

    overs DECIMAL(5,1) NOT NULL DEFAULT 0,
    runs_conceded INTEGER NOT NULL DEFAULT 0,
    wickets INTEGER NOT NULL DEFAULT 0,
    maidens INTEGER NOT NULL DEFAULT 0,
    economy_rate DECIMAL(6,2),

    FOREIGN KEY (match_id)
        REFERENCES match(match_id),

    FOREIGN KEY (player_id)
        REFERENCES player(player_id),

    FOREIGN KEY (team_id)
        REFERENCES team(team_id),

    CHECK (innings > 0),
    CHECK (overs >= 0),
    CHECK (runs_conceded >= 0),
    CHECK (wickets >= 0),
    CHECK (maidens >= 0),

    UNIQUE (match_id, player_id, innings)
);


-- ============================================================
-- 9. FIELDING_PERFORMANCE
-- ============================================================

CREATE TABLE fielding_performance (
    fielding_id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    innings INTEGER NOT NULL,

    catches INTEGER NOT NULL DEFAULT 0,
    stumpings INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (match_id)
        REFERENCES match(match_id),

    FOREIGN KEY (player_id)
        REFERENCES player(player_id),

    FOREIGN KEY (team_id)
        REFERENCES team(team_id),

    CHECK (innings > 0),
    CHECK (catches >= 0),
    CHECK (stumpings >= 0),

    UNIQUE (match_id, player_id, innings)
);


-- ============================================================
-- 10. PARTNERSHIP
-- ============================================================

CREATE TABLE partnership (
    partnership_id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL,
    innings INTEGER NOT NULL,

    batsman1_id INTEGER NOT NULL,
    batsman2_id INTEGER NOT NULL,

    batsman1_position INTEGER NOT NULL,
    batsman2_position INTEGER NOT NULL,

    runs INTEGER NOT NULL DEFAULT 0,
    balls INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (match_id)
        REFERENCES match(match_id),

    FOREIGN KEY (batsman1_id)
        REFERENCES player(player_id),

    FOREIGN KEY (batsman2_id)
        REFERENCES player(player_id),

    CHECK (innings > 0),
    CHECK (batsman1_id <> batsman2_id),
    CHECK (batsman1_position > 0),
    CHECK (batsman2_position > 0),
    CHECK (runs >= 0),
    CHECK (balls >= 0)
);