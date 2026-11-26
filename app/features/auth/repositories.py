from splent_framework.repositories.BaseRepository import BaseRepository

from app.features.auth.models import RecoveryCode, User


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def create(self, commit: bool = True, **kwargs):
        password = kwargs.pop("password")
        instance = self.model(**kwargs)
        instance.set_password(password)
        self.session.add(instance)
        if commit:
            self.session.commit()
        else:
            self.session.flush()
        return instance

    def get_by_email(self, email: str):
        return self.model.query.filter_by(email=email).first()


class RecoveryCodeRepository(BaseRepository):
    def __init__(self):
        super().__init__(RecoveryCode)

    def get_by_user(self, user_id: int) -> list[RecoveryCode]:
        return self.model.query.filter_by(user_id=user_id).order_by(self.model.id).all()

    def get_unused_by_user(self, user_id: int) -> list[RecoveryCode]:
        return self.model.query.filter_by(user_id=user_id, used_at=None).order_by(self.model.id).all()

    def get_unused_by_user_and_hash(self, user_id: int, code_hash: str) -> RecoveryCode | None:
        return self.model.query.filter_by(user_id=user_id, code_hash=code_hash, used_at=None).first()
