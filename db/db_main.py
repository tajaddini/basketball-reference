from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, select
from sqlalchemy.orm import declarative_base, relationship, Session
import pandas as pd

engine = create_engine("sqlite:///db/main.db")

Base = declarative_base()


class Player(Base):
    __tablename__ = "players"

    id = Column(String(50), primary_key=True)
    name = Column(String(255))
    pos = Column(String(255))
    shoots = Column(String(255))
    age = Column(Float)
    is_alive = Column(Boolean)
    height = Column(Integer)
    weight = Column(Integer)
    career_length = Column(Integer)
    is_active = Column(Boolean)
    has_hall_of_fame = Column(Boolean)
    count_allstar = Column(Integer)
    stat_games = Column(Integer)
    stat_points = Column(Integer)
    stat_total_rebounds = Column(Integer)
    stat_assists = Column(Integer)
    stat_field_goal_pct = Column(Float)
    stat_three_point_field_goal_pct = Column(Float)
    stat_effective_field_goal_pct = Column(Float)
    stat_free_throw_pct = Column(Float)
    stat_efficiency_rating = Column(Float)
    stat_win_shares = Column(Float)

    salaries = relationship('Salary', back_populates='player')
    roster_datas = relationship('RosterData', back_populates='player')
    player_evaluations = relationship(
        'PlayerEvaluation', back_populates='player')
    awards = relationship('Award', back_populates='player')


class Salary(Base):
    __tablename__ = "salaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String(50), ForeignKey('players.id'))
    season = Column(String(50))
    salary = Column(Integer)
    player = relationship('Player', back_populates='salaries')


class RosterData(Base):
    __tablename__ = "roster_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String(50), ForeignKey('players.id'))
    team_name = Column(String(255))
    season = Column(String(50))
    player_position = Column(String(50))
    player = relationship('Player', back_populates='roster_datas')
    champions = relationship('Champion', back_populates='roster_data')


class PlayerEvaluation(Base):
    __tablename__ = "player_evaluations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String(50), ForeignKey('players.id'))
    won_at_age = Column(Integer)
    season = Column(String(50))
    rank = Column(Integer)
    team = Column(String(50))
    player_position = Column(String(50))
    points = Column(Integer)
    player = relationship('Player', back_populates='player_evaluations')


class Award(Base):
    __tablename__ = "awards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    award_type = Column(String(50))
    player_id = Column(String(50), ForeignKey('players.id'))
    season = Column(String(50))
    player_age = Column(Integer)
    team = Column(String(50))
    games = Column(Integer)
    minutes_per_game = Column(Float)
    points_per_game = Column(Float)
    total_rebounds_per_game = Column(Float)
    assists_per_game = Column(Float)
    steals_per_game = Column(Float)
    blocks_per_game = Column(Float)
    pct_field_goals = Column(Float)
    pct_threeP_field_goals = Column(Float)
    pct_ft_field_goals = Column(Float)
    win_shares = Column(Float)
    win_shares_48 = Column(Float)
    player = relationship('Player', back_populates='awards')


class Champion(Base):
    __tablename__ = "champions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    season = Column(String(50))
    team = Column(String(50))
    team_id = Column(String(50))
    roster_data = relationship('RosterData', back_populates='champions')


Base.metadata.create_all(engine)

df1 = pd.read_csv("scraped/players.csv")
df1.to_sql("players", con=engine, if_exists="replace", index=False)
df2 = pd.read_csv("scraped/salaries.csv")
df2.to_sql("salaries", con=engine, if_exists="replace", index=False)
df3 = pd.read_csv("scraped/roster_data.csv")
df3.to_sql("roster_data", con=engine, if_exists="replace", index=False)
df4 = pd.read_csv("scraped/player_evaluations.csv")
df4.to_sql("player_evaluations", con=engine,
           if_exists="append", index=False)
df5 = pd.read_csv("scraped/basketball_dpoy.csv")
df6 = pd.read_csv("scraped/mvp_winners.csv")
df6["award_type"] = "MVP"
df_awards = pd.concat([df5, df6])
df_awards.to_sql("awards", con=engine, if_exists="replace", index=False)
df7 = pd.read_csv("scraped/champions.csv")
df7.to_sql("champions", con=engine, if_exists="replace", index=False)

session = Session(engine)
