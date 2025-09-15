def format_task(task):
    """Hide username/token from Flower."""
    kwargs = eval(task.kwargs)
    if 'username' in kwargs:
        kwargs['username'] = '*' * len(kwargs['username'])
    if 'token' in kwargs:
        kwargs['token'] = '*' * len(kwargs['token'])
    task.kwargs = str(kwargs)
    return task