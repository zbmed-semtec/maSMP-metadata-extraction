class CallbackOffer:

    """
    Offers callback functions to be executed when a certain event occurs.
    Callback functions can be registered and deregistered by the user.
    """

    def __init__(self):
        self.callbacks = {}

    def register(self, handle, callback):
        self.callbacks[handle] = callback
    
    def deregister(self, handle):
        if handle in self.callbacks:
            del self.callbacks[handle]

    def callback(self, *args, **kwargs):
        for func in self.callbacks.values():
            func(*args, **kwargs)
    