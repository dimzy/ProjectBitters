"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from bitters import app
import forms
import config
import pydocumentdb.document_client as document_client


@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/actors', methods=['GET', 'POST'])
def viewactors(): 
    default_actors = ['blacksmith', 'butler', 'area_boss', 'king', 'area_minion1', 'area_minion2', 'area_minion3', 'merchant']
    
    # Set up the clients to query for actors in these collections. 
    client = document_client.DocumentClient(config.DOCUMENTDB_HOST, {'masterKey': config.DOCUMENTDB_KEY})
    # Read databases and take first since id should not be duplicated.
    db = next((data for data in client.ReadDatabases() if data['id'] == config.DOCUMENTDB_DATABASE))

    # Read collections and take first since id should not be duplicated.
    coll = next((coll for coll in client.ReadCollections(db['_self']) if coll['id'] == config.DOCUMENTDB_COLLECTION))

    # Read documents and take first since id should not be duplicated.
    doc = next((doc for doc in client.ReadDocuments(coll['_self']) if doc['id'] == config.DOCUMENTDB_DOCUMENT))

def setup_collection(CollectionName):
    # Set up the clients to query for actors in these collections. 
    client = document_client.DocumentClient(config.DOCUMENTDB_HOST, {'masterKey': config.DOCUMENTDB_KEY})

    #Try accesesing the database
    try:
        db = next((data for data in client.ReadDatabases() if data['id'] == config.BITTERS_CONFIG))
    except: #DB doesn't exist
        createDB(client, config.BITTERS_CONFIG)
    
    # Get the collection from the database. 
    try:
        coll = next((coll for coll in client.ReadCollections(db['_self']) if coll['id'] == CollectionName))    
    except:
        createCollection(client, db, CollectionName)

    #Set the current collection back to the one we just created
    coll = next((coll for coll in client.ReadCollections(db['_self']) if coll['id'] == CollectionName))    
    
    return client, coll

def del_entity(client, collection, id):
    del_doc_iter = client.QueryDocuments(collection['_self'], 'select * from c where c.id = @id', { 'id' : id }).fetch_next_block()
    del_doc_iter = client.QueryDocuments(collection['_self'], {
                'query': 'select * from c where c.id = @id',
                'parameters': [{ 'name':'@id', 'value': id} ] } ).fetch_next_block()
    del_doc_id = del_doc_iter.__iter__().next()['_self']            
    ##TODO: Figure out what to do when the entity doesn't exist
    client.DeleteDocument(del_doc_id)

def get_collection_docs(client, collection_name):
    db = next((data for data in client.ReadDatabases() if data['id'] == config.BITTERS_CONFIG))
    coll = next((coll for coll in client.ReadCollections(db['_self']) if coll['id'] == collection_name))    
    return client.ReadDocuments(coll['_self']).__iter__()
    

@app.route('/placeable', methods=['GET', 'POST'])
def placeable():  
    from bitters.gameConfig.entity.placeable_entity import placeableType
    client, coll = setup_collection(config.PLACEABLES)    
    form = forms.PlaceableForm()
    
    if form.validate_on_submit():
        #form has been validated. We can try creating a new document now. 
        #TODO: Check for the ID/name to see if it exists first before submitting. Otherwise gonna throw error. 
        if form.del_entity.data == "Delete":
            del_entity(client, coll, form.placeableName.data)            
            form.del_entity.data = ""
        else:            
            placeable_object =  placeableType()
            placeable_object.name = form.placeableName.data
            placeable_object.id = form.placeableName.data
            placeable_object.description = form.new_description.data

            document = client.UpsertDocument(coll['_self'], placeable_object.__dict__)            

    #Get all documents and populate on the screen
    docs = client.ReadDocuments(coll['_self']).__iter__()    
    
    return render_template('placeable.html', 
                            title = 'Placeables', 
                            form = form, 
                            placeables = docs,
                            year=datetime.now().year)


@app.route('/placeable_upgrade_type', methods=['GET', 'POST'])
def placeable_upgrade_type():  
    from bitters.gameConfig.entity.placeable_entity import placeableUpgradeType
    client, coll = setup_collection(config.PLACEABLE_UPGRADE_TYPE)    
    form = forms.placeableUpgradeTypeForm()
    
    if form.validate_on_submit():
        #form has been validated. We can try creating a new document now. 
        #TODO: Check for the ID/name to see if it exists first before submitting. Otherwise gonna throw error. 
        if form.del_entity.data == "Delete":
            del_entity(client, coll, form.name.data)            
            form.del_entity.data = ""
        else:            
            obj =  placeableUpgradeType()
            obj.name = form.name.data
            obj.id = form.name.data
            obj.description = form.description.data

            document = client.UpsertDocument(coll['_self'], obj.__dict__)

    #Get all documents and populate on the screen
    docs = client.ReadDocuments(coll['_self']).__iter__()    
    
    return render_template('placeable_upgrade_type.html', 
                            title = 'Placeable Upgrade Types', 
                            entityName = 'placeable_upgrade_type',
                            form = form, 
                            existings = docs,
                            year=datetime.now().year)


@app.route('/placeable_upgrade', methods=['GET', 'POST'])
def placeable_upgrade():  
    from bitters.gameConfig.entity.placeable_entity import placeableUpgrade
    client, coll = setup_collection(config.PLACEABLE_UPGRADE)    
    form = forms.placeableUpgradeForm()
    
    #Get all documents and populate on the screen
    docs = client.ReadDocuments(coll['_self']).__iter__()
    
    #Get all upgrade types
    col_upgrade_docs = get_collection_docs(client, config.PLACEABLE_UPGRADE_TYPE)
    form.upgrade_type.choices = [(g['id'], g['name']) for g in col_upgrade_docs]
    
    if form.validate_on_submit():
        #form has been validated. We can try creating a new document now. 
        #TODO: Check for the ID/name to see if it exists first before submitting. Otherwise gonna throw error. 
        if form.del_entity.data == "Delete":
            del_entity(client, coll, form.name.data)            
            form.del_entity.data = ""
        else:            
            obj =  placeableUpgrade()
            obj.name = form.name.data
            obj.id = form.name.data
            obj.description = form.description.data
            obj.upgrade_type = form.upgrade_type.data

            document = client.UpsertDocument(coll['_self'], obj.__dict__)            

    
    return render_template('placeable_upgrade.html', 
                            title = 'Placeable Upgrades', 
                            entityName = 'placeable_upgrade',
                            form = form, 
                            existings = docs,
                            year=datetime.now().year)

def createDB(client, DB):    
    db = client.CreateDatabase({ 'id': DB})

def createCollection(client, db, collectionName):
    collection = client.CreateCollection(db['_self'],{ 'id': collectionName })