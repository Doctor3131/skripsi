"""Read-only Neo4j connectivity smoke check."""

import logging

from neo4j import GraphDatabase

from fsm_graphrag.config import load_settings
from fsm_graphrag.logging_config import configure_logging


def main() -> int:
    try:
        settings = load_settings()
        configure_logging(settings.log_level)
        logger = logging.getLogger(__name__)
        with GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        ) as driver:
            driver.verify_connectivity()
            with driver.session(database=settings.neo4j_database) as session:
                record = session.run("RETURN 1 AS ok").single()
                if record is None or record["ok"] != 1:
                    raise RuntimeError("Neo4j returned an unexpected smoke-check result")
        logger.info("Neo4j connectivity smoke check passed")
        return 0
    except Exception:
        logging.getLogger(__name__).exception("Neo4j connectivity smoke check failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
