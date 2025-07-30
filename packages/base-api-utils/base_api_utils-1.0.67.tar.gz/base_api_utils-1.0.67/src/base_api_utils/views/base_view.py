from rest_framework.viewsets import ModelViewSet

class BaseView(ModelViewSet):
    ordering_fields = {}

    def get_queryset(self):
        return self.queryset

    def apply_ordering(self, queryset):
        ordering = self.request.query_params.get('ordering')
        if ordering:
            ordering_fields = []
            for field in ordering.split(","):
                if field.startswith("-"):
                    field_name = field[1:]
                    if field_name in self.ordering_fields:
                        ordering_fields.append(f"-{field_name}")
                else:
                    if field in self.ordering_fields:
                        ordering_fields.append(field)

            if ordering_fields:
                queryset = queryset.order_by(*ordering_fields)

        return queryset
