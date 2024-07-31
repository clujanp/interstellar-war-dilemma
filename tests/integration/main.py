from .test_user import test_cases_user
from . import all
from .core import TestBank


if __name__ == "__main__":
    print("Start!")

    print("\n  Users tests 👤")
    users = test_cases_user(auth_data={}, roles=[])

    percents = [test_set.percent for test_set in all]
    avg = sum(percents) / len(percents)
    print(f"\nEnd! 🏁 | compliance {avg} {TestBank.get_icon(avg)}\n")
