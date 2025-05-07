from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from task_5.main import browse_documents

url_doc = {}
with open("task_1/index.txt", "r", encoding="utf-8") as f:
    index = f.read().splitlines()
    for line in index:
        print(line)
        doc_id, url = line.split(" ")[0], line.split(" ")[1]
        url_doc[doc_id] = url


class BrowseDocumentsViewSet(ViewSet):
    @extend_schema(
        tags=["Browse Documents"],
        summary="Получить список документов по запросу",
        parameters=[
            OpenApiParameter(
                "query",
                type=OpenApiTypes.STR,
                description="Запрос по которому будут получены результаты",
            ),
            OpenApiParameter(
                "top_n",
                type=OpenApiTypes.INT,
                description="Количество результатов которое будет возвращено",
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="browse-documents")
    def browse_documents(self, request, pk=None):
        query = request.query_params.get("query")
        top_n = request.query_params.get("top_n")
        if not query:
            return Response(
                {"error": "Поле 'query' не заполнено"}, status=status.HTTP_400_BAD_REQUEST
            )
        if not top_n:
            return Response(
                {"error": "Поле 'top_n' не заполнено"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            top_n = int(top_n)
        except ValueError:
            return Response(
                {"error": "Поле 'top_n' должно быть числом"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        results = browse_documents(query, top_n)
        for result in results:
            result["url"] = url_doc[str(result["doc_num"])]

        return Response(results)
