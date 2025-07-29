"""
@Author: obstacle
@Time: 20/01/25 15:16
@Description:  
"""
import asyncio
import json
import traceback
import requests

from urllib.parse import quote
from datetime import datetime
from puti.logs import logger_factory
from celery import shared_task
from tenacity import retry, stop_after_attempt, wait_fixed, RetryCallState

from puti.conf.client_config import TwitterConfig
from puti.llm.roles.agents import CZ
from puti.llm.roles.x_bot import TwitWhiz
from puti.db.sqlite_operator import SQLiteOperator
from puti.db.model.task.bot_task import TweetSchedule
from puti.llm.actions.x_bot import GenerateTweetAction, PublishTweetAction
from puti.llm.roles.agents import Ethan
from puti.llm.workflow import Workflow
from puti.llm.graph import Graph, Vertex
from croniter import croniter

lgr = logger_factory.default
cz = CZ()
x_conf = TwitterConfig()
twit_whiz = TwitWhiz()
ethan = Ethan()


# @celery_app.task(task_always_eager=True)
def add(x, y):
    lgr.info('[Task] add starting execution')
    try:
        result = x + y
        lgr.info(f'[Task] add executed successfully, result: {result}')
        return result
    except Exception as e:
        lgr.error(f'[Task] add execution failed: {e}')
        raise
    finally:
        lgr.info('[Task] add execution finished')


# @celery_app.task(task_always_eager=False)
@shared_task()
def periodic_post_tweet():
    start_time = datetime.now()
    try:
        loop = asyncio.get_event_loop()
        tweet = loop.run_until_complete(cz.run('give me a tweet'))
        tweet = json.loads(tweet)['final_answer']
        lgr.debug(f'[Scheduled Task] Preparing to send tweet content: {tweet}')

        @retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
        def safe_post_tweet():
            url = f"https://api.game.com/ai/xx-bot/twikit/post_tweet?text={quote(tweet)}"
            response = requests.post(url, timeout=10)
            response.raise_for_status()
            return response.text

        result = safe_post_tweet()
        lgr.debug('[Scheduled Task] Time taken: {:.2f}s'.format((datetime.now() - start_time).total_seconds()))
        lgr.debug(f"[Scheduled Task] Scheduled task executed successfully: {result}")
    except Exception as e:
        lgr.debug(f'[Scheduled Task] Task execution failed: {e.__class__.__name__} {str(e)}. {traceback.format_exc()}')
    finally:
        lgr.debug(f'============== [Scheduled Task] periodic_post_tweet execution finished ==============')
    return 'ok'


@shared_task()
def periodic_get_mentions():
    start_time = datetime.now()
    try:
        url = f"https://api.game.com/ai/xx-bot/twikit/get_mentions?query_name={x_conf.USER_NAME}"
        lgr.debug(f'[Scheduled Task] Requesting interface: {url}')

        @retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
        def safe_get_mentions():
            response = requests.post(url, timeout=10)
            response.raise_for_status()
            return response.text

        result = safe_get_mentions()
        lgr.debug('[Scheduled Task] Time taken: {:.2f}s'.format((datetime.now() - start_time).total_seconds()))
        lgr.debug(f"[Scheduled Task] get_mentions executed successfully: {result}")
    except Exception as e:
        lgr.debug(f'[Scheduled Task] get_mentions task execution failed: {e.__class__.__name__} {str(e)}. {traceback.format_exc()}')
    finally:
        lgr.debug(f'============== [Scheduled Task] periodic_get_mentions execution finished ==============')
    return 'ok'


