from time import sleep
from datetime import datetime, timedelta
import random
from threading import Event
import time
from rich import print

from linkiq.model.schedule import Schedule
from linkiq.model.db_client import DBClient
from linkiq.controller.li_handler import LIHandler
from linkiq.controller.view_handler import LIViewHandler
from linkiq.controller.post_handler import LIPostHandler
from linkiq.controller.reaction_handler import LIReactionHandler
from linkiq.controller.profile_handler import LIProfileHandler
from linkiq.controller.message_handler import LIMessageHandler

class Scheduler:

    PROFILE_VIEW = "PROFILE_VIEW"
    POST_REACTION = "POST_REACTION"
    PROFILE_ANALYSIS = "PROFILE_ANALYSIS"
    LEAD_OUTREACH = "LEAD_OUTREACH"

    TASKS = [PROFILE_VIEW, POST_REACTION, PROFILE_ANALYSIS, LEAD_OUTREACH]

    START_HOUR = 9
    END_HOUR = 21
    POST_ANALYSIS_DAYS = [4, 5, 6] #Fri-Sun
    TASK_GAP = {
        PROFILE_VIEW: [24,36], #days
        PROFILE_ANALYSIS: [3, 6], #hours
        LEAD_OUTREACH: [3, 6] #hours
    }
    INTER_TASK_DELAY_MIN = 120
    INTER_TASK_DELAY_MAX = 900

    INTER_SCHEDULER_RUN_DELAY_MIN = 10800 # 3 hrs
    INTER_SCHEDULER_RUN_DELAY_MAX = 18000 # 5 hrs

    def __init__(self):
        try:
            self.db_client = DBClient()
            self.li_handler = LIHandler()
        except Exception as e:
            print(f"[red]Error: {e}[/red]")
            raise
        self.page = self.li_handler.get_page(headless=False)
        self.li_view_handler = LIViewHandler(self.db_client, self.page)
        self.li_post_handler = LIPostHandler(self.db_client, self.page)
        self.li_post_reaction_handler = LIReactionHandler(self.db_client, self.page)
        self.li_profile_handler = LIProfileHandler(self.db_client, self.page)
        self.li_msg_handler = LIMessageHandler(self.db_client, self.page)

    @staticmethod
    def schedule_on_specific_day(specific_days: list = []):

        now = datetime.now()
         # Randomly pick one of the target weekdays
        target_weekday = random.choice(specific_days)

        # Compute how many days to add to reach the next occurrence of the target weekday
        days_until_target = (target_weekday - now.weekday() + 7) % 7
        if days_until_target == 0:
            days_until_target = 7  # Always schedule in the future

        scheduled_day = now + timedelta(days=days_until_target)

        random_hour = random.randint(Scheduler.START_HOUR, Scheduler.END_HOUR - 1)
        random_minute = random.randint(0, 59)

        next_run = scheduled_day.replace(
            hour=random_hour, minute=random_minute, second=0, microsecond=0
        )
        return next_run
    
    @staticmethod
    def schedule_with_gap(minimum_hours_between_next_run: int):
        now = datetime.now()
        earliest_allowed_time = now + timedelta(hours=minimum_hours_between_next_run)
        candidate_time = max(now, earliest_allowed_time)

        # Pick a random time window in allowed hours (same day)
        random_hour = random.randint(Scheduler.START_HOUR, Scheduler.END_HOUR)
        random_minute = random.randint(0, 59)
        # Snap to the run time window 
        if candidate_time.hour < Scheduler.START_HOUR:
            candidate_time = candidate_time.replace(hour=random_hour, minute=random_minute)
        # If after 9 PM, move to 9 AM next day
        elif candidate_time.hour >= Scheduler.END_HOUR:
            candidate_time = (candidate_time + timedelta(days=1))
            candidate_time = candidate_time.replace(hour=random_hour, minute=random_minute)

        return candidate_time
        


    def schedule_next_run(
        self,
        task: Schedule
    ) -> datetime:
        
        task_name = task.task

        if task_name == Scheduler.POST_REACTION:
            next_run = Scheduler.schedule_on_specific_day(Scheduler.POST_ANALYSIS_DAYS)
        else:
            task_gap_min, task_gap_max = Scheduler.TASK_GAP.get(task_name, [3, 6])
            minimum_hours_between_next_run = random.randint(task_gap_min, task_gap_max)
            next_run = Scheduler.schedule_with_gap(minimum_hours_between_next_run)
        
        task.next_run = next_run
        task.add(self.db_client)


    def _initial_schedule(self):
        # do profile view now
        # schedule the post_reaction for nearest Fr/Sa/Su
        # schedule profile analysis for 30 mins from now
        # schedule lead outreach for 90 mins from now
        profile_view = Schedule(TASK=self.PROFILE_VIEW,
                                NEXT_RUN=datetime.now())
        post_reaction = Schedule(TASK=self.POST_REACTION,
                                NEXT_RUN=datetime.now())
        profile_analysis = Schedule(TASK=self.PROFILE_ANALYSIS,
                                NEXT_RUN=datetime.now() + timedelta(minutes=30))
        lead_outreach = Schedule(TASK=self.LEAD_OUTREACH,
                                NEXT_RUN=datetime.now() + timedelta(minutes=90))
        for task in [profile_view, post_reaction, profile_analysis, lead_outreach]:
            task.add(self.db_client)
        return

    def _run_profile_view(self, task):
        self.li_view_handler.gather_profile_views()
        return
    
    def _run_post_reaction(self, task):
        self.li_post_handler.get_post_urls()
        self.li_post_reaction_handler.gather_reactions()
        return

    def _run_profile_analysis(self, task):
        self.li_profile_handler.get_profiles()
        return

    def _run_lead_outreach(self, task):
        self.li_msg_handler.process_leads()
        return
        

    def _run_task(self, task):
        match task.task:
            case self.PROFILE_VIEW: self._run_profile_view(task)
            case self.POST_REACTION: self._run_post_reaction(task)
            case self.PROFILE_ANALYSIS: self._run_profile_analysis(task)
            case self.LEAD_OUTREACH: self._run_lead_outreach(task)

    def _sleep_with_stop(self, total_seconds: int, stop_event: Event):
        """
        Sleep in small intervals, checking stop_event to exit early.
        """
        interval = 1  # second
        slept = 0
        while slept < total_seconds:
            if stop_event.is_set():
                print("[yellow]Scheduler stopping early during sleep[/yellow]")
                break
            time.sleep(interval)
            slept += interval

    def run(self, stop_event: Event = None):
        stop_event = stop_event or Event()

        while True:
            try:
                if stop_event.is_set():
                    print("[yellow]Scheduler received stop signal, exiting run loop[/yellow]")
                    break

                is_empty = Schedule.is_table_empty(self.db_client)
                if is_empty:
                    self._initial_schedule()
                    self._sleep_with_stop(60, stop_event)
                    continue

                scheduled_tasks = Schedule.get_due_tasks(self.db_client)
                for i, task in enumerate(scheduled_tasks):
                    if stop_event.is_set():
                        print("[yellow]Scheduler received stop signal during task execution, exiting[/yellow]")
                        return

                    task_name = task.task
                    if task_name not in Scheduler.TASKS:
                        print(f"Unknown task: {task}")
                        continue

                    task.last_run = datetime.now()
                    self.schedule_next_run(task)
                    self._run_task(task)

                    # Sleep between tasks if not last task
                    if i < len(scheduled_tasks) - 1:
                        sleep_time = random.randint(self.INTER_TASK_DELAY_MIN,
                                                    self.INTER_TASK_DELAY_MAX)
                        print(f"[gray] Sleeping for {sleep_time} seconds [/gray]")
                        self._sleep_with_stop(sleep_time, stop_event)

                earliest_next_task = Schedule.get_next_scheduled_time(self.db_client)
                print(f"[white] Next scheduled task is at {earliest_next_task} [/white]")
                if earliest_next_task:
                    now = datetime.now()
                    sleep_time = int(max((earliest_next_task - now).total_seconds(), 0) + 120)
                    print(f"[gray] Scheduler sleeping for {sleep_time} seconds [/gray]")
                    self._sleep_with_stop(sleep_time, stop_event)
            except Exception as e:
                print(f"[red]Error in scheduler run: {e}[/red]")
                break
