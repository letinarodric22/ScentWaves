from flask import Flask, render_template, request, redirect, flash, jsonify,session,url_for
from database import *
from datetime import datetime,timedelta
import pygal
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "12345678"


@app.route("/")  # this sets the route to this page 
def home():
    return render_template("index.html")

@app.route("/signup", methods=["POST", "GET" ])
def signup():
    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        contact = request.form["contact"] 
        address = request.form["address"]
        password = request.form["password"]
        password= generate_password_hash(password)
        user = (full_name, email, contact, address, password, 'now()')
        adduser(user)
        flash("Account successfully created. Please proceed to login.", "success")
        return redirect("/signup")
    
    return render_template("register.html")


@app.route("/sign_in", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        users = fetch_data("users")
        for user in users:
            db_email = user[2]   
            db_pass = user[5]
            if db_email == email and check_password_hash (db_pass, password):
                return redirect("/")
            else:
                flash("Incorrect email or password. Please try again.", "error")
    return render_template("login.html")

@app.route("/customers")
def customer():
    user = fetch_data("users")
    return render_template("customers.html", renny= user)

@app.route("/editservice", methods=['POST', 'GET'])  # Lowercase 'methods'
def editservices():
     if request.method == "POST":
        s_id = request.form['s_id']
        servicetype = request.form["servicetype"]
        itemtype = request.form["itemtype"]
        service_price = request.form["service_price"]
        image = request.form["image"]
        s= (s_id, servicetype, itemtype, service_price,image)
        update_service(s)
     return redirect("/inventory")
 
 
@app.route("/addservice", methods=["POST","GET"])
def addservice():
     if request.method=="POST":
         servicetype=request.form["servicetype"]
         itemtype=request.form["itemtype"]
         service_price=request.form["service_price"]
         image=request.form["image"]
         s = (servicetype,itemtype,service_price,image)
         add_services(s)
     return redirect('/inventory')
     

@app.route("/services")
def service():
    return render_template("services.html")



@app.route('/deleteservice', methods=["POST"])
def deleteproduct():
    if request.method == "POST":
        s_id = request.form["s_id"]
        delete_services(s_id)
    return redirect("/inventory")

@app.route("/pricing")
def price():
    service = fetch_data("services")
    # Extract unique service types (categories)
    ser = {i[1] for i in service}
    # Create a dictionary to store items grouped by category
    items_by_category = {category: [] for category in ser}
    # Populate the items_by_category dictionary
    for item in service:
        category = item[1]  # Assuming servicetype is at index 1
        items_by_category[category].append(item)
    return render_template("pricing.html", items_by_category=items_by_category, service=service)

@app.route("/index")
def index():
    return render_template("index.html")



@app.route('/addtocart', methods=["POST"])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []
    s_id = request.form["s_id"]
    quantity = int(request.form["quantity"])
    # Fetch laundry service information from the database
    cur.execute("SELECT * FROM services WHERE s_id = %s", (s_id,))
    service = cur.fetchone()
    if service:
        # Check if the service is already in the cart
        service_found = False
        for item in session['cart']:
            if item['s_id'] == s_id:
                # If the service is already in the cart, update the quantity
                item['quantity'] += quantity
                service_found = True
                break
        if not service_found:
            # If the service is not in the cart, add it
            session['cart'].append({
                's_id': s_id,
                'service_type': service[1],
                'itemtype': service[2],
                'price': service[3],
                'image': service[4],
                'quantity': quantity
            })
        # Reconstruct the entire session cart with updated item quantities
        session['cart'] = reconstruct_cart(session['cart'])
        # Insert sales data into the sales table
        # Redirect to view_cart route
        return redirect(url_for('view_cart'))
    else:
        return "Laundry service not found"
    
    
    
def reconstruct_cart(cart):
    reconstructed_cart = []
    seen_sids = set()  # Track seen service IDs
    for item in cart:
        if item['s_id'] not in seen_sids:
            # If service ID is not seen before, add the item directly
            reconstructed_cart.append(item)
            seen_sids.add(item['s_id'])
        else:
            # If service ID is seen before, update the quantity
            for existing_item in reconstructed_cart:
                if existing_item['s_id'] == item['s_id']:
                    existing_item['quantity'] += item['quantity']
                    break
    return reconstructed_cart


@app.route('/cart')
def view_cart():
    # Retrieve the cart data from the session
    cart = session.get('cart', [])
    # Calculate the total price
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    # Render the cart HTML template with the cart data and total price
    return render_template('cart.html', cart=cart, total_price=total_price)



@app.route("/inventory")
def services():
    service = fetch_data("services")
    return render_template("inventory.html", service= service)

@app.route("/dashboard")
def dashboard():
    return render_template("layout2.html")

@app.route("/additem", methods=["POST", "GET"])
def additem():
    if request.method == "POST":
        service = request.form["servicetype"]
        item= request.form["itemtype"]
        price= request.form["service_price"] 
        service= (service, item, price)
        insert_item(service)
    return redirect("/inventory")


@app.route('/addorders', methods=["POST", "GET"])
def addorder():
    if request.method == "POST":
        # Retrieve data from the form
          s_ids = request.form.getlist("s_id")
          quantities = request.form.getlist("quantity")
          delivery = request.form["delivery"]
          status = "Pending"
        # Iterate over each item and insert into the orders table
          for s_id, quantity in zip(s_ids, quantities):
            order = (s_id, status, quantity, delivery, 'now()')
            insert_orders(order)
    return redirect("/cart")


@app.route("/orders")
def sales():
       sales = fetch_data("orders")
       ser= fetch_data("services")
       return render_template('order.html', sales=sales, ser=ser)
   
@app.route("/graph")
def graph():
    line_chart = pygal.Line()
    line_chart.title = 'Revenue per Day'
    daily_sales = revenue_per_day()
    dates = []
    sales = []
    for i in daily_sales:
       dates.append(i[0])
       sales.append(i[1])
    line_chart.x_labels = dates
    line_chart.add('Sales', sales)
    line_chart=line_chart.render_data_uri()
    
    
    line_chart1 = pygal.Line()
    line_chart1.title = 'Revenue per Month'
    daily_sales = revenue_per_month()
    dates = []
    sales = []
    for i in daily_sales:
       dates.append(i[0])
       sales.append(i[1])
    line_chart1.x_labels = dates
    line_chart1.add('Sales', sales)
    line_chart1=line_chart1.render_data_uri()
    
    return render_template('graph.html', line_chart=line_chart, line_chart1=line_chart1)


    
if __name__ == "__main__":
    app.run(port=5000, debug=True)
    
    

