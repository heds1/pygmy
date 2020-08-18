

from django.shortcuts import render
from .forms import MessageRetrievalForm
from .models import MessageHelpers

def home(request):

    if request.method == 'POST':

        form = MessageRetrievalForm(request.POST)
        if form.is_valid():
            service = MessageHelpers.instantiate_service()
            num_messages = form.cleaned_data['num_messages']
            message_ids = MessageHelpers.get_message_ids(
                service=service, user_id='me', n=num_messages)

            context = {
                'message_ids': message_ids
            }

            return render(request, 'home.html', context)
        else:
            pass

    elif request.method == 'GET':
        form = MessageRetrievalForm()

    context = {
        'form': form
    }

    return render(request, 'home.html', context)



    
    # def get_message_ids(self, service, user_id='me', n=10):
    #     """
    #     return email message ids

    #     ARGS
    #         service: 
    #             authorized Gmail API service instance
    #         user_id: 
    #             user's email address. the special value
    #             "me" can be used to indicate the authenticated user.
    #         n: 
    #             number of message ids to retrieve (from most recent).

    #     RETURNS:
    #         a list of message ids
    #     """
    #     try:
    #         message_list = service.users().messages().list(userId=user_id, maxResults=n).execute()
    #         message_ids = [i['id'] for i in message_list['messages']]
    #         return(message_ids)
    #     except:
    #         print('An error occurred retrieving the message IDs.')