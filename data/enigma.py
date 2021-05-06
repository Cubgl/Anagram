import sqlalchemy
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase

class Enigma(SqlAlchemyBase):
    __tablename__ = 'enigma'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    question = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    answer = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    subquestion = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    subanswer = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    helper = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    good_answers = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    bad_answers = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    difficult = sqlalchemy.Column(sqlalchemy.Float, nullable=True)

    def set_answer(self, answer):
        self.answer = generate_password_hash(answer)

    def check_answer(self, answer):
        return check_password_hash(self.answer, answer)

    def set_subanswer(self, subanswer):
        self.subanswer = generate_password_hash(subanswer)

    def check_subanswer(self, subanswer):
        return check_password_hash(self.subanswer, subanswer)