@shared_task()
def periodic_reply_to_tweet():
    start_time = datetime.now()
    try:
        db = SQLiteOperator()
        sql = "SELECT text, author_id, mention_id FROM twitter_mentions WHERE replied=0 AND is_del=0"
        rows = db.fetchall(sql)
        lgr.debug(f'[Scheduled Task] Number of mentions to reply to: {len(rows)}')
        for row in rows:
            text, author_id, mention_id = row
            try:
                loop = asyncio.get_event_loop()
                reply = loop.run_until_complete(twit_whiz.run(text))
                reply_text = json.loads(reply).get('final_answer', '')
                if not reply_text:
                    lgr.debug(f'[Scheduled Task] LLM did not generate a reply for: {text}')
                    continue
                url = f"https://api.game.com/ai/xx-bot/twikit/reply_to_tweet?text={quote(reply_text)}&tweet_id={mention_id}&author_id={author_id}"
                lgr.debug(f'[Scheduled Task] Requesting interface: {url}')

                @retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
                def safe_reply_to_tweet():
                    response = requests.post(url, timeout=10)
                    response.raise_for_status()
                    return response.text

                result = safe_reply_to_tweet()
                lgr.debug(f"[Scheduled Task] reply_to_tweet executed successfully: {result}")

            except Exception as e:
                lgr.debug(f'[Scheduled Task] Single reply failed: {e.__class__.__name__} {str(e)}. {traceback.format_exc()}')
    except Exception as e:
        lgr.debug(f'[Scheduled Task] reply_to_tweet task execution failed: {e.__class__.__name__} {str(e)}. {traceback.format_exc()}')
    finally:
        lgr.debug(f'============== [Scheduled Task] periodic_reply_to_tweet execution finished ==============')
    return 'ok'


@shared_task()
def check_dynamic_schedules():
    """
    Checks for dynamic schedules in the database and triggers tasks as needed.
    This task is the heartbeat of the dynamic scheduler system and should be
    scheduled to run frequently (e.g., every minute).
    """
    now = datetime.now()
    lgr.debug(f'Checking dynamic schedules at {now}')

    try:
        # Use the schedule manager for better database interaction
        from puti.db.schedule_manager import ScheduleManager
        manager = ScheduleManager()
        
        # 1. Automatically reset stuck tasks
        reset_count = manager.reset_stuck_tasks(max_minutes=10)
        if reset_count > 0:
            lgr.info(f'Reset {reset_count} stuck tasks')
        
        # 2. Get all active scheduled tasks
        schedules = manager.get_all(where_clause="enabled = 1 AND is_del = 0")
        lgr.debug(f'Found {len(schedules)} active schedules to evaluate')
        
        # 3. Check and trigger due tasks
        for schedule in schedules:
            # Skip schedules that are already running
            if schedule.is_running:
                lgr.debug(f'Schedule "{schedule.name}" is already running, skipping.')
                continue
                
            # A robust way to check if a task should have run.
            # We iterate from the last known run time up to the current time.
            # This ensures we don't miss runs if the service was down.
            last_run = schedule.last_run or datetime.fromtimestamp(0)
            try:
                cron = croniter(schedule.cron_schedule, last_run)
                
                # Get the next scheduled run time based on the last execution
                next_run_time = cron.get_next(datetime)

                if next_run_time <= now:
                    lgr.info(f'[Scheduler] Triggering task for schedule "{schedule.name}" (ID: {schedule.id})')

                    # Extract parameters from the schedule
                    params = schedule.params or {}
                    topic = params.get('topic')

                    # Mark the task as running in the database
                    manager.update(schedule.id, {"is_running": True})
                    
                    # Asynchronously trigger the target task via Celery worker
                    task = generate_tweet_task.delay(topic=topic)
                    
                    # Update the schedule's timestamps and task info in the database
                    new_next_run = croniter(schedule.cron_schedule, now).get_next(datetime)
                    schedule_updates = {
                        "last_run": now,
                        "next_run": new_next_run,
                        "task_id": task.id
                    }
                    manager.update(schedule.id, schedule_updates)
                    
                    lgr.info(f'[Scheduler] Schedule "{schedule.name}" executed. Next run at {new_next_run}.')
            except Exception as e:
                lgr.error(f'Error processing schedule {schedule.id} ({schedule.name}): {str(e)}')
                # Attempt to set the next run time
                try:
                    from croniter import croniter
                    new_next_run = croniter(schedule.cron_schedule, now).get_next(datetime)
                    manager.update(schedule.id, {"next_run": new_next_run, "is_running": False})
                    lgr.info(f'Reset next_run for schedule "{schedule.name}" to {new_next_run} after error')
                except Exception as inner_e:
                    lgr.error(f'Could not reset next_run for schedule {schedule.id}: {str(inner_e)}')

    except Exception as e:
        lgr.error(f'[Scheduler] Error checking dynamic schedules: {str(e)}. {traceback.format_exc()}')

    return 'ok'


