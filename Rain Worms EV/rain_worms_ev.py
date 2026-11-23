"""Exact single-turn EV calculator for the base game Rain Worms / Pickomino.

Input is one JSON object on stdin. Die faces are integers 1 through 6, where
6 represents a worm and is worth 5 points. See README.md for the input shape.
"""

from __future__ import annotations

import json
import math
import argparse
import sys
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

FACES = 6
DICE = 8
FACE_VALUES = (1, 2, 3, 4, 5, 5)  # face 6 is the worm


def tile_worms(tile: int) -> int:
    if not 21 <= tile <= 36:
        raise ValueError(f"tile must be from 21 to 36: {tile}")
    return (tile - 21) // 4 + 1


@lru_cache(maxsize=None)
def _roll_counts(dice: int) -> tuple[tuple[tuple[int, ...], int], ...]:
    """Unique face-count outcomes and their multiplicities among 6**dice rolls."""
    if dice == 0:
        return (((0,) * FACES, 1),)
    result: list[tuple[tuple[int, ...], int]] = []
    counts = [0] * FACES

    def build(face: int, left: int) -> None:
        if face == FACES - 1:
            counts[face] = left
            ways = math.factorial(dice)
            for count in counts:
                ways //= math.factorial(count)
            result.append((tuple(counts), ways))
            return
        for count in range(left + 1):
            counts[face] = count
            build(face + 1, left - count)

    build(0, dice)
    return tuple(result)


@dataclass(frozen=True)
class GameState:
    free_tiles: tuple[int, ...]
    opponent_top: int | None
    own_top: int | None

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> "GameState":
        free_tiles = tuple(sorted(set(raw["free_tiles"])))
        for tile in free_tiles:
            tile_worms(tile)
        opponent = raw.get("opponent_top")
        own = raw.get("own_top")
        if opponent is not None:
            tile_worms(opponent)
        if own is not None:
            tile_worms(own)
        if opponent in free_tiles or own in free_tiles or (opponent is not None and opponent == own):
            raise ValueError("a tile cannot be in more than one location")
        return cls(free_tiles, opponent, own)


