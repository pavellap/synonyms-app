from app import app, create_table

# запускаем проект
if __name__ == "__main__":
    create_table()
    app.run(debug=True, port=5000)
