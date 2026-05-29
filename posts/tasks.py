from posts.post_planner import post_planner

from celery import shared_task

@shared_task
def run_post_planner() -> str:
    count = post_planner()
    return f"Published {count} scheduled posts"
