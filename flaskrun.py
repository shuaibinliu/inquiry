from inquiry import create_app
from inquiry.extensions.register_ext import celery

app = create_app()

if __name__ == '__main__':
    app.run(port=7444)
