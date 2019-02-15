from service_images import create_app
# import logging
# log = logging.getLogger(__name__)

app = create_app()

if __name__ == "__main__":
    port = 5000
    # print(
    #     f'>>>>> Service_images is starting serving at http://{app.config["SERVER_NAME"]}/:{port}>>>>>'
    # )
    app.run(port=port, debug=__debug__)
