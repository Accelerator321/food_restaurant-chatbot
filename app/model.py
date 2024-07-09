from app.app import db


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer)
    item = db.Column(db.String(), nullable = False)
    quantity = db.Column(db.Integer, default = 1, nullable = False )

    def __repr__(self):
        return f"<Order {self.order_id}: {self.item}>"


class Status(db.Model):

    order_id = db.Column(db.Integer, primary_key=True)
    
    status = db.Column(db.String(), default = "in tansit")

    def __repr__(self):
        return f"<Order {self.id}: {self.status}>"
    
class Address(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(), primary_key=True)

    def __repr__(self):
        return f"<Order {self.id}: {self.address}>"
    


