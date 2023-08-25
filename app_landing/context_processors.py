from app_landing.forms import OrderCreateForm


def add_order_create_form(request):
    return {
        'order_create_form': OrderCreateForm()
    }