import httplib2
import requests
import json

from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash, make_response
from models import Base, User, Category, Item
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)


@app.route('/')
def showMain():
    categories = session.query(Category).all()
    return render_template('main.html', categories=categories)


@app.route('/catalog/<string:cat>/items')
def showItems(cat):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=cat).one()
    items = session.query(Item).filter_by(category_id=category.id)
    return render_template('main.html', categories=categories,
                           category=category, items=items)


@app.route('/catalog/<string:cat>/<string:item>')
def showItem(cat, item):
    category = session.query(Category).filter_by(name=cat).one()
    item = session.query(Item).filter_by(name=item, category=category).one()
    return render_template('item.html', category=category, item=item)


@app.route('/catalog/<string:cat>/add', methods=['GET', 'POST'])
def addItem(cat):
    category = session.query(Category).filter_by(name=cat).one()
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category=category)
        session.add(newItem)
        flash('%s created' % newItem.name)
        session.commit()
        return redirect(url_for('showItems', cat=category.name))
    else:
        return render_template('additem.html', category=category)


@app.route('/catalog/<string:cat>/<string:item>/delete',
           methods=['GET', 'POST'])
def deleteItem(cat, item):
    category = session.query(Category).filter_by(name=cat).one()
    item = session.query(Item).filter_by(name=item, category=category).one()
    if request.method == 'POST':
        session.delete(item)
        flash('%s deleted' % item.name)
        session.commit()
        return redirect(url_for('showItems', cat=category.name))
    else:
        return render_template('deleteitem.html', cat=category, item=item)


@app.route('/catalog/<string:cat>/<string:item>/edit',
           methods=['GET', 'POST'])
def editItem(cat, item):
    category = session.query(Category).filter_by(name=cat).one()
    item = session.query(Item).filter_by(name=item, category=category).one()
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        session.add(item)
        flash('%s updated' % item.name)
        session.commit()
        return redirect(url_for('showItems', cat=category.name))
    else:
        return render_template('edititem.html', cat=category, item=item)


# JSON of the whole catalog
@app.route('/catalog.json')
def catalogJSON():
    categories = session.query(Category).all()

    list = {'Categories' : []}
    for c in categories:
        category_list = {'id' : c.id, 'name' : c.name, 'items' : []}
        items = session.query(Item).filter_by(category_id=c.id)
        for i in items:
            category_list['items'].append(i.serialize)
        list['Categories'].append(category_list)

    #json = jsonify(Categories=[c.serialize for c in categories])
    response = make_response(json.dumps(list, indent=4))
    response.headers['Content-Type'] = 'application/json'
    return response


# launch web server
if __name__ == '__main__':
    app.secret_key = 'vhjaretlaclkjafdoluihaalwejkhalkjshvlzjlkhjwet'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
