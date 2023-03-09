import os

import xlrd
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_restful import reqparse
from marshmallow import Schema, fields

app = Flask(__name__)
api = Api(app)
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db.init_app(app)
app.config['UPLOAD_FOLDER'] = '/files'


class InventoryList(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String)
    quantity = db.Column(db.Integer)
    item_value = db.Column(db.Integer)


class Healthcheck(Resource):
    def get(self):
        return 200, "OK"


class Inventory(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("item_name", type=str)
    parser.add_argument("quantity", type=int)
    parser.add_argument("item_value", type=int)

    class ItemSchema(Schema):
        id = fields.Integer()
        item_name = fields.String()
        quantity = fields.Integer()
        item_value = fields.Integer()

    def get(self):
        response = InventoryList.query.all()
        schema = self.ItemSchema(many=True)
        res = schema.dumps(response)
        return make_response(res)

    def post(self):
        data = self.parser.parse_args()
        if not data:
            data = {"ERROR": "No data"}
            return jsonify(data)
        else:
            found = InventoryList.query.filter_by(item_name=data["item_name"]).first()
            if not found:
                new_item = InventoryList()
                new_item.item_name = data['item_name']
                new_item.quantity = data['quantity']
                new_item.item_value = data['item_value']
                db.session.add(new_item)
                db.session.commit()
                return 200
            else:
                return {"ERROR": "Item already exists"}

    def put(self):
        self.parser.add_argument('id')
        data = self.parser.parse_args()
        if not data:
            data = {"ERROR": "No data"}
            return jsonify(data)
        else:
            to_del = request.json
            a = InventoryList.query.filter_by(id=to_del.get('id')).first()
            if a:
                if data.get('item_name'):
                    a.item_name = data.get('item_name')
                if data.get('quantity'):
                    a.quantity = data.get('quantity')
                if data.get('item_value'):
                    a.quantity = data.get('item_value')
                db.session.commit()
                return 200
            else:
                return {"code": 404, "msg": "not found"}

    def delete(self):
        to_del = request.json
        print(to_del)
        item_del = InventoryList.query.filter_by(id=to_del.get('id')).first()
        if item_del is not None:
            db.session.delete(item_del)
            db.session.commit()
        return 200


class InventoryBulk(Resource):
    def post(self):
        if not request.files:
            return 500, "nof a file"
        else:
            mem = request.files['file']
            xls_file = xlrd.open_workbook(file_contents=mem.read())
            sh = xls_file.sheet_by_index(0)
            for rx in range(1, sh.nrows):
                if InventoryList.query.filter_by(item_name=sh.cell(rx, 0).value).first() is None:
                    new_item = InventoryList()
                    new_item.item_name = sh.cell(rx, 0).value
                    new_item.quantity = sh.cell(rx, 1).value
                    new_item.item_value = sh.cell(rx, 2).value
                    print(new_item.item_name)
                    db.session.add(new_item)
                    db.session.commit()

            return {"code": 200, "msg": "Ok"}


api.add_resource(Healthcheck, '/')
api.add_resource(Inventory, "/inventory")
api.add_resource(InventoryBulk, "/inventory_upload")

with app.app_context():
    db.create_all()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)
