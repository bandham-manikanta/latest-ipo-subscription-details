from app_main import create_app
from flask_apscheduler import APScheduler

class Config:
    """App configuration."""

    SCHEDULER_API_ENABLED = True

scheduler = APScheduler()

# interval examples
@scheduler.task("interval", id="do_job_1", seconds=5, misfire_grace_time=10)
def job1():
    print("Job 1 executed")

app = create_app('config.py')

if __name__ == '__main__':
    scheduler.init_app(app)
    scheduler.start()
    app.run(threaded=True)