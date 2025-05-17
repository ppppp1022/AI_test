try:
    from plyer import notification
except:
    import os
    os.system("pip install plyer")
    from plyer import notification

notification.notify(
    title = "tmp title",
    message = "sample message",
    )
