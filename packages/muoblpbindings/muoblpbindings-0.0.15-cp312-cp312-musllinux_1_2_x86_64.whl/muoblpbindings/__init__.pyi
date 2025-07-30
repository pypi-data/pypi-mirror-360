def equal_shares_utils(voters: list[str],
                 projects: list[str],
                 cost: dict[str, float],
                 approvals_utilities: dict[str, list[tuple[str, int]]],
                 total_utility: dict[str, int],
                 total_budget: float) -> list[str]:
    """
    Equal shares baseline
    """

def equal_shares_add1(voters: list[str],
                 projects: list[str],
                 cost: dict[str, float],
                 approvals_utilities: dict[str, list[tuple[str, int]]],
                 total_utility: dict[str, int],
                 total_budget: float) -> list[str]:
    """
    Equal shares Add1
    """

def equal_shares_utils_precomputed(voters: list[str],
                 projects: list[str],
                 cost: dict[str, float],
                 approvals_utilities: dict[str, list[tuple[str, int]]],
                 total_utility: dict[str, int],
                 total_budget: float,
                 budget: dict[str, float],
                 winners: list[str]) -> tuple[list[str], dict[str, float]]:
    """
    Equal shares precomputed winners implementation
    """
