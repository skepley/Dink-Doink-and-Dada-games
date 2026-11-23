import unittest

from rain_worms_ev import GameState, TurnEV, calculate, run_interactive, tile_worms


class TurnEVTests(unittest.TestCase):
    def test_tile_worm_counts(self):
        self.assertEqual([tile_worms(x) for x in (21, 24, 25, 28, 29, 32, 33, 36)],
                         [1, 1, 2, 2, 3, 3, 4, 4])

    def test_exact_steal_is_double_net_value(self):
        ev = TurnEV(GameState((), 25, None))
        kept = (0, 0, 0, 0, 0, 5)  # 25 points and a worm
        self.assertEqual(ev.stop_value(kept), 4.0)

    def test_pool_claim_uses_highest_available_at_or_below_score(self):
        ev = TurnEV(GameState((21, 24, 29), None, None))
        kept = (0, 0, 0, 0, 0, 5)  # 25 points and a worm
        self.assertEqual(ev.stop_value(kept), 1.0)

    def test_bust_penalty_is_own_top_worm_count(self):
        ev = TurnEV(GameState((), None, 29))
        self.assertEqual(ev.bust_value, -3.0)

    def test_unavailable_roll_faces_force_bust(self):
        ev = TurnEV(GameState((21,), None, 21))
        result = ev.choices_for_roll((1, 0, 0, 0, 0, 0), [1] * 7)
        self.assertEqual(result["status"], "bust")
        self.assertEqual(result["ev"], -1.0)

    def test_request_reports_only_faces_in_current_roll(self):
        request = {
            "game_state": {"free_tiles": [21, 22, 23, 24], "own_top": None},
            "kept_counts": [0] * 6,
            "current_roll": [1, 2, 2, 3, 4, 5, 5, 6],
        }
        result = calculate(request)
        self.assertEqual({item["face"] for item in result["choices"]}, {1, 2, 3, 4, 5, 6})
        self.assertIn(result["recommended_face"], {1, 2, 3, 4, 5, 6})

    def test_probability_of_roll_outcomes_sums_to_one(self):
        from rain_worms_ev import _roll_counts
        for dice in range(9):
            self.assertEqual(sum(ways for _, ways in _roll_counts(dice)), 6 ** dice)

    def test_interactive_commands_accept_roll_and_pick(self):
        commands = iter([
            "pool 21 22 23 24 25 26", "mine none", "opponent none", "start",
            "roll 6 6 6 6 6 6 1 2", "pick 6", "quit",
        ])
        output = []
        run_interactive(lambda _prompt: next(commands), output.append)
        self.assertTrue(any("Recommended face: 6" in line for line in output))
        self.assertTrue(any("Stop now: EV" in line and "Roll the remaining 2 dice: EV" in line
                            for line in output))
        self.assertTrue(any("Recommended action:" in line for line in output))

    def test_pool_add_remove_and_exposed_tiles_update_pool(self):
        commands = iter([
            "pool -25", "pool -25", "pool 25", "pool 25", "mine 26",
            "opponent 27", "status", "quit",
        ])
        output = []
        run_interactive(lambda _prompt: next(commands), output.append)
        self.assertTrue(any("Removed 25" in line for line in output))
        self.assertTrue(any("tile 25 is not in the free pool" in line for line in output))
        self.assertTrue(any("Added 25" in line for line in output))
        self.assertTrue(any("tile 25 is already in the free pool" in line for line in output))
        self.assertTrue(any("Automatically removed tile 26" in line for line in output))
        self.assertTrue(any("Automatically removed tile 27" in line for line in output))
        self.assertTrue(any("Free pool: [21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 34, 35, 36]" == line
                            for line in output))


if __name__ == "__main__":
    unittest.main()
