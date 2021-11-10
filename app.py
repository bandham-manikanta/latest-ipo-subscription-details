from app_main import create_app

app = create_app('config.py')

if __name__ == '__main__':
    app.run(threaded=True)