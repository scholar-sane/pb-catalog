from flask import Flask, render_template, request, redirect, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///item.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Specify the upload folder
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# For establish a many-to-many relationship between the product and color tables
product_color = db.Table('product_color',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('color_id', db.Integer, db.ForeignKey('color.id'), primary_key=True)
)

# For create a many-to-many relationship between the product and size tables
product_size_association = db.Table('product_size_association',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('size_id', db.Integer, db.ForeignKey('size.id'), primary_key=True)
)

# Model for a product table
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(50), nullable=False)
    brand_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    cover = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    colors = db.relationship('Color', secondary=product_color, backref='products')
    sizes = db.relationship('Size', secondary=product_size_association, backref='products')

    # Defining a string representation of the Product object
    def __str__(self):
        return f"Product ID: {self.id}, Name: {self.product_name}, Brand: {self.brand_name}, Price: {self.price}, Colors: {self.colors}, Sizes: {self.sizes}"

    # Defining a canonical string representation of the Product object
    def __repr__(self):
        return f"Product ID: {self.id}, Name: {self.product_name}, Brand: {self.brand_name}, Price: {self.price}, Colors: {self.colors}, Sizes: {self.sizes}"


# Defines a SQLAlchemy model for colors in a database,
class Color(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

# Defines a SQLAlchemy model for sizes in a database
class Size(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)


with app.app_context():
    db.create_all()


# Route handler '/' renders the 'index.html' template 
@app.route('/')
def hello():
    products = Product.query.all()
    return render_template('index.html', products=products)

# '/create' route handles both GET and POST requests
@app.route('/create', methods=['GET','POST'])
def createProduct():
    if request.method == 'POST':
        product_name = request.form['product_name']
        brand_name = request.form['brand_name']
        price = request.form['price']
        cover = request.files['cover']

        # Retrieve color names from the form
        color_names = request.form.getlist('colors')
        print(color_names)
        colors = []

        # Retrieve color objects by name or create new ones if they don't exist
        for color_name in color_names:
            color = Color.query.filter_by(name=color_name).first()
            if not color:
                color = Color(name=color_name)
                db.session.add(color)
            colors.append(color)

        # Retrieve size names from the form
        size_names = request.form.getlist('sizes')
        sizes = []

        # Retrieve size objects by name or create new ones if they don't exist
        for size_name in size_names:
            size = Size.query.filter_by(name=size_name).first()
            if not size:
                size = Size(name=size_name)
                db.session.add(size)
            sizes.append(size)

        if cover:
            filename = secure_filename(cover.filename)
            cover.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cover_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        else:
            cover_path = None
        
        product = Product(
            product_name=product_name,
            brand_name=brand_name,
            price=price,
            cover=cover_path
        )

        # Add colors and sizes to the product
        product.colors.extend(colors)
        product.sizes.extend(sizes)

        db.session.add(product)
        db.session.commit()
        return redirect('/')
    else:
        colors = Color.query.all()
        sizes = Size.query.all()
        return render_template('create.html', colors=colors, sizes=sizes)


@app.route('/add_to_cart', methods=['GET', 'POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data['productId']
    colors = data['colors']
    sizes = data['sizes']
    
    message = f'Item added to cart successfully. Product ID: {product_id}, Colors: {colors}, Sizes: {sizes}'
    return jsonify({'message': message})

    # return render_template('index.html')
    

if __name__ == '__main__':
    app.run(debug=True)