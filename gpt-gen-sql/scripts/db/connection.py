try:
    import pymysql
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--target=/tmp/pylib", "pymysql"])
    sys.path.insert(0, "/tmp/pylib")
    import pymysql

config = {
 "host": "103.2.113.229",
 "port": 3306,
 "user": "lotus_whmcs",
 "password": "w,jmik[8iy[",
 "database": "temp-whmcs",
 "cursorclass": pymysql.cursors.DictCursor
}

def get_connection():
    return pymysql.connect(**config)