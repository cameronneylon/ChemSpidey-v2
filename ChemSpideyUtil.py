# ChemSpidey Utility Functions. 
#
# The aim here is to keep the ChemSpider interacting functionality separate from the
# Wave functionality found in the main scrip. This in theory will make re-use of the
# code easier later on.
#
# Cameron Neylon, 2010, 
#
# Licence info to go here...


import ChemSpiPy
import ChemParsing
import unittest
import urllib2
import logging

def chemify(text):
  """Accepts a text string and returns dictionary of information and annotations

  Text string is parsed and sent to chemspider to return chemspider ID, image url,
  and molecular weight information that makes it feasible to convert weight to
  moles and similar. Returns a dictionary that contains at a minimum the keys 
  'replacementtext', 'imageurl', and 'annotations' which is a tuple of dictionaries 
  containing the keys 'text', 'annotation', 'value', 'offset', 'length' for each
  of the annotations required

  test = {'replacementtext':'chemchemchem',
          'imageurl'       :'http://www.chemspider.com/ImagesHandler.ashx?id=236',
          'annotations'    :[{'text'      :'chem',
                              'annotation':'link/manual',
                              'value'     :'http://www.chemspider.com',
                              'offset'    :4,
                              'length'    :4},
                             {'text'      :'chem',
                              'annotation':'chemspidey.appspot.com/csid',
                              'value'     :'666',
                              'offset'    :8,
                              'length'    :4}
                             ]
          }
  """
  # Set up the dictionary to be returned
  chemified = {'replacementtext' : 'chemchem',
               'originaltext'    : text,
               'imageurl'        : 'none',
               'annotations'     : []
               }

  # Parse the text using chemparse which returns a dictionary
  parsed = ChemParsing.chemparse(text)

  # Create local variables for the relevant returned information  
  parsedname = parsed.get('name', None)
  quantity = parsed.get('amount', None)
  quantityunits = parsed.get('units', None)
  role = parsed.get('role', None)

  # Obtain chemspider ID and other information via ChemSpider simple search

  try:
      chemspiderID = ChemSpiPy.simplesearch(parsedname)
      logging.debug('Success connecting to ChemSpider')
  except IndexError, ie:
      errorstring = "Sorry I can't find %s in ChemSpider - try a different name?" % parsedname
      chemified['replacementtext'] = errorstring
      chemified['error'] = 'IndexError'
      logging.debug('Failed to find a match in simplesearch')
      return chemified

  chemified['csid'] = chemspiderID
  chemified['imageurl'] = chemspiderID.imageurl()

  csurl = "http://www.chemspider.com/Chemical-Structure.%s.html" % chemspiderID
  chemified['csurl'] = csurl

  # Check if an amount has been returned, and if it a weight attempt to calculate moles
  quantitystring = ''
  if quantity != '' and quantityunits.find('g') != -1:

      if quantityunits == 'mg':
          nanomoles = 1000*float(quantity)/chemspiderID.molweight()
          nanomoles = round(nanomoles, 2)
          chemified['moles'] = str(nanomoles)
          chemified['molesunits'] = 'nmol'

      elif quantityunits == 'g':
          millimoles = 1000*float(quantity)/chemspiderID.molweight()
          millimoles = round(millimoles, 2)
          chemified['moles'] = str(millimoles)
          chemified['molesunits'] = 'mmol'

      quantitystring = (' ' + quantity + ' ' + quantityunits + ', '
                        + chemified['moles'] + ' ' + chemified['molesunits'])

  # Set up the string to be returned back to the Wave robot
  texttoreturn = parsedname + ' (csid:' + chemspiderID + quantitystring + ')'
  chemified['replacementtext'] = texttoreturn

  # Set up the annotations to be returned
  chemified['annotations'].append({'text'       : texttoreturn,
                                   'annotation' : 'chemspidey.appspot.com/role',
                                   'value'      : role,
                                   'offset'     : 0,
                                   'length'     : len(texttoreturn)})

  chemified['annotations'].append({'text'       : chemspiderID,
                                   'annotation' : 'link/manual',
                                   'value'      : csurl,
                                   'offset'     : (len(parsedname) + 7),
                                   'length'     : len(chemspiderID)})
      

  return chemified


# some tests

if __name__ == '__main__':
    tests = [ "benzene", 
          "glucose 5g", 
          "acetone 5 ml", 
          "benzene solvent image", 
          "glucose 5g startingmaterial", 
          "2-5-dithioglucose 7.34mg product"]

    for t in tests:
        try:
            print t, chemify(t)
        except TypeError, te:
            print 'te'