class TurnEV:
    """Memoized Bellman recursion over kept dice, with exact roll enumeration."""

    def __init__(self, game: GameState):
        self.game = game

    @staticmethod
    def score(kept: tuple[int, ...]) -> int:
        return sum(c * value for c, value in zip(kept, FACE_VALUES))

    @staticmethod
    def used_mask(kept: tuple[int, ...]) -> int:
        return sum((1 << i) for i, count in enumerate(kept) if count)

    def stop_value(self, kept: tuple[int, ...]) -> float:
        score = self.score(kept)
        if kept[5] == 0:
            return self.bust_value

        outcomes: list[float] = []
        # Claiming the highest free tile at or below the rolled total.
        pool_claims = [tile for tile in self.game.free_tiles if tile <= score]
        if pool_claims:
            outcomes.append(float(tile_worms(max(pool_claims))))
        # A steal requires an exact total and is optional. Its value includes
        # both the tile gained and the same tile removed from the opponent.
        if self.game.opponent_top == score:
            outcomes.append(float(2 * tile_worms(score)))
        return max(outcomes) if outcomes else self.bust_value

    @property
    def bust_value(self) -> float:
        return -float(tile_worms(self.game.own_top)) if self.game.own_top is not None else 0.0

    @lru_cache(maxsize=None)
    def value_after_pick(self, kept: tuple[int, ...]) -> float:
        """Best EV after a pick, before choosing to stop or roll again."""
        left = DICE - sum(kept)
        stop = self.stop_value(kept)
        if left == 0:
            return stop
        roll_value = self._roll_value(kept)
        return max(stop, roll_value)

    def choices_for_roll(self, kept: tuple[int, ...], roll_faces: list[int]) -> dict[str, Any]:
        if len(kept) != FACES or sum(kept) > DICE:
            raise ValueError("kept_counts must contain six counts totaling at most 8")
        if any(not isinstance(n, int) or n < 0 for n in kept):
            raise ValueError("kept_counts must be nonnegative integers")
        if any(not isinstance(face, int) or not 1 <= face <= 6 for face in roll_faces):
            raise ValueError("current_roll faces must be integers from 1 to 6")
        expected = DICE - sum(kept)
        if len(roll_faces) != expected:
            raise ValueError(f"current_roll must contain {expected} dice for the supplied kept_counts")

        counts = tuple(roll_faces.count(face) for face in range(1, 7))
        used = self.used_mask(kept)
        options = []
        for face in range(FACES):
            if counts[face] == 0 or used & (1 << face):
                continue
            next_kept = list(kept)
            next_kept[face] += counts[face]
            next_kept_tuple = tuple(next_kept)
            stop = self.stop_value(next_kept_tuple)
            left = DICE - sum(next_kept_tuple)
            if left == 0:
                continue_value = None
                best = stop
                recommendation = "stop" if stop != self.bust_value or next_kept_tuple[5] else "forced_resolution"
            else:
                continue_value = self._roll_value(next_kept_tuple)
                best = max(stop, continue_value)
                recommendation = "stop" if stop >= continue_value else "roll"
            options.append({
                "face": face + 1,
                "dice_set_aside": counts[face],
                "score_after_pick": self.score(next_kept_tuple),
                "stop_ev": stop,
                "continue_ev": continue_value,
                "ev": best,
                "recommended_next_action": recommendation,
            })
        if not options:
            return {"status": "bust", "ev": self.bust_value, "choices": []}
        return {"status": "ok", "choices": options,
                "recommended_face": max(options, key=lambda item: item["ev"])["face"]}

    def _roll_value(self, kept: tuple[int, ...]) -> float:
        left = DICE - sum(kept)
        used = self.used_mask(kept)
        total = 0.0
        for roll, multiplicity in _roll_counts(left):
            choices = [i for i in range(FACES) if not (used & (1 << i)) and roll[i] > 0]
            if not choices:
                outcome_value = self.bust_value
            else:
                outcome_value = max(
                    self.value_after_pick(tuple(kept[j] + (roll[i] if i == j else 0)
                                                 for j in range(FACES)))
                    for i in choices
                )
            total += multiplicity * outcome_value
        return total / (FACES ** left)


def calculate(request: dict[str, Any]) -> dict[str, Any]:
    game = GameState.from_json(request["game_state"])
    calculator = TurnEV(game)
    kept = tuple(request.get("kept_counts", [0] * FACES))
    result = calculator.choices_for_roll(kept, request["current_roll"])
    result["bust_ev"] = calculator.bust_value
    result["score_before_roll"] = calculator.score(kept)
    return result


def _read_exposed_tile(parts: list[str]) -> int | None:
    if len(parts) != 1:
        raise ValueError("enter one tile number, or 'none'")
    if parts[0].lower() in {"none", "empty"}:
        return None
    try:
        tile = int(parts[0])
    except ValueError as exc:
        raise ValueError("tile must be a number from 21 to 36, or 'none'") from exc
    tile_worms(tile)
    return tile


def _describe_stop(calculator: TurnEV, kept: tuple[int, ...]) -> str:
    score = calculator.score(kept)
    if kept[5] == 0:
        return f"Bust: no worm was set aside. Net worms: {calculator.bust_value:g}."
    pool_claims = [tile for tile in calculator.game.free_tiles if tile <= score]
    steal = calculator.game.opponent_top == score
    pool_tile = max(pool_claims) if pool_claims else None
    candidates = []
    if pool_tile is not None:
        candidates.append((tile_worms(pool_tile), f"take pool tile {pool_tile}"))
    if steal:
        candidates.append((2 * tile_worms(score), f"steal opponent tile {score}"))
    if not candidates:
        return f"Bust: score {score} cannot claim a tile. Net worms: {calculator.bust_value:g}."
    value, action = max(candidates)
    return f"{action} (score {score}); net worms: {value}. Update the board before your next turn."


