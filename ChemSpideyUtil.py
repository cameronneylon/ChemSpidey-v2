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
  parsed = chemparse(text)

  # Create local variables for the relevant returned information  
  parsedname = parsed.results.chemicalname
  quantity = float(parsed.results.amount)
  quantityunits = parsed.results.units
  role = parsed.results.role

  # Obtain chemspider ID and other information via ChemSpider simple search
  chemspiderID = simplesearch(parsedname)
  chemified['csid'] = chemspiderID
  chemified['imageurl'] = chemspiderID.imageurl()

  csurl = "http://www.chemspider.com/Chemical-Structure.%s.html" % chemspiderID
  chemified['csurl'] = csurl

  # Check if an amount has been returned, and if it a weight attempt to calculate moles
  quantitystring = ''
  if quantity != '' and units.find('g') != -1:

      if quantityunits == 'mg':
          nanomoles = 1000*quantity/chemspiderID.molweight()
          nanomoles = round(nanomoles, 2)
          chemified['moles'] = nanomoles
          chemified['molesunits'] = 'nmol'

      elif quantityunits == 'g':
          millimoles = 1000*quantity/chemspiderID.molweight()
          millimoles = round(millimoles, 2)
          chemified['moles'] = nanomoles
          chemified['molesunits'] = 'mmol'

      quantitystring = (' ' + quantity + ' ' + quantityunits + ', '
                        + chemified['moles'] + ' ' + chemified['molesunits'])

  # Set up the string to be returned back to the Wave robot
  texttoreturn = parsedname + ' (csid:' + chemspiderID + quantitystring + ')'
  chemified['annotations'].append({'text'       : texttoreturn,
                                   'annotation' : chemspidey.appspot.com/role,
                                   'value'      : role,
                                   'offset'     : 0,
                                   'length'     : len(texttoreturn)})

  chemified['annotations'].append({'text'       : chemspiderID,
                                   'annotation' : 'link/manual',
                                   'value'      : csurl,
                                   'offset'     : (len(parsedname) + 7),
                                   'length'     : len(chemspiderID)})
      

  return chemified

















