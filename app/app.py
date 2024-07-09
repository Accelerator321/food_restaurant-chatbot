from flask import Flask, request, jsonify

from flask_sqlalchemy import SQLAlchemy
import re
from  collections import defaultdict
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///food_restaurant"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

from app.model import Order, Status


sessions = defaultdict(lambda: defaultdict())
with app.app_context():
        db.create_all()

id = 0



@app.route("/" ,methods = ["GET", "POST"])
def main():
    

    try:
        payload = request.get_json()["queryResult"]
        intent = payload["intent"]["displayName"]
        action = actions_map[intent]
        return action(payload)
    except Exception as e:
        print("error: ",e)
        return jsonify({"fulfillmentText":"some error ocuured. Please try again"})

    

    


def get_session_id(payload):
     txt = payload["outputContexts"][0]["name"]
     pattern = r"sessions/([^/]+)/contexts"
     match = re.search(pattern, txt)

     if not match:
        return None
     session_id = match.group(1)
   
     return session_id


def add_to_order(payload):
    session_id = get_session_id(payload)
    if not session_id:
        return "sorry some error occured"
    
    if session_id not in sessions: sessions[session_id] = defaultdict(lambda :0)

    quantity = payload["parameters"]["number"]
    items = payload["parameters"]["foot-item"]
    
    if len(quantity) != len(items): return "sorry some error occured"

    for i in range(len(quantity)):
        sessions[session_id][items[i]] += quantity[i]

    return payload["fulfillmentText"]
    
def complete_order(payload):
    session_id = get_session_id(payload)
    print("order  complete req")
    if session_id not in sessions:
        return "some error occured"
    
    status = Status(status ="in transit")
    db.session.add(status)
    db.session.commit()
    order_id =status.order_id
    print("order_id", order_id)
    order_arr = []

    for item, quantity in sessions[session_id].items():
        order = Order(order_id =order_id,item=item, quantity = quantity)
        db.session.add(order)
        order_arr.append(f"{item}-{int(quantity)}")
    db.session.commit()
    del sessions[session_id]
    print(Order.query.all()) 

    res= clear_context_response(payload, context_name="ongoing-order")
    res["fulfillmentText"] = f"""Order Taken your order id is {order_id}\n and your order is-\n 
        {' , '.join(order_arr)}"""
    return jsonify(res)


def remove_order(payload):
     session_id = get_session_id(payload)
#      print(payload)
     items = payload["parameters"]["foot-item"]
     if len(items) ==0: return jsonify( {"fulfillmentText": f"Please specify the item to be removed"})
     
     if  len(sessions[session_id])==0:
        return jsonify( {"fulfillmentText": f"No ongoing order session. If this msg was in context of any previous order.\n i am sorry but once the order is finalised it cant be changed"})
#      print(payload)
         
     for item in items:
        if item in sessions[session_id]:
             del sessions[session_id][item]

     return jsonify( {"fulfillmentText": f"""{' , '.join(items)} removed from the order
                      \n you would like anything else?"""})

     


def track_order(payload):
     id = payload["parameters"]["number"]
     res = Status.query.filter_by(order_id=id).first()
     
     
     if not res:
        return jsonify( {"fulfillmentText": "No such order"})
     
     return jsonify( {"fulfillmentText": f"your order {int(id)} is {res.status}"})


def clear_context_response(payload, context_name):
    session_id = get_session_id(payload)
    return {
        'outputContexts': [
            {
                'name': f"projects/geko-chat-bot-eovp/agent/sessions/{session_id}/contexts/{context_name}",
                'lifespanCount': 0
            }
        ]
    }
      


actions_map = {
     "order.add": add_to_order,
     "order.complete": complete_order,
     "order.remove": remove_order,
     "order.track": track_order
}