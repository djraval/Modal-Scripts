# modal.Cron

    
    
    class Cron(modal.schedule.Schedule)

Copy

Cron jobs are a type of schedule, specified using the Unix cron tab syntax.

The alternative schedule type is the `modal.Period`.

**Usage**

    
    
    import modal
    app = modal.App()
    
    
    @app.function(schedule=modal.Cron("* * * * *"))
    def f():
        print("This function will run every minute")

Copy

We can specify different schedules with cron strings, for example:

    
    
    modal.Cron("5 4 * * *")  # run at 4:05am every night
    modal.Cron("0 9 * * 4")  # runs every Thursday 9am

Copy

    
    
    def __init__(self, cron_string: str) -> None:

Copy

Construct a schedule that runs according to a cron expression string.

