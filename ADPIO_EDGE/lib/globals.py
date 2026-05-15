import os


ROOT_FOLDER  = os.getcwd()

WORKSPACE    = f'{os.path.expanduser("~")}/.ADPIOEDGE'
ASSET_FOLDER = f'{WORKSPACE}/assets'
APPS_FOLDER  = f'{WORKSPACE}/applications'


def WEB_INF_index():
    INDEX = """
    <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <meta name='viewport' content='width=device-width,initial-scale=1'>

            <title>ADPIO EDGE</title>

            <link rel="apple-touch-icon" sizes="180x180"    href="/favicon/apple-touch-icon.png">
            <link rel="icon" type="image/png" sizes="32x32" href="/favicon/favicon-32x32.png">
            <link rel="icon" type="image/png" sizes="16x16" href="/favicon/favicon-16x16.png">
            <link rel="manifest"                            href="/favicon/site.webmanifest">
            <script type="module" crossorigin src="/assets/index.js"></script>
            <link rel="stylesheet" crossorigin href="/assets/index.css">
        </head>
        <body>
            <div id="app"></div>
        </body>
    </html>
    """

    return INDEX
    