@shared_task(bind=True)
def generate_tweet_task(self, topic: str = None):
    """
    Task that uses the test_generate_tweet_graph function to generate and post tweets.
    Accepts an optional topic to guide tweet generation.
    """
    start_time = datetime.now()
    task_id = self.request.id
    
    try:
        # Find the schedule associated with this task
        from puti.db.schedule_manager import ScheduleManager
        manager = ScheduleManager()
        
        # Try to update running status 
        try:
            import os
            pid = os.getpid()
            
            # Try to find the schedule by task_id if we have one
            schedules = manager.get_all(where_clause="task_id = ?", params=(task_id,))
            if schedules:
                schedule = schedules[0]
                manager.update(schedule.id, {"pid": pid})
                lgr.info(f'[Task {task_id}] Updated schedule {schedule.name} with PID {pid}')
        except Exception as e:
            lgr.warning(f'Could not update PID for task {task_id}: {str(e)}')
        
        lgr.info(f'[Task {task_id}] generate_tweet_task started, topic: {topic}')
        
        generate_tweet_action = GenerateTweetAction()
        post_tweet_action = PublishTweetAction()

        # Pass the topic to the action
        generate_tweet_vertex = Vertex(id='generate_tweet', action=generate_tweet_action, topic=topic)
        post_tweet_vertex = Vertex(id='post_tweet', action=post_tweet_action, role=ethan)

        graph = Graph()
        graph.add_vertices(generate_tweet_vertex, post_tweet_vertex)
        graph.add_edge(generate_tweet_vertex.id, post_tweet_vertex.id)
        graph.set_start_vertex(generate_tweet_vertex.id)

        workflow = Workflow(graph=graph)
        resp = asyncio.run(workflow.run_until_vertex(post_tweet_vertex.id))
        
        # Task completed successfully
        try:
            schedules = manager.get_all(where_clause="task_id = ?", params=(task_id,))
            if schedules:
                schedule = schedules[0]
                manager.update(schedule.id, {"is_running": False, "pid": None})
                lgr.info(f'[Task {task_id}] Completed schedule {schedule.name} successfully')
        except Exception as e:
            lgr.warning(f'Could not update status for task {task_id}: {str(e)}')
        
        execution_time = (datetime.now() - start_time).total_seconds()
        lgr.info(f'[Task {task_id}] Completed in {execution_time:.2f} seconds')
        return resp
        
    except Exception as e:
        # Task failed
        try:
            from puti.db.schedule_manager import ScheduleManager
            manager = ScheduleManager()
            schedules = manager.get_all(where_clause="task_id = ?", params=(task_id,))
            if schedules:
                schedule = schedules[0]
                manager.update(schedule.id, {"is_running": False, "pid": None})
                lgr.error(f'[Task {task_id}] Failed schedule {schedule.name}: {str(e)}')
        except Exception as inner_e:
            lgr.warning(f'Could not update status for task {task_id}: {str(inner_e)}')
            
        lgr.error(f'[Task {task_id}] Failed: {str(e)}. {traceback.format_exc()}')
    finally:
        lgr.info(f'[Task {task_id}] Execution finished')
    return 'ok'
