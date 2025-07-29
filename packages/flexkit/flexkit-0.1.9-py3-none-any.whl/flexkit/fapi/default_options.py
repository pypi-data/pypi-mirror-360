from fastapi.middleware.cors import CORSMiddleware


def app_default_options():
    return {
        "title": "API SERVER",
        "version": "0.0.1",
        "description": "this is a api server",
    }


def default_cors():
    return {
        "middleware_class": CORSMiddleware,
        "allow_origins": ["*"],
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
