from sqlalchemy import create_engine
from sqlalchemy import Column, DateTime, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session

Base = declarative_base()


class MoistureReading(Base):
    __tablename__ = "reading"

    id = Column(Integer, primary_key=True)
    reading = Column(Float)
    date = Column(DateTime)

    def __repr__(self):
        return "<User(reading='%s', date='%s')>" % (
            self.reading, self.date)


class WateringEvent(Base):
    __tablename__ = "watering"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    duration = Column(Integer)

    def __repr__(self):
        return "<User(date='%s', duration='%s')>" % (
            self.date, self.duration)

from sqlalchemy.orm import sessionmaker

def init_db():
    engine = create_engine('sqlite:///waterer.db?check_same_thread=False', echo=False)
    Session = scoped_session(sessionmaker(bind=engine))
    Base.metadata.create_all(engine)
    return Session()


if __name__ == "__main__":
    engine = create_engine('sqlite:///waterer.db?check_same_thread=False', echo=False)
    db = Base.metadata.create_all(engine)
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    import pdb;pdb.set_trace()
    # session = Session()
    # from datetime import datetime
    # event = MoistureReading(reading=100, date=datetime.now())
    # # session.add(event)
    # # session.flush()
    # # session.commit()
    # # session.flush()
    # print(session.query(MoistureReading.reading, MoistureReading.date).all())
    # print(session.query(WateringEvent.duration).all())
