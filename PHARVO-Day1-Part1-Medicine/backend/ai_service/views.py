from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .predictor import predict_health_problem


@api_view(["POST"])
def ai_query(request):
    text = request.data.get("text", "")

    if not text or not str(text).strip():
        return Response(
            {"error": "text is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        result = predict_health_problem(text)
        return Response(result)

    except Exception as exc:
        return Response(
            {"error": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )