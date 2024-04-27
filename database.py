import psycopg2

conn = psycopg2.connect("dbname=laundry user=postgres password=1234")
cur = conn.cursor()


def fetch_data(tbname):
  q = "SELECT * FROM " + tbname + ";"
  cur.execute(q)
  records = cur.fetchall()
  return records

def adduser(v):
  vs = str(v)
  q = "insert into users(full_name, email,contact, address,password, created_at)"\
    "values" + vs
  cur.execute(q)
  conn.commit()
  return q

def insert_item(v):
  vs = str(v)
  q = "insert into services(servicetype, itemtype, service_price,image)"\
    "values" + vs
  cur.execute(q)
  conn.commit()
  return q

def update_service(vs):
        s_id = vs[0]
        servicetype = vs[1]
        itemtype = vs[2]
        service_price = vs[3]
        image = vs[4]
        q = "UPDATE services SET servicetype = %s, itemtype = %s, service_price = %s,image = %s WHERE s_id = %s"
        cur.execute(q, (servicetype,itemtype,service_price,image,s_id))
        conn.commit()
        return q

def add_services(v):
  vs = str(v)
  q = "insert into services(servicetype, itemtype, service_price,image)"\
    "values" + vs
  cur.execute(q)
  conn.commit()
  return q


def delete_services(s_id):
  q_delete_product = "DELETE FROM services WHERE s_id = %s;"
  cur.execute(q_delete_product, (s_id,))
  conn.commit()
  
  
def pricing_item(v):
  vs = str(v)
  q = "insert into pricing(Item, Description, Price)"\
    "values" + vs
  cur.execute(q)
  conn.commit()
  return q



def insert_orders(order):
    # Define the SQL query with placeholders for values
    query = "INSERT INTO orders (s_id, status, quantity, delivery, order_date) VALUES (%s, %s, %s, %s, %s)"
    # Execute the query with the provided order data
    cur.execute(query, order)
    # Commit the transaction to persist the changes
    conn.commit()

def revenue_per_day():
    q = "SELECT * FROM sales_per_days"
    cur.execute(q)
    results = cur.fetchall()
    return results
  
def revenue_per_month():
    q = "SELECT * FROM sales_per_month"
    cur.execute(q)
    results = cur.fetchall()
    return results
  