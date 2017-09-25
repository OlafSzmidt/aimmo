from abc import ABCMeta, abstractmethod


class _Pickup(object):
    '''
    Abstract class for all types (ie. subclasses) of pickups.
    '''
    __metaclass__ = ABCMeta

    def __init__(self, cell):
        self.cell = cell

    def __str__(self):
        return self.__class__.__name__

    def delete_pickup(self):
        self.cell.pickup = None

    def apply(self, avatar):
        '''
        Public method to apply the pickup to an avatar. This will vary from type of pickup
        therefore implementation is done privately.
        :param avatar: an Avatar object.
        '''
        self._apply(avatar)
        self.delete_pickup()

    @abstractmethod
    def _apply(self, avatar):
        raise NotImplementedError()

    @abstractmethod
    def serialise(self):
        raise NotImplementedError()


class DeliveryTote(_Pickup):
    '''
    Inherits generic functionality from _Pickup and needs to implement abstract methods.
    '''

    def __init__(self, cell):
        super(DeliveryTote, self).__init__(cell)

    def _apply(self, avatar):
        avatar.holdingTote = True

    def serialise(self):
        return {
            'type': 'delivery_tote',
        }

ALL_PICKUPS = (
    DeliveryTote
)