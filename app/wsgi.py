from app.__init__ import getApp
app = getApp()
if __name__ == "__main__":
    # app.run(threaded=True)
    app.run("0.0.0.0", port=5001)