import datetime as dt
import importlib
import json
from pathlib import Path

from fastapi.encoders import jsonable_encoder
from sqlalchemy import inspect, text

from api.db import Base, db_engine, db_session

for path in Path("./api/models").glob("*.py"):
    if path.stem != "__init__":
        importlib.import_module(f"api.models.{path.stem}")


def backup_database(
    *,
    inspector,
    db_session,
    file_path: Path = None,
):
    """
    DBのすべてのデータを一つのjsonファイルバックアップする

    ex)
    {
        "users": [
            {
                "id": 1,
                "email": "
    ...
    """
    if file_path is None:
        dir_path = Path(__file__).parent / "db_back_up"
        dir_path.mkdir(exist_ok=True)
        ext_str = (
            dt.datetime.now().astimezone().replace(microsecond=0).isoformat()
        )
        # file name e.g. backup_2021-01-01T00:00:00+09:00.json
        file_path = dir_path / f"backup_{ext_str}.json"

    with db_session() as session:
        table_names = inspector.get_table_names()
        data = {}

        for table_name in table_names:
            result = session.execute(text(f"SELECT * FROM {table_name}"))
            rows = [row._asdict() for row in result]
            data[table_name] = rows

    if all(len(v) == 0 for v in data.values()):
        print("データがありません、バックアップしません")
        return

    with file_path.open("w") as f:
        json.dump(jsonable_encoder(data), f, ensure_ascii=False, indent=4)


def reset_database(*, inspector, db_engine, db_session):
    table_names = inspector.get_table_names()

    with db_session() as session:
        for table_name in table_names:
            session.execute(text(f"DROP TABLE {table_name}"))

        session.commit()

    Base.metadata.create_all(bind=db_engine)


if __name__ == "__main__":
    db_engine.echo = False
    inspector = inspect(db_engine)

    print("バックアップ中...")
    try:
        backup_database(
            inspector=inspector,
            db_session=db_session,
        )
    except Exception as e:
        print(f"バックアップに失敗しました: {e}")
        if input("続行するとデータが消えます、続行しますか？(y/N)") != "y":
            raise

    print("リセット中...")
    reset_database(
        inspector=inspector,
        db_engine=db_engine,
        db_session=db_session,
    )
    print("完了")
