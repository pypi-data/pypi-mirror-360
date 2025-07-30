def register(plugin):
    def wrapper(cls):
        plugin.append(cls);
        return cls;
    return wrapper;