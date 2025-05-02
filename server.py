from flask_app import app

if __name__ == "__main__":
    print("Available Routes:", app.url_map)  # Debugging routes
    app.run(debug=True, port=4346)
