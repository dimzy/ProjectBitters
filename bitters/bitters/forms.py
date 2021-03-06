from flask.ext.wtf import Form, BooleanField, StringField, validators, SelectField, TextAreaField, HiddenField
from wtforms import RadioField


#Intended for new placeables, should still get a selectable field though. 
#TODO: Make some new selectable fields for placeable type
class PlaceableForm(Form):
    placeableName = StringField('Name', [validators.Length(min=4, max=20)])
    new_description = TextAreaField('Description', [validators.Length(min=4, max=250)])
    del_entity = HiddenField('del_entity')
    #compatible character classes = undefined
    #compatible upgrade types = undefined

class placeableUpgradeTypeForm(Form):
    name = StringField('Type Name', [validators.Length(min=4, max=20)])
    description = TextAreaField('Describe the Intention of this type', [validators.Length(min=4, max=250)])
    del_entity = HiddenField('del_entity')
    
class placeableUpgradeForm(Form):
    name = StringField('Type Name', [validators.Length(min=4, max=20)])
    description = TextAreaField('Describe the Intention of this upgrade', [validators.Length(min=4, max=250)])
    #Upgrde type selectable
    upgrade_type = SelectField(u'Upgrade Type', coerce=unicode)
    del_entity = HiddenField('del_entity')
    #upgradeType = undefined

class CharacterClassForm(Form):
    className = StringField('Character Class Name',[validators.Length(min=4, max=20)])
    classDescription = TextAreaField('Describe the intention of this character class', [validators.Length(min=4, max=250)])
    #classPerks = RollableClass Perks


class EventActorForm(Form):
    actorName = StringField('Event Actor name', [validators.Length(min=4, max=20)])
    description = TextAreaField('Describe the intention of this actor', [validators.Length(min=4, max=250)])


class EventForm(Form):
    eventName = StringField('Event Name', [validators.Length(min=4, max=30)])