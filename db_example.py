
import logging
import os
import random
import time
import uuid
from argparse import ArgumentParser, RawTextHelpFormatter

import psycopg
from psycopg.errors import SerializationFailure, Error
from psycopg.rows import namedtuple_row


def create_accounts(conn):
    id1 = uuid.uuid4()
    id2 = uuid.uuid4()
    with conn.cursor() as cur:
        for row in cur.execute("SHOW TABLES"):
            print(row)
    with conn.cursor() as cur:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS test_db_accounts (id UUID PRIMARY KEY, balance INT)"
        )
    with conn.cursor() as cur:
        cur.execute(
            "UPSERT INTO test_db_foo_1 (foo) VALUES (123)"
        )
        logging.debug("%s", cur.statusmessage)

    with conn.cursor() as cur:
        cur.execute(
            "UPSERT INTO test_db_accounts (id, balance) VALUES (%s, 1000), (%s, 250)", (id1, id2))
        logging.debug("create_accounts(): status message: %s",
                      cur.statusmessage)
    with conn.cursor() as cur:
        for row in cur.execute("SHOW TABLES"):
            print(row)
    conn.commit()
    return [id1, id2]


def delete_accounts(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM test_db_accounts")
        logging.debug("delete_accounts(): status message: %s",
                      cur.statusmessage)
    conn.commit()


def print_balances(conn):
    with conn.cursor() as cur:
        print(f"Balances at {time.asctime()}:")
        for row in cur.execute("SELECT id, balance FROM test_db_accounts"):
            print("account id: {0}  balance: ${1:2d}".format(row.id, row.balance))


def transfer_funds(conn, frm, to, amount):
    with conn.cursor() as cur:

        # Check the current balance.
        cur.execute("SELECT balance FROM test_db_accounts WHERE id = %s", (frm,))
        from_balance = cur.fetchone()[0]
        if from_balance < amount:
            raise RuntimeError(
                f"insufficient funds in {frm}: have {from_balance}, need {amount}"
            )

        # Perform the transfer.
        cur.execute(
            "UPDATE test_db_accounts SET balance = balance - %s WHERE id = %s", (
                amount, frm)
        )
        cur.execute(
            "UPDATE test_db_accounts SET balance = balance + %s WHERE id = %s", (
                amount, to)
        )

    logging.debug("transfer_funds(): status message: %s", cur.statusmessage)
    # conn.commit()
    logging.debug("Committed")


def run_transaction(conn, op, max_retries=3):
    """
    Execute the operation *op(conn)* retrying serialization failure.

    If the database returns an error asking to retry the transaction, retry it
    *max_retries* times before giving up (and propagate it).
    """
    # leaving this block the transaction will commit or rollback
    # (if leaving with an exception)
    with conn.transaction():
        for retry in range(1, max_retries + 1):
            try:
                op(conn)

                # If we reach this point, we were able to commit, so we break
                # from the retry loop.
                return

            except SerializationFailure as e:
                # This is a retry error, so we roll back the current
                # transaction and sleep for a bit before retrying. The
                # sleep time increases for each failed transaction.
                logging.debug("got error: %s", e)
                conn.rollback()
                logging.debug("EXECUTE SERIALIZATION_FAILURE BRANCH")
                sleep_seconds = (2**retry) * 0.1 * (random.random() + 0.5)
                logging.debug("Sleeping %s seconds", sleep_seconds)
                time.sleep(sleep_seconds)

            except psycopg.Error as e:
                logging.debug("got error: %s", e)
                logging.debug("EXECUTE NON-SERIALIZATION_FAILURE BRANCH")
                raise e

        raise ValueError(
            f"transaction did not succeed after {max_retries} retries")


def main():
    opt = parse_cmdline()
    logging.basicConfig(level=logging.DEBUG if opt.verbose else logging.INFO)
    try:
        # Attempt to connect to cluster with connection string provided to
        # script. By default, this script uses the value saved to the
        # DATABASE_URL environment variable.
        # For information on supported connection string formats, see
        # https://www.cockroachlabs.com/docs/stable/connect-to-the-database.html.
        db_url = opt.dsn
        conn = psycopg.connect(db_url, 
                               application_name="$ docs_simplecrud_psycopg3", 
                               row_factory=namedtuple_row)
        ids = create_accounts(conn)
        print_balances(conn)
            
        amount = 100
        toId = ids.pop()
        fromId = ids.pop()

        try:
            run_transaction(conn, lambda conn: transfer_funds(conn, fromId, toId, amount))
        except ValueError as ve:
            # Below, we print the error and continue on so this example is easy to
            # run (and run, and run...).  In real code you should handle this error
            # and any others thrown by the database interaction.
            logging.debug("run_transaction(conn, op) failed: %s", ve)
            pass
        except psycopg.Error as e:
            logging.debug("got error: %s", e)
            raise e

        # fromId = uuid.UUID("00e15e46-2730-47d8-b852-bc6f12c6812a")
        # toId = uuid.UUID("0dd006c1-8b31-4877-a798-f25b3612b707")
        logging.debug("uuids: %s %s", fromId, toId)
        try:
            run_transaction(conn, lambda conn: transfer_funds(conn, fromId, toId, amount))
        except ValueError as ve:
            # Below, we print the error and continue on so this example is easy to
            # run (and run, and run...).  In real code you should handle this error
            # and any others thrown by the database interaction.
            logging.debug("run_transaction(conn, op) failed: %s", ve)
            pass
        except psycopg.Error as e:
            logging.debug("got error: %s", e)
            raise e

        print_balances(conn)

        # delete_accounts(conn)
    except Exception as e:
        logging.fatal("database connection failed")
        logging.fatal(e)
        return


def parse_cmdline():
    parser = ArgumentParser(description=__doc__,
                            formatter_class=RawTextHelpFormatter)

    parser.add_argument("-v", "--verbose",
                        action="store_true", help="print debug info")

    parser.add_argument(
        "dsn",
        default=os.environ.get("DATABASE_URL"),
        nargs="?",
        help="""\
database connection string\
 (default: value of the DATABASE_URL environment variable)
            """,
    )

    opt = parser.parse_args()
    if opt.dsn is None:
        parser.error("database connection string not set")
    return opt


if __name__ == "__main__":
    main()
