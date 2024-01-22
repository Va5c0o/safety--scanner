from website import create_app
# from flask_wtf.csrf import CSRFProtect

# csrf = CSRFProtect()
# csrf.init_app(app)

app = create_app()

if __name__ == '__main__':
  app.run(debug=False)