from sqlalchemy import text
from sqlalchemy.orm import Session


def get_done(db: Session, task_id: int):
    sql = text(
        """
        SELECT * FROM dones
        WHERE id = :id
        """
    )
    params = {"id": task_id}

    print(f"SQL: {sql}\nParams: {params}")
    result = db.execute(sql, params).first()
    if result is not None:
        result = result._asdict()
    print(f"DB操作の結果: {result}")

    return result


def create_done(db: Session, task_id: int):
    sql = text(
        """
        INSERT INTO dones (id)
        VALUES (:id)
        """
    )
    params = {"id": task_id}

    print(f"SQL: {sql}\nParams: {params}")
    db.execute(sql, params)
    db.commit()
    new_done = get_done(db, task_id)
    print(f"DB操作の結果: {new_done}")

    return new_done


def delete_done(db: Session, original: dict):
    sql = text(
        """
        DELETE FROM dones
        WHERE id = :id
        """
    )
    params = {"id": original.get("id")}

    print(f"SQL: {sql}\nParams: {params}")
    db.execute(sql, params)
    db.commit()
