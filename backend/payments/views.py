from django.core.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Payment
from .serializers import PaymentSerializer


class PaymentCreateView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except ValidationError as exc:
            if hasattr(exc, "message_dict"):
                detail = exc.message_dict
            else:
                detail = {"detail": exc.messages}
            return Response(detail, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


from django.views.generic import DetailView
from .models import Contract

class ContractDetailView(DetailView):
    model = Contract
    template_name = "contracts/contract_detail.html"
    context_object_name = "contract"
