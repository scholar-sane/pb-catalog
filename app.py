from flask import Flask, render_template, request, redirect
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Specify the upload folder
db = SQLAlchemy(app)
migrate = Migrate(app,db)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(50), nullable=False)
    brand_name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    cover = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def _repr_(self):
        return f"product_name='{self.product_name}'"

with app.app_context():
    db.create_all()

# Create the database tables
# db.create_all()


@app.route('/')
def hello():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/create', methods=['GET','POST'])
def createProduct():
    if request.method == 'POST':
        product_name = request.form['product_name']
        brand_name = request.form['brand_name']      
        color = request.form['color'] 
        size = request.form['size']     
        price = request.form['price']  
        cover = request.files['cover'] 

        if cover:
            filename = cover.filename
            cover.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cover_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        else:
            cover_path = None

        product = Product(product_name=product_name, brand_name=brand_name, color=color, size=size, price=price, cover=cover_path)
        db.session.add(product)
        db.session.commit()

        return "Done"
    else:
        return render_template('create.html')

if __name__ == '__main__':
    app.run(debug=True)