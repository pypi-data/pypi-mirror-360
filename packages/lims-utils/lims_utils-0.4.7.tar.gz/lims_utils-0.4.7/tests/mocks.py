from sqlalchemy import Select


class FakeExecute:
    def all(self):
        return ["a", "b", "c"]

    def scalar_one(self):
        return 1


class FakeSession:
    def close(self):
        pass

    def rollback(self):
        pass

    def execute(self, *args, **kwargs):
        return FakeExecute()

    def scalars(self, *args, **kwargs):
        return FakeExecute()


def query_eq(q1: Select, q2: Select):
    return str(q1.compile(compile_kwargs={"literal_binds": True})) == str(
        q2.compile(compile_kwargs={"literal_binds": True})
    )
