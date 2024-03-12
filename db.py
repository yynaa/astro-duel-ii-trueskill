import trueskill
from sqlmodel import SQLModel, create_engine, Field, Session, select
from sqlalchemy.orm import load_only
from datetime import datetime

default_mu = 100.0
default_sigma = 25.0 / 3.0
beta = default_sigma / 2.0
tau = default_sigma / 100.0
trueskill.setup(mu=default_mu, sigma=default_sigma, beta=beta, tau=tau, draw_probability=0.0)

engine = create_engine("sqlite:///astro-duel-ii.sqlite")


class Player(SQLModel, table=True):
    name: str = Field(primary_key=True)
    rating: float = Field(default=default_mu)
    deviation: float = Field(default=default_sigma)

class Match(SQLModel, table=True):
    id: int = Field(primary_key=True)
    map: str = Field()
    date: datetime = Field(default=datetime.now())

    teams: bool = Field(default=False)

    player1: str = Field(foreign_key="player.name")
    player2: str = Field(foreign_key="player.name")
    player3: str = Field(foreign_key="player.name", nullable=True)
    player4: str = Field(foreign_key="player.name", nullable=True)

    rank1: int = Field()
    rank2: int = Field()
    rank3: int = Field(nullable=True)
    rank4: int = Field(nullable=True)

SQLModel.metadata.create_all(engine)

def get_player(name: str) -> Player:
    with Session(engine) as session:
        return session.get(Player, name)

def get_players() -> list[str]:
    with Session(engine) as session:
        return [a.name for a in session.exec(select(Player)).all()]

def get_players_ranked() -> list[Player]:
    with Session(engine) as session:
        return [a.name for a in session.exec(select(Player).order_by(Player.rating.desc())).all()]

def add_player(name: str) -> None:
    with Session(engine) as session:
        if get_player(name):
            return
        session.add(Player(name=name))
        session.commit()

def remove_player(name: str) -> None:
    with Session(engine) as session:
        session.delete(Player, name=name)
        session.commit()

def recalculate_all_ratings() -> None:
    with Session(engine) as session:
        players = session.exec(select(Player)).all()
        for player in players:
            player.rating = default_mu
            player.deviation = default_sigma
        session.commit()

        matches = session.exec(select(Match)).all()
        for match in matches:
            recalculate_ratings(session, match)

def recalculate_ratings(session: Session, match: Match) -> None:
    if not match.teams:
        rating_groups = []
        ranks = []
        for i in range(1, 5):
            if getattr(match, f"player{i}"):
                player = session.get(Player, getattr(match, f"player{i}"))
                rating = trueskill.Rating(player.rating, player.deviation)
                rating_groups.append((rating,))
                ranks.append(int(getattr(match, f"rank{i}")))
        
        rated_rating_groups = trueskill.rate(rating_groups, ranks=ranks)

        for i in range(1, 5):
            if getattr(match, f"player{i}"):
                player = session.get(Player, getattr(match, f"player{i}"))
                player.rating = rated_rating_groups[i-1][0].mu
                player.deviation = rated_rating_groups[i-1][0].sigma
        
    else:
        if not match.player1 or not match.player2 or not match.player3 or not match.player4:
            return
        
        r1 = trueskill.Rating(session.get(Player, match.player1).rating, session.get(Player, match.player1).deviation)
        r2 = trueskill.Rating(session.get(Player, match.player2).rating, session.get(Player, match.player2).deviation)
        r3 = trueskill.Rating(session.get(Player, match.player3).rating, session.get(Player, match.player3).deviation)
        r4 = trueskill.Rating(session.get(Player, match.player4).rating, session.get(Player, match.player4).deviation)

        rating_groups = [(r1, r2), (r3, r4)]
        ranks = [int(match.rank1), int(match.rank2)]

        rated_rating_groups = trueskill.rate(rating_groups, ranks=ranks)

        match.player1.rating = rated_rating_groups[0][0].mu
        match.player1.deviation = rated_rating_groups[0][0].sigma
        match.player2.rating = rated_rating_groups[0][1].mu
        match.player2.deviation = rated_rating_groups[0][1].sigma
        match.player3.rating = rated_rating_groups[1][0].mu
        match.player3.deviation = rated_rating_groups[1][0].sigma
        match.player4.rating = rated_rating_groups[1][1].mu
        match.player4.deviation = rated_rating_groups[1][1].sigma
    
    session.commit()

def add_match(map: str, teams: bool, players: list[str], ranks: list[int]) -> None:
    with Session(engine) as session:
        match = Match(map=map, teams=teams)
        for i in range(4):
            if i < len(players):
                setattr(match, f"player{i+1}", players[i])
                setattr(match, f"rank{i+1}", int(ranks[i]))
        session.add(match)
        session.commit()
        recalculate_ratings(session, match)

def remove_match(id: int) -> None:
    with Session(engine) as session:
        session.delete(Match, id=id)
        session.commit()
        recalculate_all_ratings()

def get_matches() -> list[Match]:
    with Session(engine) as session:
        return session.exec(select(Match)).all()