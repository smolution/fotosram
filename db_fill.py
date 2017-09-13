# -*- coding: utf-8 -*-
from AtelierApp import db, models

#models.Category.register('Interiér')
#models.Category.register('Exteriér')
#models.Category.register('Svatby')

#models.Subcategory.register('Děti')
#models.Subcategory.register('Matky')
#models.Subcategory.register('Báby')

cat = models.Category.query.first()
scat = models.Subcategory.query.first()
photo1 = models.Photo(filename = "photo1.jpg", filepath = "photos\\170713\\", category = cat, subcategory = scat)
db.session.add(photo1)
db.session.commit()

