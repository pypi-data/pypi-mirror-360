import yaml
import argparse
from rich.console import Console
from rich.table import Table
from .schemas import Meeting
from .solver import ilp_solver
from .export import generate_ics
from .timezones import get_time_in_tz


def main():
    parser = argparse.ArgumentParser(
        description="Find fair meeting times for distributed teams."
    )
    parser.add_argument(
        "participants_file", help="Path to a YAML file with participant data."
    )
    parser.add_argument(
        "--duration", type=int, default=60, help="Meeting duration in minutes."
    )
    parser.add_argument(
        "--weekdays",
        default="Mon,Tue,Wed,Thu,Fri",
        help="Comma-separated list of allowed weekdays.",
    )
    parser.add_argument(
        "--horizon", type=int, default=4, help="Number of occurrences to schedule."
    )
    parser.add_argument("--ics", help="Path to write the output .ics file.")

    args = parser.parse_args()

    console = Console()

    try:
        with open(args.participants_file, "r") as f:
            participants_data = yaml.safe_load(f)
    except FileNotFoundError:
        console.print(
            f"[bold red]Error:[/bold red] Participants file not found at [cyan]{args.participants_file}[/cyan]"
        )
        return

    meeting = Meeting(
        participants=participants_data["participants"],
        duration_minutes=args.duration,
        allowed_weekdays=args.weekdays.split(","),
        horizon=args.horizon,
        min_gap_between_meetings=0,  # Not used in this version
    )

    solution = ilp_solver(meeting)

    if "error" in solution:
        console.print(f"[bold red]Error:[/bold red] {solution['error']}")
    else:
        table = Table(title=f"Fair Meeting Plan ({meeting.horizon} Occurrences)")
        table.add_column("Occurrence", justify="center")
        table.add_column("UTC Time", justify="center")
        for p in meeting.participants:
            table.add_column(f"{p.name} ({p.tz})", justify="center")

        for slot in solution["scheduled_slots"]:
            row = [
                str(slot["occurrence"] + 1),
                slot["slot_utc"].strftime("%Y-%m-%d %H:%M"),
            ]
            for p in meeting.participants:
                local_time = get_time_in_tz(slot["slot_utc"], p.tz)
                row.append(local_time.strftime("%a %H:%M"))
            table.add_row(*row)

        console.print(table)
        console.print(
            f"\n[bold]Max Total Cost (lower is better):[/bold] {solution['max_total_cost']:.2f}"
        )

        if args.ics:
            ics_content = generate_ics(meeting, solution["scheduled_slots"])
            with open(args.ics, "w") as f:
                f.write(ics_content)
            console.print(
                f"\n[bold green]Success:[/bold green] Calendar file saved to [cyan]{args.ics}[/cyan]"
            )


if __name__ == "__main__":
    main()
