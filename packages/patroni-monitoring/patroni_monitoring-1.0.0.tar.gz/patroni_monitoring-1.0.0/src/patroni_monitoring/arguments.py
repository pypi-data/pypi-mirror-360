import argparse

class ValidateNumber(argparse.Action):
    """Custom action to validate that the argument is a positive integer."""
    def __call__(self, parser, namespace, values, option_string=None):
        if values < 0:
            raise argparse.ArgumentTypeError(f"{self.dest} must be a positive integer")
        if not values > 0:
            raise argparse.ArgumentTypeError(f"{self.dest} must be greater than 0")
        setattr(namespace, self.dest, values)

def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Patroni Monitoring CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Patroni API URL",
        default="http://localhost:8008",
    )
    parser.add_argument(
        "--warning",
        type=int,
        help="Warning threshold for replication lag in bytes",
        default=1024,
        action=ValidateNumber
    )
    parser.add_argument(
        "--critical",
        type=int,
        help="Critical threshold for replication lag in bytes",
        default=2048,
        action=ValidateNumber
    )
    parser.add_argument(
        "--delay-warning",
        type=float,
        help="Warning threshold for delay in seconds",
        default=20.0,
        action=ValidateNumber
    )
    parser.add_argument(
        "--delay-critical",
        type=float,
        help="Critical threshold for delay in seconds",
        default=30.0,
        action=ValidateNumber
    )
    parser.add_argument(
        "--log-level",
        type=str,
        help="Logging level",
        choices=["debug", "info", "warning", "error", "critical"],
        default="warning"
    )
    parser.add_argument(
        "--conn-timeout",
        type=int,
        help="Connection timeout in seconds",
        default=5,
        action=ValidateNumber
    )

    return parser.parse_args()