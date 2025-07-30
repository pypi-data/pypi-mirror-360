from django.apps import AppConfig

from ..utils import is_runserver, camel_to_kebab


class DjangoHeadlessRestConfig(AppConfig):
    name = "headless.rest"
    label = "headless_rest"

    def ready(self):
        from django.urls import path
        from rest_framework import serializers
        from rest_framework.viewsets import ModelViewSet
        from ..registry import headless_registry
        from ..utils import log
        from .routers import rest_router
        from .viewsets import SingletonViewSet

        if is_runserver():
            log(":building_construction:", "Setting up REST routes")
            models = headless_registry.get_models()

            for model_config in models:
                model_class = model_config["model"]
                singleton = model_config["singleton"]
                base_path = camel_to_kebab(model_class.__name__)

                class Serializer(serializers.ModelSerializer):
                    class Meta:
                        model = model_class
                        fields = "__all__"

                if singleton:

                    class ViewSet(SingletonViewSet):
                        queryset = model_class.objects.none()
                        serializer_class = Serializer

                        def get_queryset(self):
                            return model_class.objects.all()[:1]

                    log("   ---", f"{model_class._meta.verbose_name}")
                    log("     |---", f"GET /{base_path}")
                    log("     |---", f"PUT /{base_path}")
                    log("     |---", f"PATCH /{base_path}")
                    log("\n")
                    rest_router.urls.append(
                        path(
                            base_path,
                            ViewSet.as_view(
                                {
                                    "get": "retrieve",
                                    "put": "update",
                                    "patch": "partial_update",
                                }
                            ),
                        )
                    )

                else:

                    class ViewSet(ModelViewSet):
                        queryset = model_class.objects.all()
                        serializer_class = Serializer

                    log("   ---", f"{model_class._meta.verbose_name}")
                    log("     |--", f"GET /{base_path}")
                    log("     |--", f"GET /{base_path}/{{id}}")
                    log("     |--", f"PUT /{base_path}/{{id}}")
                    log("     |--", f"PATCH /{base_path}/{{id}}")
                    log("     |--", f"POST /{base_path}")
                    log("     |--", f"DELETE /{base_path}/{{id}}")
                    log("\n")

                    rest_router.register(base_path, ViewSet)
