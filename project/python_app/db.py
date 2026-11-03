"""Прямой доступ к PostgreSQL через psycopg2.

Модуль предоставляет те же функции-обёртки (select_all, select_one,
insert, update, delete), что и прежний REST-клиент, но работает
напрямую с базой данных PostgreSQL через psycopg2 с RealDictCursor.
"""

import psycopg2
import psycopg2.extras
from contextlib import contextmanager

from config import DATABASE_URL


def _connect():
    """Создаёт новое подключение к PostgreSQL."""
    return psycopg2.connect(DATABASE_URL)


@contextmanager
def get_conn():
    """Контекстный менеджер: открывает и закрывает соединение."""
    conn = _connect()
    try:
        yield conn
    finally:
        conn.close()


def _execute_query(query, params=None, fetch='all'):
    """Выполняет SELECT и возвращает результат в виде списка dict."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch == 'one':
                return cur.fetchone()
            return cur.fetchall()


def select_all(table, select='*', order=None, filters=None, limit=None):
    """Возвращает список dict из таблицы.

    :param table: имя таблицы
    :param select: колонки (по умолчанию '*')
    :param order: 'column.direction' (например 'created_at.desc')
    :param filters: словарь {column: value} (точное совпадение)
    :param limit: ограничение количества строк
    """
    query = f'SELECT {select} FROM {table}'
    params = []
    conditions = []

    if filters:
        for col, val in filters.items():
            conditions.append(f'{col} = %s')
            params.append(val)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    if order:
        parts = order.split('.')
        col = parts[0]
        direction = parts[1].upper() if len(parts) > 1 else 'ASC'
        query += f' ORDER BY {col} {direction}'

    if limit:
        query += ' LIMIT %s'
        params.append(limit)

    return _execute_query(query, params, fetch='all')


def select_one(table, select='*', filters=None):
    """Возвращает один dict или None."""
    query = f'SELECT {select} FROM {table}'
    params = []
    conditions = []

    if filters:
        for col, val in filters.items():
            conditions.append(f'{col} = %s')
            params.append(val)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' LIMIT 1'

    result = _execute_query(query, params, fetch='one')
    return dict(result) if result else None


def insert(table, payload):
    """Вставляет строку и возвращает её (включая сгенерированные поля).

    :param table: имя таблицы
    :param payload: dict с данными для вставки
    :return: dict — вставленная строка
    """
    columns = list(payload.keys())
    placeholders = ['%s'] * len(columns)
    values = [payload[c] for c in columns]

    col_str = ', '.join(columns)
    val_str = ', '.join(placeholders)
    query = f'INSERT INTO {table} ({col_str}) VALUES ({val_str}) RETURNING *'

    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, values)
            conn.commit()
            result = cur.fetchone()
            return dict(result) if result else None


def update(table, payload, eq_field, eq_value):
    """Обновляет строки по условию eq_field=eq_value и возвращает обновлённую строку.

    :param table: имя таблицы
    :param payload: dict с обновляемыми полями
    :param eq_field: имя колонки для условия
    :param eq_value: значение для условия
    :return: dict — обновлённая строка
    """
    set_parts = [f'{col} = %s' for col in payload.keys()]
    values = list(payload.values())
    values.append(eq_value)

    set_str = ', '.join(set_parts)
    query = f'UPDATE {table} SET {set_str} WHERE {eq_field} = %s RETURNING *'

    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, values)
            conn.commit()
            result = cur.fetchone()
            return dict(result) if result else None


def delete(table, eq_field, eq_value):
    """Удаляет строки по условию eq_field=eq_value."""
    query = f'DELETE FROM {table} WHERE {eq_field} = %s'
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (eq_value,))
            conn.commit()


def select_join(table, select, joins, filters=None, order=None):
    """SELECT с JOIN. joins — список (table, on_clause)."""
    query = f'SELECT {select} FROM {table}'
    for jt, on in joins:
        query += f' JOIN {jt} ON {on}'

    params = []
    conditions = []
    if filters:
        for col, val in filters.items():
            conditions.append(f'{col} = %s')
            params.append(val)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    if order:
        parts = order.split('.')
        col = parts[0]
        direction = parts[1].upper() if len(parts) > 1 else 'ASC'
        query += f' ORDER BY {col} {direction}'

    return _execute_query(query, params, fetch='all')