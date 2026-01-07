import pandas
import sqlalchemy as sa

# read the data
players = pandas.read_csv('../scraped/players.csv', index_col='id')
salaries = pandas.read_csv('../scraped/salaries.csv')

# make the engine
engine = sa.create_engine('sqlite:///basketball_reference.db')

# data types, just to be sure

players_dtypes = {
    'id': sa.VARCHAR(50),
    'name': sa.VARCHAR(255),
    'pos': sa.VARCHAR(255),
    'shoots': sa.VARCHAR(255),
    'age': sa.FLOAT,
    'is_alive': sa.BOOLEAN,
    'height': sa.INTEGER,
    'weight': sa.INTEGER,
    'career_length': sa.INTEGER,
    'is_active': sa.BOOLEAN,
    'has_hall_of_fame': sa.BOOLEAN,
    'count_allstar': sa.INTEGER,
    'stat_games': sa.INTEGER,
    'stat_points': sa.INTEGER,
    'stat_total_rebounds': sa.INTEGER,
    'stat_assists': sa.INTEGER,
    'stat_field_goal_pct': sa.FLOAT,
    'stat_three_point_field_goal_pct': sa.FLOAT,
    'stat_effective_field_goal_pct': sa.FLOAT,
    'stat_free_throw_pct': sa.FLOAT,
    'stat_efficiency_rating': sa.FLOAT,
    'stat_win_shares': sa.FLOAT,
}

salaries_dtypes = {
    'id': sa.INTEGER,
    'player_id': sa.VARCHAR(50),
    'season': sa.VARCHAR(50),
    'salary': sa.INTEGER,
}

# export to sqlite

players.to_sql(
    name='players',
    con=engine,
    if_exists='replace',
    dtype=players_dtypes,
    index=True)

salaries.to_sql(
    name='salaries_raw',
    con=engine,
    if_exists='replace',
    dtype=salaries_dtypes,
    index=True
)

# now that the data is exported, I just need to specify the foreign key

create_command = sa.text('''create table salaries (
    id integer primary key autoincrement,
    player_id varchar(50),
    season varchar(50),
    salary integer,
    foreign key (player_id) references players(id)
);''')


with engine.connect() as session:
    session.execute(sa.text('drop table if exists salaries;'))
    session.execute(create_command)
    session.execute(sa.text('insert into salaries(player_id, season, salary) select player_id, season, salary from salaries_raw;'))
    session.execute(sa.text('drop table salaries_raw;'))
    # also, let's create indexes as well
    session.execute(sa.text('create index player_id_index on salaries(player_id);'))
    session.commit()