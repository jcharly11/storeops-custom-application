class EventBus:
    subscribers = {}

    @classmethod
    def subscribe(cls, type, subscriber):
        if type not in cls.subscribers:
            cls.subscribers[type] = []
        cls.subscribers[type].append(subscriber)

    @classmethod
    def publish(cls, type, data=None):
        if type in cls.subscribers:
            for subscriber in cls.subscribers[type]:
                subscriber.handleMessage(type, data)
