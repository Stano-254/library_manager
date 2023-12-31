import logging

from django.db.models import F

from base.backend.service import StateService
from base.backend.transactionlogbase import TransactionLogBase
from base.backend.utils.utilities import validate_name, validate_uuid4
from members.backend.service import MemberService
from django.forms.models import model_to_dict

lgr = logging.getLogger(__name__)


class MembersAdministration(TransactionLogBase):
    """
    handle the administration functionality relating to members including CRUD
    """

    def create_member(self, request, **kwargs):
        """
          Handles adding of members in the library system
          :param request: the original request
          :param kwargs: keyword arguments for creation of member.
          :return: dict response with code
          """
        transaction = None
        try:
            transaction = self.log_transaction('CreateMember', request=request, user=request.user)
            if not transaction:
                return {'code': '900.500.500', 'message': 'Create member transaction failed'}
            first_name = kwargs.get('first_name')
            last_name = kwargs.get('last_name')
            if not validate_name(first_name):
                self.mark_transaction_failed(transaction, message="Invalid first name")
                return {'code': '500.400.003', 'message': 'Invalid first name'}
            if not validate_name(last_name):
                self.mark_transaction_failed(transaction, message="Invalid last name")
                return {'code': '500.400.003', 'message': 'Invalid last name'}
            member = MemberService().create(**kwargs)
            if not member:
                self.mark_transaction_failed(
                    transaction, message='Failed to create member', response_code='200.001.003')
                return {'code': '200.001.003', 'message': 'Failed to create member'}
            self.complete_transaction(transaction, message='Success')
            return {'code': '100.000.000', 'message': 'success', 'data': model_to_dict(member)}
        except Exception as e:
            lgr.exception(f"Exception occurred during create of member :{e}")
            self.mark_transaction_failed(transaction, response=str(e))
            return {'code': '999.999.999', 'message': 'Error occurred during creation of member'}

    def get_member(self, request, member_id):
        """
        handle fetching of one member
        :param request: original request as received
        :param member_id: the unique identifier of the member
        :return: HttpResponse with member data
        """
        try:
            if not validate_uuid4(member_id):
                return {'code': '500.004.004', 'message': 'Invalid identifier'}
            member = MemberService().filter(id=member_id).annotate(state_name=F('state__name')).values().first()
            if not member:
                return {'code': '200.002.002', 'message': 'Member record not found'}
            return {'code': '100.000.000', 'data': member}
        except Exception as e:
            lgr.exception(f"Error retrieving member: {e}")
            return {'code': '999.999.999', 'message': 'Error occurred during fetch member'}

    def get_members(self, request, **kwargs):
        """
        Handles fetching of multiple user, either with added conditions
        (like active members or inactive members etc.) or without conditions
        :param request: original request received
        :param kwargs: The parameters used to filter based on conditions if any.
        :return: dict response of a list of all user based on conditions provided
        """
        try:
            members = MemberService().filter().annotate(
                state_name=F('state__name')).values(
                'id', 'first_name', 'last_name', 'national_id', 'mobile_no', 'gender', 'membership_no', 'state_name')
            if not members:
                return {'code': '200.001.002', 'message': 'Members not found'}
            return {'code': '100.000.000', 'data': list(members)}
        except Exception as e:
            lgr.exception(f"Error occurred during fetch of members : {e}")
            return {'code': '999.999.999', 'message': 'Error occurred during retrieval of members'}

    def update_member(self, request, member_id, **kwargs):
        """
        Handles updating of members personal information or
        any other information related to members
        :param member_id: unique identifier of the member
        :param request: Original Django HTTP request
        :type request: WSGIRequest
        :param kwargs: dict of other parameters
        :return: dict response
        """
        transaction = None
        try:
            transaction = self.log_transaction('UpdateMember', request=request, user=request.user)
            if not transaction:
                return {'code': '900.500.500', 'message': 'Update member transaction failed'}
            if not validate_uuid4(member_id):
                self.mark_transaction_failed(
                    transaction, message='Invalid member identifier', response_code='500.400.004')
                return {'code': '500.400.004', 'message': 'Invalid member identifier'}
            member = MemberService().get(id=member_id)
            if not member:
                self.mark_transaction_failed(transaction, message='Member not found', response_code='200.001.002')
                return {'code': '200.001.002', 'message': 'Member not found'}
            updated_member = MemberService().update(member.id, **kwargs)
            if not updated_member:
                self.mark_transaction_failed(
                    transaction, message='Member details not update', response_code='200.001.003')
                return {'code': '200.001.003', 'message': 'Member details not updated'}
            self.complete_transaction(transaction, message='Success')
            return {'code': '100.000.000', 'message': 'success'}
        except Exception as e:
            lgr.exception(f"Error occurred during updating member details")
            self.mark_transaction_failed(transaction, response=str(e))
            return {'code': '999.999.999', 'message': 'Error updating member details'}

    def change_member_status(self, request, member_id, **kwargs):
        """
        Handles deletion of user from the system hypothetically
        though the user is never deleted just updated to state deleted
        :param request: Original Django HTTP request
        :param member_id: the unique member identifier
        :return: dict response with code
        """
        action = kwargs.get('action', 'delete').title()
        transaction = None
        try:
            transaction = self.log_transaction(f'{action}Member', request=request, user=request.user)
            if not transaction:
                return {'code': '900.500.500', 'message': 'Delete member transaction failed'}
            if not validate_uuid4(member_id):
                self.mark_transaction_failed(
                    transaction, message='Invalid member identifier', response_code='500.400.004')
                return {'code': '500.400.004', 'message': 'Invalid member identifier'}
            member = MemberService().get(id=member_id)
            if not member:
                self.mark_transaction_failed(transaction, message='Member not found', response_code='200.001.002')
                return {'code': '200.001.002', 'message': 'Member not found'}
            # check for action to be performed
            state = ""
            if action == "Delete":
                # check current member state
                if member.state.name == 'Deleted':
                    self.mark_transaction_failed(transaction, message='Member already deleted',
                                                 response_code='100.000.001')
                    return {'code': '100.000.001', 'message': 'Cannot deleted member, record was already deleted'}
                state = StateService().get(name='Deleted')
            elif action == 'Enable':
                if member.state.name == 'Active':
                    self.mark_transaction_failed(
                        transaction, message='Member already activated', response_code='100.000.002')
                    return {'code': '100.000.002', 'message': 'Member already activated'}
                state = StateService().get(name='Active')
            elif action == 'Disable':
                if member.state.name in tuple(['Disabled', 'Deleted']):
                    self.mark_transaction_failed(
                        transaction, message='Member already Disabled', response_code='100.000.003')
                    return {'code': '100.000.003', 'message': 'Member already Disabled'}
                state = StateService().get(name='Disabled')
            else:
                self.mark_transaction_failed(
                    transaction, message='Wrong action', response_code='100.000.003')
                return {'code': '300.300.003', 'message': 'No action to be performed'}
            update_member = MemberService().update(member.id, state=state)
            if not update_member:
                self.mark_transaction_failed(
                    transaction, message=f'Failed to {action} Member', response_code='200.001.007')
                return {'code': '200.001.007', 'message': f'Failed to {action} Member'}
            self.complete_transaction(transaction, message=f'{action } member Successfully')
            return {'code': '100.000.000', 'message': f'{action } member Successfully'}
        except Exception as e:
            lgr.exception(f"Error deleting member details : {e}")
            self.mark_transaction_failed(transaction, message='Error deleting member details', response=str(e))
            return {'code': '999.999.999', 'message': 'Error deleting member details'}
