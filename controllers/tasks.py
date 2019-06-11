
def index():
    redirect(URL(request.controller, 'list'))

@auth.requires_login()
def list():
    num_tasks = len()
    notifications = all_notifications


    response.view_title = '%s %s %s' % (
        request.controller.replace('_', ' ').title(),
        ' |',
        request.function.replace('_', ' ').title(),
    )

    message_types = []
    for note in notifications:
        message_types.append(note['message_type'])

    return locals()

def menu():
    # notification check functions

    return dict(
        num_notifications = len(all_notifications),
        notifications = all_notifications
        )
