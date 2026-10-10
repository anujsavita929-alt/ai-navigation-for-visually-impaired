"""Conservative rule-based local guidance engine."""


class NavigationEngine:
    def decide(self, free_space):
        regions = free_space["regions"]
        centre = regions.get("centre", "unknown")

        if centre == "blocked":
            alternatives = [
                direction for direction in ("left", "right")
                if regions.get(direction) == "caution"
            ]
            if alternatives:
                direction = alternatives[0]
                return {
                    "level": "warning",
                    "text": (
                        f"Obstacle detected ahead. {direction.capitalize()} appears less obstructed, "
                        "but verify before moving."
                    ),
                    "direction": direction,
                }
            if all(regions.get(direction) == "blocked" for direction in ("left", "centre", "right")):
                return {
                    "level": "danger",
                    "text": "Obstacles detected across the view. Stop and assess your surroundings.",
                    "direction": None,
                }
            return {
                "level": "warning",
                "text": "Obstacle detected ahead. Stop and assess your surroundings.",
                "direction": None,
            }

        if centre == "unknown":
            return {
                "level": "caution",
                "text": (
                    "I cannot verify that the path ahead is clear. Please proceed cautiously "
                    "and use your usual mobility aid."
                ),
                "direction": None,
            }
        if centre == "caution":
            return {
                "level": "caution",
                "text": "Possible obstacle ahead. Slow down and check the path.",
                "direction": None,
            }
        return {
            "level": "info",
            "text": "No clear obstruction detected in the centre region, but the path is not verified safe.",
            "direction": None,
        }
