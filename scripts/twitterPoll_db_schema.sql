CREATE TABLE TWEETS (
  TWEET_ID DECIMAL(65,0) PRIMARY KEY NOT NULL,
  USER_ID DECIMAL(65,0) NOT NULL,
  CANDIDATE_ID DECIMAL(65,0) NOT NULL,
  PLACE VARCHAR(250),
  TWEET_TEXT VARCHAR(250)
);

CREATE TABLE TWEET_TIMES (
  TWEET_ID DECIMAL(65,0) PRIMARY KEY NOT NULL,
  TWEET_TIME DATETIME
);

CREATE TABLE GEO_LOCS (
  GEO_ID INT PRIMARY KEY NOT NULL,
  XCOOR INT,
  YCOOR INT,
  GEO_DESC VARCHAR(500)
);

CREATE TABLE CANDIDATES (
  CANDIDATE_ID INT PRIMARY KEY NOT NULL,
  NAME VARCHAR(100),
  PARTY VARCHAR(100)
);

CREATE TABLE VOTES (
  VOTE_ID DECIMAL(65,0) PRIMARY KEY NOT NULL,
  CANDIDATE_ID INT
);

CREATE TABLE WEIGHTED_VOTES (
  VOTE_ID DECIMAL(65,0) PRIMARY KEY NOT NULL,
  CANDIDATE_ID INT,
  SCORE INT,
  SIDE VARCHAR(10)
);

CREATE TABLE USERS (
  USER_ID DECIMAL(65,0) PRIMARY KEY NOT NULL,
  SCREEN_NAME VARCHAR(140),
  LOCATION VARCHAR(140),
  DESCRIPTION VARCHAR(250),
  NUM_FOLLOWERS INT,
  NUM_STATUSES INT
);

SELECT *
FROM TWEETS T,
     USERS U,
     NLP_RESULTS N
WHERE T.USER_ID = U.USER_ID AND T.TWEET_ID = N.NLP_ID;


INSERT INTO CANDIDATES VALUES (0, 'Hillary Clinton', 'Democrat');
INSERT INTO CANDIDATES VALUES (1, 'Bernie Sanders', 'Democrat');
INSERT INTO CANDIDATES VALUES (2, 'Donald Trump', 'GOP');
INSERT INTO CANDIDATES VALUES (3, 'Ted Cruz', 'GOP');
INSERT INTO CANDIDATES VALUES (4, 'John Kasich', 'GOP');

CREATE TABLE NLP_RESULTS (
  NLP_ID DECIMAL(65,0) PRIMARY KEY NOT NULL,
  SCORE VARCHAR(5),
  AGREEMENT VARCHAR(25),
  SUBJECTIVE VARCHAR(25),
  CONFIDENCE INT CHECK (CONFIDENCE >= 0 AND CONFIDENCE <= 100)
);

CREATE TABLE HASHTAGS (
  HASHTAG_ID INT PRIMARY KEY NOT NULL,
  TAG VARCHAR(100)
);

CREATE TABLE HASHTAG_LOOKUP (
  TWEET_ID INT NOT NULL,
  HASHTAG_ID INT NOT NULL,
  CONSTRAINT ID PRIMARY KEY (id),
);
