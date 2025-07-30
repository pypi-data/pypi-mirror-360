cache = {
    "time_period": None,
    "last_updated": None
}

def get_time_period():
    return cache.get('time_period')

def set_time_period(time_period):
    cache['time_period'] = time_period
    cache['last_updated'] = time_period
