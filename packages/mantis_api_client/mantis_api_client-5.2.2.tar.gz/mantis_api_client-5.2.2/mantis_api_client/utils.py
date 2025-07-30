# -*- coding: utf-8 -*-
import json
import time
from typing import Dict
from typing import List

from alive_progress import alive_bar
from mantis_scenario_model.lab_model import ScenarioExecutionStatus
from urllib3.exceptions import NewConnectionError

from mantis_api_client import scenario_api

try:
    from colorama import init
    from termcolor import colored

    HAS_COLOUR = True
except ImportError:
    HAS_COLOUR = False

# Initialize colorama
if HAS_COLOUR:
    init(autoreset=True)
else:
    # Override colored function to return first argument
    def colored(text: object, *args: Any, **kwargs: Any) -> str:  # type: ignore # noqa
        return str(text)


def wait_lab(lab_id: str) -> None:
    notifications_output: List[Dict[str, str]] = []

    print("[+] Notifications:")

    with alive_bar(
        refresh_secs=0.08,
        spinner=None,
        enrich_print=False,
        stats=False,
        monitor=False,
        theme="classic",
    ) as bar:
        nb_requests_failed = 0
        while True:
            in_error = False

            time.sleep(1)

            # Retrieve current lab status and associated
            # notifications. Only display error message if it occurs
            # multiple times.
            try:
                lab = scenario_api.fetch_lab(lab_id)
            except NewConnectionError as e:
                in_error = True
                nb_requests_failed += 1
                if nb_requests_failed > 10:
                    print(e)
            except Exception as e:
                in_error = True
                nb_requests_failed += 1
                if nb_requests_failed > 10:
                    print(e)

            # Exit in case of multiple failures when fetching lab status
            if nb_requests_failed > 10:
                break

            if in_error:
                continue

            # Retrieve lab notifications
            notifications = scenario_api.fetch_lab_notifications(lab_id)

            # Only display new notifications
            new_output = notifications[len(notifications_output) :]
            for event in new_output:
                event = json.loads(event)
                print(f"⚡ {event['event_datetime']} UTC - {event['event_data']}")
            notifications_output = notifications

            # Display current macro step (deploy, provisioning, attack, etc.)
            if "status" in lab:
                bar.text(lab["status"])
                if lab["status"].rstrip() == "PAUSE":
                    with bar.pause():
                        print("Press Enter to continue the scenario...")
                        input()
                        scenario_api.resume_lab(lab_id)
                        lab = scenario_api.fetch_lab(lab_id)
            else:
                bar()

            # Condition to break loop: the scenario execution
            # has finished, either because it has been cancelled or
            # because it has successfully finished
            if "status" in lab and lab["status"] in [
                ScenarioExecutionStatus.scenario_finished.value,
                ScenarioExecutionStatus.completed.value,
                ScenarioExecutionStatus.cancelled.value,
                ScenarioExecutionStatus.error.value,
            ]:
                break
