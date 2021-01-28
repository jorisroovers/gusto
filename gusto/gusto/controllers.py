from .models import GustoModel

class GustoController:

    def __init__(self, request, model: GustoModel = None) -> None:
        self.request = request
        self.db = self.request.app.state.db_session
        self.model = model

    @staticmethod
    def as_dict(object):
        return [o.as_dict() for o in object]

    def list(self):
        return self.as_dict(self.db.query(self.model).all())

    def filter(self, *args):
        return self.as_dict(self.db.query(self.model).filter(*args))

    def create(self, obj):
        self.db.add(obj)
        self.db.commit()

    def delete(self, filter):
        self.db.query(self.model).filter(filter).delete()
        self.db.commit()
