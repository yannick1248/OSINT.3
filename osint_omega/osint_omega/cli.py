"""Interface en ligne de commande — ``python -m osint_omega``."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from osint_omega import __version__
from osint_omega.engine import Engine, detect_target_type
from osint_omega.types import Scope, Target, TargetType

LEGAL_BANNER = (
    "OSINT OMEGA — usage légal et éthique uniquement. "
    "Toute mission doit déclarer un périmètre (--scope). "
    "Les requêtes sont journalisées."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="osint-omega",
        description=LEGAL_BANNER,
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--target",
        default=None,
        help="Valeur de la cible (requis sauf si --list-tools).",
    )
    parser.add_argument(
        "--type",
        choices=[t.value for t in TargetType],
        default=None,
        help="Type de cible (auto-détecté si omis).",
    )
    parser.add_argument(
        "--scope",
        choices=[s.value for s in Scope],
        default=Scope.SANDBOX_TEST.value,
        help="Périmètre légal déclaré.",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        default=None,
        help="Restreindre à une liste d'outils (ex: --only crtsh subfinder).",
    )
    parser.add_argument(
        "--actor",
        default="anonymous",
        help="Identifiant de l'opérateur (pour l'audit trail).",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Affiche le JSON indenté plutôt que compact.",
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="Liste les outils enregistrés et quitte.",
    )
    return parser


async def _run(args: argparse.Namespace) -> dict:
    engine = Engine()
    try:
        if args.list_tools:
            return {"tools": engine.describe_tools()}
        if not args.target:
            raise SystemExit("error: --target est requis (ou utilisez --list-tools).")
        target = (
            Target(value=args.target, type=TargetType(args.type))
            if args.type
            else detect_target_type(args.target)
        )
        mission = await engine.run(
            target,
            scope=Scope(args.scope),
            only=args.only,
            actor_id=args.actor,
        )
        return mission.model_dump(mode="json")
    finally:
        engine.close()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    payload = asyncio.run(_run(args))
    indent = 2 if args.pretty else None
    json.dump(payload, sys.stdout, indent=indent, ensure_ascii=False, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
