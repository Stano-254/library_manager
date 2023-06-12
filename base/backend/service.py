from base.backend.servicebase import ServiceBase
from base.models import State, TransactionType, Transaction


class StateService(ServiceBase):
    """ Service class for state"""
    manager = State.objects

class TransactionTypeService(ServiceBase):
    """ Service for Transaction type"""
    manager = TransactionType.objects

class TransactionService(ServiceBase):
    """ Service for transaction """
    manager = Transaction.objects