def run_interactive(input_fn=input, output_fn=print) -> None:
    """Small command loop for entering the live board and each roll."""
    free_tiles: tuple[int, ...] = tuple(range(21, 37))
    own_top: int | None = None
    opponent_top: int | None = None
    kept = (0,) * FACES
    current_roll: list[int] | None = None
    active = False

    output_fn("Rain Worms EV. Type 'help' for commands.")
    while True:
        try:
            line = input_fn("EV> ").strip()
        except (EOFError, KeyboardInterrupt):
            output_fn("Goodbye.")
            return
        if not line:
            continue
        parts = line.split()
        command, args = parts[0].lower(), parts[1:]
        try:
            if command in {"quit", "exit"}:
                output_fn("Goodbye.")
                return
            if command == "help":
                output_fn(
                    "Commands:\n"
                    "  pool <tile>               Add a tile to the pool\n"
                    "  pool -<tile>              Remove a tile from the pool\n"
                    "  mine <tile | none>        Set your exposed tile\n"
                    "  opponent <tile | none>    Set opponent's exposed tile\n"
                    "  status                    Show board and turn state\n"
                    "  start                     Begin/reset a turn\n"
                    "  roll <face ...>           Enter current dice roll (faces 1-6; 6=worm)\n"
                    "  pick <face>               Set aside all dice of that face\n"
                    "  stop                      Stop and resolve the turn\n"
                    "  quit                      Exit"
                )
            elif command == "pool":
                if len(args) != 1:
                    raise ValueError("use 'pool <tile>' to add or 'pool -<tile>' to remove one tile")
                try:
                    signed_tile = int(args[0])
                except ValueError as exc:
                    raise ValueError("pool command needs a tile number from 21 to 36") from exc
                tile = abs(signed_tile)
                tile_worms(tile)
                if signed_tile < 0:
                    if tile not in free_tiles:
                        raise ValueError(f"tile {tile} is not in the free pool")
                    free_tiles = tuple(value for value in free_tiles if value != tile)
                    output_fn(f"Removed {tile} from the free pool.")
                else:
                    if tile in free_tiles:
                        raise ValueError(f"tile {tile} is already in the free pool")
                    if tile in (own_top, opponent_top):
                        raise ValueError(f"tile {tile} is currently an exposed player tile")
                    free_tiles = tuple(sorted((*free_tiles, tile)))
                    output_fn(f"Added {tile} to the free pool.")
            elif command == "mine":
                new_top = _read_exposed_tile(args)
                proposed_pool = tuple(tile for tile in free_tiles if tile != new_top)
                GameState.from_json({"free_tiles": list(proposed_pool), "own_top": new_top,
                                     "opponent_top": opponent_top})
                removed = new_top in free_tiles
                own_top, free_tiles = new_top, proposed_pool
                output_fn(f"Your exposed tile: {own_top if own_top is not None else 'none'}")
                if removed:
                    output_fn(f"Automatically removed tile {own_top} from the free pool.")
            elif command == "opponent":
                new_top = _read_exposed_tile(args)
                proposed_pool = tuple(tile for tile in free_tiles if tile != new_top)
                GameState.from_json({"free_tiles": list(proposed_pool), "own_top": own_top,
                                     "opponent_top": new_top})
                removed = new_top in free_tiles
                opponent_top, free_tiles = new_top, proposed_pool
                output_fn(f"Opponent exposed tile: {opponent_top if opponent_top is not None else 'none'}")
                if removed:
                    output_fn(f"Automatically removed tile {opponent_top} from the free pool.")
            elif command == "status":
                output_fn(f"Free pool: {list(free_tiles)}")
                output_fn(f"Your exposed tile: {own_top if own_top is not None else 'none'}; "
                          f"opponent exposed tile: {opponent_top if opponent_top is not None else 'none'}")
                output_fn(f"Turn: {'active' if active else 'not started'}; "
                          f"kept dice: {list(kept)}; score: {TurnEV.score(kept)}")
                if current_roll is not None:
                    output_fn(f"Current roll: {current_roll}")
            elif command == "start":
                GameState.from_json({"free_tiles": list(free_tiles), "own_top": own_top,
                                     "opponent_top": opponent_top})
                kept = (0,) * FACES
                current_roll = None
                active = True
                output_fn("Turn started. Enter the first roll with 'roll <8 faces>'.")
            elif command == "roll":
                if not active:
                    raise ValueError("start a turn first")
                if current_roll is not None:
                    raise ValueError("choose a face with 'pick <face>' before entering the next roll")
                try:
                    roll = [int(value) for value in args]
                except ValueError as exc:
                    raise ValueError("roll faces must be integers from 1 to 6") from exc
                calculator = TurnEV(GameState(free_tiles, opponent_top, own_top))
                result = calculator.choices_for_roll(kept, roll)
                if result["status"] == "bust":
                    output_fn(f"Bust: no unused face appeared. Net worms: {calculator.bust_value:g}.")
                    active = False
                    current_roll = None
                    continue
                current_roll = roll
                output_fn("Set-aside choices (EV includes optimal future play):")
                for choice in result["choices"]:
                    future = "forced resolution" if choice["continue_ev"] is None else (
                        f"stop {choice['stop_ev']:.3f}, continue {choice['continue_ev']:.3f}; "
                        f"then {choice['recommended_next_action']}"
                    )
                    output_fn(f"  face {choice['face']} ({choice['dice_set_aside']} dice), "
                              f"score {choice['score_after_pick']}: EV {choice['ev']:.3f} [{future}]")
                output_fn(f"Recommended face: {result['recommended_face']}. Choose with 'pick <face>'.")
            elif command == "pick":
                if not active or current_roll is None:
                    raise ValueError("enter a roll first")
                if len(args) != 1:
                    raise ValueError("use 'pick <face>'")
                try:
                    face = int(args[0])
                except ValueError as exc:
                    raise ValueError("face must be an integer from 1 to 6") from exc
                calculator = TurnEV(GameState(free_tiles, opponent_top, own_top))
                result = calculator.choices_for_roll(kept, current_roll)
                choice = next((item for item in result["choices"] if item["face"] == face), None)
                if choice is None:
                    raise ValueError("that face is not an available choice in the current roll")
                updated = list(kept)
                updated[face - 1] += choice["dice_set_aside"]
                kept = tuple(updated)
                current_roll = None
                output_fn(f"Set aside {choice['dice_set_aside']} die/dice showing {face}. "
                          f"Score: {calculator.score(kept)}.")
                if sum(kept) == DICE:
                    output_fn(_describe_stop(calculator, kept))
                    active = False
                else:
                    remaining = DICE - sum(kept)
                    stop_ev = calculator.stop_value(kept)
                    roll_ev = calculator._roll_value(kept)
                    recommendation = "stop" if stop_ev >= roll_ev else "roll"
                    output_fn(f"Stop now: EV {stop_ev:.3f} worms. "
                              f"Roll the remaining {remaining} dice: EV {roll_ev:.3f} worms.")
                    output_fn(f"Recommended action: {recommendation.upper()}. "
                              f"Enter 'stop' or 'roll <{remaining} faces>'.")
            elif command == "stop":
                if not active or sum(kept) == 0:
                    raise ValueError("set aside at least one face before stopping")
                if current_roll is not None:
                    raise ValueError("choose a face from the current roll before stopping")
                calculator = TurnEV(GameState(free_tiles, opponent_top, own_top))
                output_fn(_describe_stop(calculator, kept))
                active = False
                current_roll = None
            else:
                output_fn("Unknown command. Type 'help' to see available commands.")
        except (ValueError, KeyError) as exc:
            output_fn(f"Error: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Rain Worms / Pickomino turn EV calculator")
    parser.add_argument("--interactive", action="store_true", help="run keyboard command mode")
    args = parser.parse_args()
    if args.interactive or sys.stdin.isatty():
        run_interactive()
        return
    try:
        request = json.load(sys.stdin)
        print(json.dumps(calculate(request), indent=2))
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
